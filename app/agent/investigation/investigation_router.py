from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Any, Iterable

from app.agent.investigation.specialist_registry import (
    SpecialistRegistry,
    SpecialistRegistrySnapshot,
    SpecialistRuntimeDefinition,
)


class RoutingReason(StrEnum):
    ANALYSIS_ISSUES = "analysis_issues"
    ANALYSIS_HEALTH = "analysis_health"
    REPORT_FAILURE = "report_failure"
    HEALTHY_NO_ISSUES = "healthy_no_issues"
    NO_ACTIONABLE_SIGNAL = "no_actionable_signal"
    NO_SUITABLE_SPECIALIST = "no_suitable_specialist"


@dataclass(slots=True, frozen=True)
class SpecialistRoutingMatch:
    specialist_id: int
    specialist_slug: str
    specialist_name: str
    score: int
    matched_domains: tuple[str, ...]
    matched_trigger_hints: tuple[str, ...]
    matched_issue_indexes: tuple[int, ...]
    priority: int


@dataclass(slots=True, frozen=True)
class InvestigationRoutingDecision:
    should_investigate: bool
    reasons: tuple[RoutingReason, ...]
    detected_domains: tuple[str, ...]
    candidate_specialists: tuple[SpecialistRoutingMatch, ...]
    selected_specialists: tuple[SpecialistRoutingMatch, ...]
    unmatched_issue_indexes: tuple[int, ...]
    registry_size: int
    candidate_limit: int
    selection_limit: int

    @property
    def candidate_slugs(self) -> tuple[str, ...]:
        return tuple(x.specialist_slug for x in self.candidate_specialists)

    @property
    def selected_slugs(self) -> tuple[str, ...]:
        return tuple(x.specialist_slug for x in self.selected_specialists)


@dataclass(slots=True, frozen=True)
class _IssueSignal:
    index: int
    severity: str
    text: str


@dataclass(slots=True, frozen=True)
class _Candidate:
    specialist: SpecialistRuntimeDefinition
    score: int
    matched_domains: tuple[str, ...]
    matched_trigger_hints: tuple[str, ...]
    matched_issue_indexes: tuple[int, ...]


_SPACE_RE = re.compile(r"\s+")
_BOUNDARY_RE = re.compile(r"[^\w]+", re.UNICODE)


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = _BOUNDARY_RE.sub(" ", value.casefold())
    return _SPACE_RE.sub(" ", text).strip()


def _contains_phrase(normalized_text: str, phrase: str) -> bool:
    needle = _normalize_text(phrase)
    return bool(needle) and f" {needle} " in f" {normalized_text} "


