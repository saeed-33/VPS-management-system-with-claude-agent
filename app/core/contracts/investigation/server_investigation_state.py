"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .evidence_reference import EvidenceReference

from .investigation_budget import InvestigationBudget

from .investigation_finding import InvestigationFinding

from .investigation_status import InvestigationStatus

from .knowledge_source_reference import KnowledgeSourceReference

from .specialist_result import SpecialistResult

from .specialist_task import SpecialistTask

@dataclass(slots=True)
class ServerInvestigationState:
    """
    الحالة الكاملة لتحقيق مرتبط بسيرفر وتقرير وتحليل.

    تجمع الحالة الأدلة ومصادر المعرفة ومهام المتخصصين ونتائجهم، وتفرض حدود
    التحقيق وروابط الهوية قبل السماح بإضافة أي عنصر جديد.
    """
    investigation_id: str
    server_id: int
    report_id: int
    analysis_id: int | None
    status: InvestigationStatus = (
        InvestigationStatus.CREATED
    )
    round_number: int = 1
    budget: InvestigationBudget = field(
        default_factory=InvestigationBudget
    )
    detected_domains: list[str] = field(
        default_factory=list
    )
    evidence: list[EvidenceReference] = field(
        default_factory=list
    )
    knowledge_sources: list[
        KnowledgeSourceReference
    ] = field(default_factory=list)
    tasks: list[SpecialistTask] = field(
        default_factory=list
    )
    results: list[SpecialistResult] = field(
        default_factory=list
    )
    final_findings: list[
        InvestigationFinding
    ] = field(default_factory=list)
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من هوية التحقيق وروابط السيرفر والتقرير والتحليل ورقم الجولة."""
        if not self.investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if self.server_id < 1:
            raise ValueError(
                "server_id must be >= 1."
            )
        if self.report_id < 1:
            raise ValueError(
                "report_id must be >= 1."
            )
        if self.analysis_id is not None:
            if self.analysis_id < 1:
                raise ValueError(
                    "analysis_id must be >= 1 when provided."
                )
        if self.round_number < 1:
            raise ValueError(
                "round_number must be >= 1."
            )

    def add_evidence(
        self,
        evidence: EvidenceReference,
    ) -> None:
        """
        يضيف دليلًا جديدًا إلى التحقيق بعد منع تكرار معرفه.

        يضمن ذلك أن كل دليل يمكن ربطه مرة واحدة بالاستنتاجات اللاحقة.
        """
        if any(
            item.evidence_id == evidence.evidence_id
            for item in self.evidence
        ):
            raise ValueError(
                "Duplicate evidence_id: "
                f"{evidence.evidence_id}"
            )

        self.evidence.append(evidence)

    def add_knowledge_source(
        self,
        source: KnowledgeSourceReference,
    ) -> None:
        """
        يربط مصدر معرفة بالتحقيق بعد منع تكرار معرف المصدر.
        """
        if any(
            item.source_id == source.source_id
            for item in self.knowledge_sources
        ):
            raise ValueError(
                "Duplicate knowledge source_id: "
                f"{source.source_id}"
            )

        self.knowledge_sources.append(source)

    def add_task(
        self,
        task: SpecialistTask,
    ) -> None:
        """
        يسجل مهمة متخصص بعد التحقق من هويتها وميزانية التحقيق.

        يرفض العقد مهمة تخص سيرفرًا أو تقريرًا آخر، أو تتجاوز عدد الجولات أو
        عدد المتخصصين المسموحين.
        """
        if task.investigation_id != self.investigation_id:
            raise ValueError(
                "Task belongs to a different investigation."
            )

        if task.server_id != self.server_id:
            raise ValueError(
                "Task belongs to a different server."
            )

        if task.report_id != self.report_id:
            raise ValueError(
                "Task belongs to a different report."
            )

        if task.round_number > self.budget.max_rounds:
            raise ValueError(
                "Task exceeds investigation round budget."
            )

        if any(
            item.task_id == task.task_id
            for item in self.tasks
        ):
            raise ValueError(
                f"Duplicate task_id: {task.task_id}"
            )

        specialist_ids = {
            item.specialist_id
            for item in self.tasks
        }

        if (
            task.specialist_id not in specialist_ids
            and len(specialist_ids)
            >= self.budget.max_specialists
        ):
            raise ValueError(
                "Investigation specialist budget exceeded."
            )

        self.tasks.append(task)

    def add_result(
        self,
        result: SpecialistResult,
    ) -> None:
        """
        يثبت نتيجة متخصص لمهمة معروفة مرة واحدة فقط.

        يطابق العقد معرف المهمة والمتخصص قبل إلحاق النتيجة حتى لا يدخل تشخيص
        مبني على نتيجة تخص تحقيقًا أو متخصصًا آخر.
        """
        matching_task = next(
            (
                task
                for task in self.tasks
                if task.task_id == result.task_id
            ),
            None,
        )

        if matching_task is None:
            raise ValueError(
                "Result does not reference a known task."
            )

        if (
            matching_task.specialist_id
            != result.specialist_id
        ):
            raise ValueError(
                "Result specialist does not match task specialist."
            )

        if any(
            item.task_id == result.task_id
            for item in self.results
        ):
            raise ValueError(
                "A result already exists for task_id: "
                f"{result.task_id}"
            )

        self.results.append(result)
