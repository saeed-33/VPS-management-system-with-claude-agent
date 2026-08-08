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
    selected_specialists: tuple[SpecialistRoutingMatch, ...]
    unmatched_issue_indexes: tuple[int, ...]
    registry_size: int

    @property
    def selected_slugs(self) -> tuple[str, ...]:
        return tuple(
            item.specialist_slug
            for item in self.selected_specialists
        )


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

    text = value.casefold()
    text = _BOUNDARY_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def _contains_phrase(
    normalized_text: str,
    phrase: str,
) -> bool:
    needle = _normalize_text(phrase)

    if not needle:
        return False

    padded_text = f" {normalized_text} "
    padded_needle = f" {needle} "

    return padded_needle in padded_text


def _value(
    obj: Any,
    key: str,
    default: Any = None,
) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _issue_signals(
    analysis: Any,
) -> tuple[_IssueSignal, ...]:
    result: list[_IssueSignal] = []

    for index, issue in enumerate(
        _value(analysis, "issues", []) or []
    ):
        severity = str(
            _value(issue, "severity", "")
        ).casefold()

        parts = [
            _value(issue, "title", ""),
            _value(issue, "description", ""),
            _value(issue, "evidence", ""),
        ]

        text = _normalize_text(
            " ".join(
                str(part)
                for part in parts
                if part
            )
        )

        result.append(
            _IssueSignal(
                index=index,
                severity=severity,
                text=text,
            )
        )

    return tuple(result)


def _report_signal_text(
    report: Any,
) -> str:
    parts: list[str] = []

    status = _value(
        report,
        "status",
        None,
    )

    if status:
        parts.append(
            str(status).replace(
                "_",
                " ",
            )
        )

    error_message = _value(
        report,
        "error_message",
        None,
    )

    if error_message:
        parts.append(
            str(error_message)
        )

    for execution in (
        _value(report, "executions", []) or []
    ):
        if bool(
            _value(execution, "success", True)
        ):
            continue

        for key in (
            "command_name",
            "stderr",
            "error_message",
        ):
            value = _value(
                execution,
                key,
                None,
            )

            if value:
                parts.append(
                    str(value)
                )

    return _normalize_text(
        " ".join(parts)
    )


def _report_failed(
    report: Any,
) -> bool:
    if not bool(
        _value(
            report,
            "connection_successful",
            True,
        )
    ):
        return True

    status = str(
        _value(report, "status", "")
    ).casefold()

    if status in {
        "failed",
        "connection_failed",
        "partial_failure",
    }:
        return True

    if int(
        _value(
            report,
            "commands_failed",
            0,
        )
        or 0
    ) > 0:
        return True

    return False


def _health_status(
    analysis: Any,
) -> str:
    value = _value(
        analysis,
        "health_status",
        "",
    )

    return str(
        value or ""
    ).casefold()


def _actionable_issues(
    issues: Iterable[_IssueSignal],
) -> tuple[_IssueSignal, ...]:
    return tuple(
        issue
        for issue in issues
        if issue.severity
        in {
            "warning",
            "critical",
        }
    )


