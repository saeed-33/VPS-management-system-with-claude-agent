"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.structured_compatibility، app.core.config، app.infrastructure.database.models.report_analysis، app.infrastructure.database.models.report_analysis_source، app.infrastructure.database.models.report_retrieval_document، app.infrastructure.database.session.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
project_root_value = str(PROJECT_ROOT)
if project_root_value not in sys.path:
    sys.path.insert(0, project_root_value)

from sqlalchemy import select, text

from app.capabilities.analysis.retrieval.structured_compatibility import (
    StructuredCompatibilityChecker,
)
from app.core.config import settings
from app.infrastructure.database.models.report_analysis import (
    ReportAnalysisModel,
)
from app.infrastructure.database.models.report_analysis_source import (
    ReportAnalysisSourceModel,
)
from app.infrastructure.database.models.report_retrieval_document import (
    ReportRetrievalDocumentModel,
)
from app.infrastructure.database.session import SessionLocal


@dataclass(slots=True)
class EvaluationSummary:
    """
    يمثل EvaluationSummary جزءًا من طبقة Developer tooling.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه CLI أو المطور مباشرة. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    completed_analyses: int
    reused: int
    assisted: int
    full: int
    llm_call_rate: float
    exact_reuse_integrity: float | None
    potential_exact_reuse_miss_rate: float | None

    assisted_analyses_with_historical_sources: int
    historical_sources_evaluated: int
    current_report_rows_ignored: int

    current_threshold_violations: int
    legacy_threshold_storage_rows: int
    current_future_leakage_violations: int
    current_scope_violations: int
    current_compatibility_violations: int
    legacy_compatibility_conflicts: int

    assisted_health_agreement_rate: float | None
    hnsw_index_present: bool
    avg_duration_ms_by_source: dict[str, float]
    retrieval_strategy_counts: dict[str, int]

    invariant_status: str


def ratio(numerator: int, denominator: int) -> float | None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى ratio؛ المدخلات المهمة: numerator، denominator.
    تعيد float | None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if denominator <= 0:
        return None
    return numerator / denominator


def fetch_hnsw_index_present(session) -> bool:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى fetch_hnsw_index_present؛ المدخلات المهمة: session.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    value = session.scalar(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE tablename = 'report_retrieval_documents'
                  AND indexname = 'ix_retrieval_embedding_hnsw_cosine'
            )
            """
        )
    )
    return bool(value)


def build_document_map(
    session,
) -> dict[int, ReportRetrievalDocumentModel]:
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى build_document_map؛ المدخلات المهمة: session.
    تعيد dict[int, ReportRetrievalDocumentModel] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    documents = session.scalars(
        select(ReportRetrievalDocumentModel)
    ).all()
    return {
        document.analysis_id: document
        for document in documents
    }


def source_scope_matches(
    current: ReportRetrievalDocumentModel | None,
    historical: ReportRetrievalDocumentModel | None,
) -> bool:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى source_scope_matches؛ المدخلات المهمة: current، historical.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if current is None or historical is None:
        return False

    return (
        current.server_id == historical.server_id
        and current.monitoring_profile_id
        == historical.monitoring_profile_id
        and current.command_set_hash
        == historical.command_set_hash
    )


def is_historical_source(
    source: ReportAnalysisSourceModel,
) -> bool:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى is_historical_source؛ المدخلات المهمة: source.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return (
        source.source_analysis_id is not None
        and source.source_report_id is not None
    )


def metadata_float(
    metadata: dict[str, Any],
    key: str,
) -> float | None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى metadata_float؛ المدخلات المهمة: metadata، key.
    تعيد float | None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    value = metadata.get(key)

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    return None