def _value(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _issue_signals(analysis: Any) -> tuple[_IssueSignal, ...]:
    result = []
    for index, issue in enumerate(_value(analysis, "issues", []) or []):
        severity = str(_value(issue, "severity", "")).casefold()
        parts = [
            _value(issue, "title", ""),
            _value(issue, "description", ""),
            _value(issue, "evidence", ""),
        ]
        text = _normalize_text(" ".join(str(p) for p in parts if p))
        result.append(_IssueSignal(index=index, severity=severity, text=text))
    return tuple(result)


def _report_signal_text(report: Any) -> str:
    parts: list[str] = []
    status = _value(report, "status", None)
    if status:
        parts.append(str(status).replace("_", " "))
    error_message = _value(report, "error_message", None)
    if error_message:
        parts.append(str(error_message))

    for execution in (_value(report, "executions", []) or []):
        if bool(_value(execution, "success", True)):
            continue
        for key in ("command_name", "stderr", "error_message"):
            value = _value(execution, key, None)
            if value:
                parts.append(str(value))
    return _normalize_text(" ".join(parts))


def _report_failed(report: Any) -> bool:
    if not bool(_value(report, "connection_successful", True)):
        return True
    status = str(_value(report, "status", "")).casefold()
    if status in {"failed", "connection_failed", "partial_failure"}:
        return True
    return int(_value(report, "commands_failed", 0) or 0) > 0


def _health_status(analysis: Any) -> str:
    return str(_value(analysis, "health_status", "") or "").casefold()


def _actionable_issues(issues: Iterable[_IssueSignal]) -> tuple[_IssueSignal, ...]:
    return tuple(x for x in issues if x.severity in {"warning", "critical"})


class InvestigationRouter:
    """
    Deterministic candidate retrieval + baseline selection.

    candidate_specialists is a higher-recall shortlist for a future
    intelligent selector. selected_specialists is the smaller baseline
    selection bounded by the investigation execution budget.
    """

    def __init__(
        self,
        *,
        specialist_registry: SpecialistRegistry,
        candidate_limit: int = 12,
        selection_limit: int = 4,
        trigger_weight: int = 5,
        domain_weight: int = 2,
    ) -> None:
        if candidate_limit < 1:
            raise ValueError("candidate_limit must be >= 1.")
        if selection_limit < 1:
            raise ValueError("selection_limit must be >= 1.")
        if candidate_limit < selection_limit:
            raise ValueError("candidate_limit must be >= selection_limit.")
        if trigger_weight < 1:
            raise ValueError("trigger_weight must be >= 1.")
        if domain_weight < 1:
            raise ValueError("domain_weight must be >= 1.")

        self._specialist_registry = specialist_registry
        self._candidate_limit = candidate_limit
        self._selection_limit = selection_limit
        self._trigger_weight = trigger_weight
        self._domain_weight = domain_weight

    def route(
        self,
        *,
        report: Any,
        analysis: Any,
        snapshot: SpecialistRegistrySnapshot | None = None,
    ) -> InvestigationRoutingDecision:
        snapshot = snapshot or self._specialist_registry.snapshot()

        issues = _issue_signals(analysis)
        actionable = _actionable_issues(issues)
        report_failed = _report_failed(report)
        health = _health_status(analysis)

        reasons: list[RoutingReason] = []
        if actionable:
            reasons.append(RoutingReason.ANALYSIS_ISSUES)
        if health in {"warning", "critical"}:
            reasons.append(RoutingReason.ANALYSIS_HEALTH)
        if report_failed:
            reasons.append(RoutingReason.REPORT_FAILURE)

        should_investigate = bool(
            actionable or report_failed or health in {"warning", "critical"}
        )

        if not should_investigate:
            reasons.append(
                RoutingReason.HEALTHY_NO_ISSUES
                if health == "healthy" and not issues and not report_failed
                else RoutingReason.NO_ACTIONABLE_SIGNAL
            )
            return InvestigationRoutingDecision(
                should_investigate=False,
                reasons=tuple(reasons),
                detected_domains=(),
                candidate_specialists=(),
                selected_specialists=(),
                unmatched_issue_indexes=(),
                registry_size=len(snapshot.definitions),
                candidate_limit=self._candidate_limit,
                selection_limit=self._selection_limit,
            )

        report_text = _report_signal_text(report)
        summary_text = _normalize_text(
            str(_value(analysis, "summary", "") or "")
        )
        evidence_text = _normalize_text(
            " ".join([
                *(issue.text for issue in actionable),
                summary_text,
                report_text,
            ])
        )

        scored = tuple(
            self._score_specialist(
                specialist=specialist,
                evidence_text=evidence_text,
                issues=actionable,
            )
            for specialist in snapshot.definitions
        )
        scored = tuple(x for x in scored if x.score > 0)

        trigger_candidates = tuple(
            x for x in scored if x.matched_trigger_hints
        )
        pool = trigger_candidates if trigger_candidates else scored

        ordered = tuple(sorted(
            pool,
            key=lambda x: (
                -x.score,
                x.specialist.priority,
                x.specialist.name.casefold(),
                x.specialist.slug,
                x.specialist.id,
            ),
        ))

        candidate_items = ordered[: self._candidate_limit]
        selected_items = candidate_items[: self._selection_limit]

        candidate_matches = tuple(self._to_match(x) for x in candidate_items)
        selected_matches = tuple(self._to_match(x) for x in selected_items)

        detected_domains = tuple(sorted({
            domain
            for item in candidate_items
            for domain in item.matched_domains
        }))

        covered = {
            index
            for item in selected_items
            for index in item.matched_issue_indexes
        }
        unmatched = tuple(
            issue.index
            for issue in actionable
            if issue.index not in covered
        )

        if not candidate_matches:
            reasons.append(RoutingReason.NO_SUITABLE_SPECIALIST)

        return InvestigationRoutingDecision(
            should_investigate=True,
            reasons=tuple(reasons),
            detected_domains=detected_domains,
            candidate_specialists=candidate_matches,
            selected_specialists=selected_matches,
            unmatched_issue_indexes=unmatched,
            registry_size=len(snapshot.definitions),
            candidate_limit=self._candidate_limit,
            selection_limit=self._selection_limit,
        )

    @staticmethod
    def _to_match(item: _Candidate) -> SpecialistRoutingMatch:
        return SpecialistRoutingMatch(
            specialist_id=item.specialist.id,
            specialist_slug=item.specialist.slug,
            specialist_name=item.specialist.name,
            score=item.score,
            matched_domains=item.matched_domains,
            matched_trigger_hints=item.matched_trigger_hints,
            matched_issue_indexes=item.matched_issue_indexes,
            priority=item.specialist.priority,
        )

    def _score_specialist(
        self,
        *,
        specialist: SpecialistRuntimeDefinition,
        evidence_text: str,
        issues: tuple[_IssueSignal, ...],
    ) -> _Candidate:
        matched_domains = tuple(
            d for d in specialist.domains
            if _contains_phrase(evidence_text, d)
        )
        matched_triggers = tuple(
            h for h in specialist.trigger_hints
            if _contains_phrase(evidence_text, h)
        )

        matched_issue_indexes = tuple(
            issue.index
            for issue in issues
            if any(
                _contains_phrase(issue.text, value)
                for value in (
                    *specialist.domains,
                    *specialist.trigger_hints,
                )
            )
        )

        score = (
            len(matched_triggers) * self._trigger_weight
            + len(matched_domains) * self._domain_weight
        )

        return _Candidate(
            specialist=specialist,
            score=score,
            matched_domains=matched_domains,
            matched_trigger_hints=matched_triggers,
            matched_issue_indexes=matched_issue_indexes,
        )