class InvestigationRouter:
    """
    Conservative deterministic Phase 4.5 router.

    It discovers candidates from user-defined Specialist domains and
    trigger_hints. It does not contain hard-coded CPU/Memory/etc. rules.
    """

    def __init__(
        self,
        *,
        specialist_registry: SpecialistRegistry,
        max_specialists: int = 4,
        trigger_weight: int = 5,
        domain_weight: int = 2,
    ) -> None:
        if max_specialists < 1:
            raise ValueError(
                "max_specialists must be >= 1."
            )

        if trigger_weight < 1:
            raise ValueError(
                "trigger_weight must be >= 1."
            )

        if domain_weight < 1:
            raise ValueError(
                "domain_weight must be >= 1."
            )

        self._specialist_registry = (
            specialist_registry
        )
        self._max_specialists = (
            max_specialists
        )
        self._trigger_weight = (
            trigger_weight
        )
        self._domain_weight = (
            domain_weight
        )

    def route(
        self,
        *,
        report: Any,
        analysis: Any,
        snapshot: SpecialistRegistrySnapshot
        | None = None,
    ) -> InvestigationRoutingDecision:
        if snapshot is None:
            snapshot = (
                self._specialist_registry
                .snapshot()
            )

        issues = _issue_signals(
            analysis
        )
        actionable = _actionable_issues(
            issues
        )

        report_failed = _report_failed(
            report
        )
        health = _health_status(
            analysis
        )

        reasons: list[
            RoutingReason
        ] = []

        if actionable:
            reasons.append(
                RoutingReason.ANALYSIS_ISSUES
            )

        if health in {
            "warning",
            "critical",
        }:
            reasons.append(
                RoutingReason.ANALYSIS_HEALTH
            )

        if report_failed:
            reasons.append(
                RoutingReason.REPORT_FAILURE
            )

        should_investigate = bool(
            actionable
            or report_failed
            or health
            in {
                "warning",
                "critical",
            }
        )

        if not should_investigate:
            if (
                health == "healthy"
                and not issues
                and not report_failed
            ):
                reasons.append(
                    RoutingReason.HEALTHY_NO_ISSUES
                )
            else:
                reasons.append(
                    RoutingReason.NO_ACTIONABLE_SIGNAL
                )

            return (
                InvestigationRoutingDecision(
                    should_investigate=False,
                    reasons=tuple(reasons),
                    detected_domains=(),
                    selected_specialists=(),
                    unmatched_issue_indexes=(),
                    registry_size=len(
                        snapshot.definitions
                    ),
                )
            )

        report_text = _report_signal_text(
            report
        )

        summary_text = _normalize_text(
            str(
                _value(
                    analysis,
                    "summary",
                    "",
                )
                or ""
            )
        )

        evidence_text = _normalize_text(
            " ".join(
                [
                    *(
                        issue.text
                        for issue
                        in actionable
                    ),
                    summary_text,
                    report_text,
                ]
            )
        )

        candidates = tuple(
            self._score_specialist(
                specialist=specialist,
                evidence_text=evidence_text,
                issues=actionable,
                report_text=report_text,
            )
            for specialist
            in snapshot.definitions
        )

        candidates = tuple(
            item
            for item in candidates
            if item.score > 0
        )

        trigger_candidates = tuple(
            item
            for item in candidates
            if item.matched_trigger_hints
        )

        # Conservative rule:
        # if explicit trigger hints matched anywhere, do not add weaker
        # domain-only candidates to the same first routing decision.
        pool = (
            trigger_candidates
            if trigger_candidates
            else candidates
        )

        ordered = tuple(
            sorted(
                pool,
                key=lambda item: (
                    -item.score,
                    item.specialist.priority,
                    item.specialist.name.casefold(),
                    item.specialist.slug,
                    item.specialist.id,
                ),
            )
        )

        selected = ordered[
            : self._max_specialists
        ]

        selected_matches = tuple(
            SpecialistRoutingMatch(
                specialist_id=(
                    item.specialist.id
                ),
                specialist_slug=(
                    item.specialist.slug
                ),
                specialist_name=(
                    item.specialist.name
                ),
                score=item.score,
                matched_domains=(
                    item.matched_domains
                ),
                matched_trigger_hints=(
                    item.matched_trigger_hints
                ),
                matched_issue_indexes=(
                    item.matched_issue_indexes
                ),
                priority=(
                    item.specialist.priority
                ),
            )
            for item in selected
        )

        detected_domains = tuple(
            sorted(
                {
                    domain
                    for item in selected
                    for domain
                    in item.matched_domains
                }
            )
        )

        covered_issue_indexes = {
            index
            for item in selected
            for index
            in item.matched_issue_indexes
        }

        unmatched_issue_indexes = tuple(
            issue.index
            for issue in actionable
            if issue.index
            not in covered_issue_indexes
        )

        if not selected_matches:
            reasons.append(
                RoutingReason.NO_SUITABLE_SPECIALIST
            )

        return InvestigationRoutingDecision(
            should_investigate=True,
            reasons=tuple(reasons),
            detected_domains=detected_domains,
            selected_specialists=(
                selected_matches
            ),
            unmatched_issue_indexes=(
                unmatched_issue_indexes
            ),
            registry_size=len(
                snapshot.definitions
            ),
        )

    def _score_specialist(
        self,
        *,
        specialist: SpecialistRuntimeDefinition,
        evidence_text: str,
        issues: tuple[_IssueSignal, ...],
        report_text: str,
    ) -> _Candidate:
        matched_domains = tuple(
            domain
            for domain in specialist.domains
            if _contains_phrase(
                evidence_text,
                domain,
            )
        )

        matched_trigger_hints = tuple(
            hint
            for hint
            in specialist.trigger_hints
            if _contains_phrase(
                evidence_text,
                hint,
            )
        )

        matched_issue_indexes: list[
            int
        ] = []

        for issue in issues:
            issue_match = any(
                _contains_phrase(
                    issue.text,
                    value,
                )
                for value in (
                    *specialist.domains,
                    *specialist.trigger_hints,
                )
            )

            if issue_match:
                matched_issue_indexes.append(
                    issue.index
                )

        # A report-level failure may match a specialist without any
        # analysis issue index (for example "connection failed").
        _ = report_text

        score = (
            len(matched_trigger_hints)
            * self._trigger_weight
            + len(matched_domains)
            * self._domain_weight
        )

        return _Candidate(
            specialist=specialist,
            score=score,
            matched_domains=(
                matched_domains
            ),
            matched_trigger_hints=(
                matched_trigger_hints
            ),
            matched_issue_indexes=tuple(
                matched_issue_indexes
            ),
        )