def effective_vector_score(
    source: ReportAnalysisSourceModel,
) -> tuple[float | None, str]:
    """
    Return semantic vector similarity and its provenance.

    Current rows store vector similarity in similarity_score and
    also include source_metadata.vector_score.

    During the historical 3.4 window, similarity_score stored the
    RRF ranking score (~0.016) while source_metadata.vector_score
    contained the real semantic similarity (~0.99). Prefer the
    explicit vector_score metadata whenever available.
    """
    metadata = source.source_metadata or {}
    vector_score = metadata_float(
        metadata,
        "vector_score",
    )

    if vector_score is not None:
        return vector_score, "metadata.vector_score"

    if source.similarity_score is not None:
        return (
            float(source.similarity_score),
            "similarity_score",
        )

    return None, "missing"


def has_current_hybrid_metadata_contract(
    source: ReportAnalysisSourceModel,
) -> bool:
    """
    Current post-3.4.1 source rows persist rrf_score separately
    from semantic similarity. Older rows do not.

    This is a data-contract marker, not a deployment timestamp.
    It lets the evaluator separate legacy records from rows that
    demonstrably follow the current persistence contract.
    """
    metadata = source.source_metadata or {}

    return (
        "rrf_score" in metadata
        and "vector_score" in metadata
    )


def is_legacy_rrf_storage(
    source: ReportAnalysisSourceModel,
    effective_score: float | None,
) -> bool:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى is_legacy_rrf_storage؛ المدخلات المهمة: source، effective_score.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if (
        source.similarity_score is None
        or effective_score is None
    ):
        return False

    stored = float(source.similarity_score)

    return (
        stored < settings.rag_minimum_similarity
        and effective_score
        >= settings.rag_minimum_similarity
        and metadata_float(
            source.source_metadata or {},
            "vector_score",
        )
        is not None
    )


def evaluate_database(
    limit: int | None = None,
) -> dict[str, Any]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى evaluate_database؛ المدخلات المهمة: limit.
    تعيد dict[str, Any] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    checker = StructuredCompatibilityChecker()

    with SessionLocal() as session:
        statement = (
            select(ReportAnalysisModel)
            .where(
                ReportAnalysisModel.status
                == "completed"
            )
            .order_by(
                ReportAnalysisModel.created_at.asc()
            )
        )

        if limit is not None:
            statement = statement.limit(limit)

        analyses = list(
            session.scalars(statement).all()
        )
        analysis_by_id = {
            item.id: item
            for item in analyses
        }

        document_by_analysis = (
            build_document_map(session)
        )

        sources = list(
            session.scalars(
                select(
                    ReportAnalysisSourceModel
                ).where(
                    ReportAnalysisSourceModel
                    .used_in_prompt
                    .is_(True)
                )
            ).all()
        )

        source_rows_by_analysis: dict[
            int,
            list[ReportAnalysisSourceModel],
        ] = {}

        for source in sources:
            source_rows_by_analysis.setdefault(
                source.analysis_id,
                [],
            ).append(source)

        counts = Counter(
            item.analysis_source
            for item in analyses
        )
        strategy_counts = Counter(
            item.retrieval_strategy or "none"
            for item in analyses
        )

        llm_calls = sum(
            bool(item.llm_called)
            for item in analyses
        )

        reused_rows = [
            item
            for item in analyses
            if item.analysis_source == "reused"
        ]

        valid_reuse = 0

        for item in reused_rows:
            source = analysis_by_id.get(
                item.reused_from_analysis_id
            )

            if source is None:
                source = session.get(
                    ReportAnalysisModel,
                    item.reused_from_analysis_id,
                )

            if source is None:
                continue

            if (
                item.report_fingerprint
                and item.report_fingerprint
                == source.report_fingerprint
                and item.server_id == source.server_id
                and source.created_at <= item.created_at
                and item.llm_called is False
            ):
                valid_reuse += 1

        potential_reuse_opportunities = 0
        potential_reuse_misses = 0
        seen_fingerprints: set[
            tuple[int, str]
        ] = set()

        for item in analyses:
            if not item.report_fingerprint:
                continue

            key = (
                item.server_id,
                item.report_fingerprint,
            )

            if key in seen_fingerprints:
                potential_reuse_opportunities += 1

                if item.analysis_source != "reused":
                    potential_reuse_misses += 1

            seen_fingerprints.add(key)

        assisted = [
            item
            for item in analyses
            if item.analysis_source
            == "generated_with_context"
        ]

        current_report_rows_ignored = 0
        historical_sources_evaluated = 0
        assisted_with_historical_sources = 0

        current_threshold_violations = 0
        legacy_threshold_storage_rows = 0
        current_future_violations = 0
        current_scope_violations = 0
        current_compatibility_violations = 0
        legacy_compatibility_conflicts = 0

        health_agreements = 0
        health_comparisons = 0

        assisted_details: list[
            dict[str, Any]
        ] = []

        for item in assisted:
            current_doc = (
                document_by_analysis.get(item.id)
            )
            all_used_sources = (
                source_rows_by_analysis.get(
                    item.id,
                    [],
                )
            )

            historical_sources = [
                source
                for source in all_used_sources
                if is_historical_source(source)
            ]

            current_report_rows_ignored += (
                len(all_used_sources)
                - len(historical_sources)
            )

            if historical_sources:
                assisted_with_historical_sources += 1

            item_detail: dict[str, Any] = {
                "analysis_id": item.id,
                "report_id": item.report_id,
                "retrieval_score": (
                    item.retrieval_score
                ),
                "historical_source_count": (
                    len(historical_sources)
                ),
                "ignored_non_historical_rows": (
                    len(all_used_sources)
                    - len(historical_sources)
                ),
                "sources": [],
            }

            for source_row in historical_sources:
                historical_sources_evaluated += 1

                historical_analysis = (
                    session.get(
                        ReportAnalysisModel,
                        source_row.source_analysis_id,
                    )
                )

                historical_doc = (
                    document_by_analysis.get(
                        source_row.source_analysis_id
                    )
                )

                if historical_doc is None:
                    historical_doc = (
                        session.scalar(
                            select(
                                ReportRetrievalDocumentModel
                            ).where(
                                ReportRetrievalDocumentModel
                                .analysis_id
                                == source_row
                                .source_analysis_id
                            )
                        )
                    )

                vector_score, score_origin = (
                    effective_vector_score(
                        source_row
                    )
                )

                legacy_rrf_storage = (
                    is_legacy_rrf_storage(
                        source_row,
                        vector_score,
                    )
                )

                if legacy_rrf_storage:
                    legacy_threshold_storage_rows += 1

                threshold_ok = (
                    vector_score is not None
                    and vector_score
                    >= settings.rag_minimum_similarity
                )

                if (
                    not threshold_ok
                    and not legacy_rrf_storage
                ):
                    current_threshold_violations += 1

                temporal_ok = (
                    historical_analysis
                    is not None
                    and historical_analysis
                    .created_at
                    <= item.created_at
                )

                if not temporal_ok:
                    current_future_violations += 1

                scope_ok = (
                    source_scope_matches(
                        current_doc,
                        historical_doc,
                    )
                )

                if not scope_ok:
                    current_scope_violations += 1

                compatible = False
                conflicts: list[
                    dict[str, Any]
                ] = []

                if (
                    current_doc is not None
                    and historical_doc
                    is not None
                ):
                    result = checker.check(
                        current_normalized_report=(
                            current_doc
                            .normalized_text
                        ),
                        historical_normalized_report=(
                            historical_doc
                            .normalized_text
                        ),
                    )

                    compatible = (
                        result.compatible
                    )
                    conflicts = [
                        asdict(conflict)
                        for conflict
                        in result.conflicts
                    ]

                current_contract = (
                    has_current_hybrid_metadata_contract(
                        source_row
                    )
                )

                if not compatible:
                    if current_contract:
                        current_compatibility_violations += 1
                    else:
                        legacy_compatibility_conflicts += 1

                if (
                    historical_analysis
                    is not None
                    and item.health_status
                    is not None
                    and historical_analysis
                    .health_status
                    is not None
                ):
                    health_comparisons += 1

                    if (
                        item.health_status
                        == historical_analysis
                        .health_status
                    ):
                        health_agreements += 1

                item_detail["sources"].append(
                    {
                        "source_analysis_id": (
                            source_row
                            .source_analysis_id
                        ),
                        "source_report_id": (
                            source_row
                            .source_report_id
                        ),
                        "strategy": (
                            source_row
                            .retrieval_strategy
                        ),
                        "stored_similarity_score": (
                            source_row
                            .similarity_score
                        ),
                        "effective_vector_score": (
                            vector_score
                        ),
                        "vector_score_origin": (
                            score_origin
                        ),
                        "legacy_rrf_storage": (
                            legacy_rrf_storage
                        ),
                        "current_metadata_contract": (
                            current_contract
                        ),
                        "rank": source_row.rank,
                        "threshold_ok": (
                            threshold_ok
                        ),
                        "temporal_ok": (
                            temporal_ok
                        ),
                        "scope_ok": scope_ok,
                        "compatible": (
                            compatible
                        ),
                        "conflicts": conflicts,
                        "metadata": (
                            source_row
                            .source_metadata
                            or {}
                        ),
                    }
                )

            assisted_details.append(
                item_detail
            )

        duration_groups: dict[
            str,
            list[float],
        ] = {}

        for item in analyses:
            if item.duration_ms is None:
                continue

            duration_groups.setdefault(
                item.analysis_source,
                [],
            ).append(
                float(item.duration_ms)
            )

        avg_duration = {
            key: round(
                mean(values),
                2,
            )
            for key, values
            in duration_groups.items()
            if values
        }

        hnsw_present = (
            fetch_hnsw_index_present(
                session
            )
        )

        invariant_failures = []

        if (
            current_threshold_violations
            > 0
        ):
            invariant_failures.append(
                "vector_threshold"
            )

        if current_future_violations > 0:
            invariant_failures.append(
                "temporal_order"
            )

        if current_scope_violations > 0:
            invariant_failures.append(
                "retrieval_scope"
            )

        if (
            current_compatibility_violations
            > 0
        ):
            invariant_failures.append(
                "structured_compatibility"
            )

        if (
            valid_reuse
            != len(reused_rows)
        ):
            invariant_failures.append(
                "exact_reuse_integrity"
            )

        if not hnsw_present:
            invariant_failures.append(
                "hnsw_index"
            )

        invariant_status = (
            "PASS"
            if not invariant_failures
            else "FAIL"
        )

        summary = EvaluationSummary(
            completed_analyses=len(analyses),
            reused=counts.get(
                "reused",
                0,
            ),
            assisted=counts.get(
                "generated_with_context",
                0,
            ),
            full=counts.get(
                "generated",
                0,
            ),
            llm_call_rate=(
                llm_calls
                / len(analyses)
                if analyses
                else 0.0
            ),
            exact_reuse_integrity=ratio(
                valid_reuse,
                len(reused_rows),
            ),
            potential_exact_reuse_miss_rate=(
                ratio(
                    potential_reuse_misses,
                    potential_reuse_opportunities,
                )
            ),
            assisted_analyses_with_historical_sources=(
                assisted_with_historical_sources
            ),
            historical_sources_evaluated=(
                historical_sources_evaluated
            ),
            current_report_rows_ignored=(
                current_report_rows_ignored
            ),
            current_threshold_violations=(
                current_threshold_violations
            ),
            legacy_threshold_storage_rows=(
                legacy_threshold_storage_rows
            ),
            current_future_leakage_violations=(
                current_future_violations
            ),
            current_scope_violations=(
                current_scope_violations
            ),
            current_compatibility_violations=(
                current_compatibility_violations
            ),
            legacy_compatibility_conflicts=(
                legacy_compatibility_conflicts
            ),
            assisted_health_agreement_rate=(
                ratio(
                    health_agreements,
                    health_comparisons,
                )
            ),
            hnsw_index_present=(
                hnsw_present
            ),
            avg_duration_ms_by_source=(
                avg_duration
            ),
            retrieval_strategy_counts=(
                dict(strategy_counts)
            ),
            invariant_status=(
                invariant_status
            ),
        )

        return {
            "generated_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "policy": (
                settings.rag_policy_summary
            ),
            "notes": {
                "current_report_rows_ignored": (
                    "used_in_prompt rows without "
                    "source_analysis_id are not "
                    "historical retrieval sources "
                    "and are excluded."
                ),
                "legacy_threshold_storage_rows": (
                    "Historical Step 3.4 rows that "
                    "stored RRF in similarity_score "
                    "but preserve the real vector "
                    "similarity in metadata."
                ),
                "legacy_compatibility_conflicts": (
                    "Historical source rows lacking "
                    "the current rrf_score/vector_score "
                    "persistence contract. These are "
                    "reported separately rather than "
                    "treated as current-policy failures."
                ),
                "assisted_health_agreement_rate": (
                    "Proxy only; matching health status "
                    "is not relevance ground truth."
                ),
                "potential_exact_reuse_miss_rate": (
                    "Diagnostic only; force=True may "
                    "intentionally bypass reuse."
                ),
            },
            "invariant_failures": (
                invariant_failures
            ),
            "summary": (
                asdict(summary)
            ),
            "assisted_details": (
                assisted_details
            ),
        }


def print_summary(
    report: dict[str, Any],
) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى print_summary؛ المدخلات المهمة: report.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    summary = report["summary"]

    print()
    print(
        "RAG End-to-End Evaluation"
    )
    print("=" * 36)

    print(
        "Completed analyses: "
        f"{summary['completed_analyses']}"
    )
    print(
        "REUSE:              "
        f"{summary['reused']}"
    )
    print(
        "ASSISTED:           "
        f"{summary['assisted']}"
    )
    print(
        "FULL:               "
        f"{summary['full']}"
    )
    print(
        "LLM call rate:      "
        f"{summary['llm_call_rate']:.2%}"
    )

    exact = (
        summary[
            "exact_reuse_integrity"
        ]
    )
    if exact is not None:
        print(
            "Exact reuse integrity: "
            f"{exact:.2%}"
        )

    miss = (
        summary[
            "potential_exact_reuse_miss_rate"
        ]
    )
    if miss is not None:
        print(
            "Potential reuse miss rate*: "
            f"{miss:.2%}"
        )

    agreement = (
        summary[
            "assisted_health_agreement_rate"
        ]
    )
    if agreement is not None:
        print(
            "Assisted health agreement*: "
            f"{agreement:.2%}"
        )

    print()
    print(
        "Historical sources evaluated: "
        f"{summary['historical_sources_evaluated']}"
    )
    print(
        "Current-report rows ignored:   "
        f"{summary['current_report_rows_ignored']}"
    )

    print()
    print(
        "Current threshold violations:  "
        f"{summary['current_threshold_violations']}"
    )
    print(
        "Legacy RRF storage rows:       "
        f"{summary['legacy_threshold_storage_rows']}"
    )
    print(
        "Current future leakage:        "
        f"{summary['current_future_leakage_violations']}"
    )
    print(
        "Current scope violations:      "
        f"{summary['current_scope_violations']}"
    )
    print(
        "Current compatibility failures:"
        f" {summary['current_compatibility_violations']}"
    )
    print(
        "Legacy compatibility conflicts:"
        f" {summary['legacy_compatibility_conflicts']}"
    )

    print()
    print(
        "HNSW index present:            "
        f"{summary['hnsw_index_present']}"
    )
    print(
        "Current invariant status:      "
        f"{summary['invariant_status']}"
    )

    if report["invariant_failures"]:
        print(
            "Invariant failures:           "
            + ", ".join(
                report[
                    "invariant_failures"
                ]
            )
        )

    print()
    print(
        "* Diagnostic/proxy metric, "
        "not labeled precision/recall."
    )


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate RAG/reuse behavior "
            "from database history."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Evaluate only the oldest N "
            "completed analyses."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path.",
    )

    args = parser.parse_args()

    report = evaluate_database(
        limit=args.limit
    )

    print_summary(report)

    output = args.output

    if output is None:
        timestamp = (
            datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        output = (
            Path("artifacts")
            / f"rag_evaluation_{timestamp}.json"
        )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"JSON report: {output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
