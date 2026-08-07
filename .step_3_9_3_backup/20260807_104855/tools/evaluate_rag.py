from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_value = str(PROJECT_ROOT)
if project_root_value not in sys.path:
    sys.path.insert(0, project_root_value)

from statistics import mean
from typing import Any

from sqlalchemy import select, text

from app.agent.analysis.retrieval.structured_compatibility import (
    StructuredCompatibilityChecker,
)
from app.shared.config import settings
from app.shared.database.models.report_analysis import (
    ReportAnalysisModel,
)
from app.shared.database.models.report_analysis_source import (
    ReportAnalysisSourceModel,
)
from app.shared.database.models.report_retrieval_document import (
    ReportRetrievalDocumentModel,
)
from app.shared.database.session import SessionLocal


@dataclass(slots=True)
class EvaluationSummary:
    completed_analyses: int
    reused: int
    assisted: int
    full: int
    llm_call_rate: float
    exact_reuse_integrity: float | None
    potential_exact_reuse_miss_rate: float | None
    assisted_threshold_violations: int
    assisted_future_leakage_violations: int
    assisted_scope_violations: int
    assisted_compatibility_violations: int
    assisted_health_agreement_rate: float | None
    hnsw_index_present: bool
    avg_duration_ms_by_source: dict[str, float]
    retrieval_strategy_counts: dict[str, int]


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def fetch_hnsw_index_present(session) -> bool:
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


def build_document_map(session) -> dict[int, ReportRetrievalDocumentModel]:
    documents = session.scalars(
        select(ReportRetrievalDocumentModel)
    ).all()
    return {document.analysis_id: document for document in documents}


def source_scope_matches(
    current: ReportRetrievalDocumentModel | None,
    historical: ReportRetrievalDocumentModel | None,
) -> bool:
    if current is None or historical is None:
        return False

    return (
        current.server_id == historical.server_id
        and current.monitoring_profile_id
        == historical.monitoring_profile_id
        and current.command_set_hash
        == historical.command_set_hash
    )


def evaluate_database(limit: int | None = None) -> dict[str, Any]:
    checker = StructuredCompatibilityChecker()

    with SessionLocal() as session:
        statement = (
            select(ReportAnalysisModel)
            .where(ReportAnalysisModel.status == 'completed')
            .order_by(ReportAnalysisModel.created_at.asc())
        )

        if limit is not None:
            statement = statement.limit(limit)

        analyses = list(session.scalars(statement).all())
        analysis_by_id = {item.id: item for item in analyses}
        document_by_analysis = build_document_map(session)

        sources = list(
            session.scalars(
                select(ReportAnalysisSourceModel)
                .where(ReportAnalysisSourceModel.used_in_prompt.is_(True))
            ).all()
        )

        source_rows_by_analysis: dict[int, list[ReportAnalysisSourceModel]] = {}
        for source in sources:
            source_rows_by_analysis.setdefault(
                source.analysis_id,
                [],
            ).append(source)

        counts = Counter(item.analysis_source for item in analyses)
        strategy_counts = Counter(
            item.retrieval_strategy or 'none'
            for item in analyses
        )

        llm_calls = sum(bool(item.llm_called) for item in analyses)

        reused_rows = [
            item
            for item in analyses
            if item.analysis_source == 'reused'
        ]

        valid_reuse = 0
        for item in reused_rows:
            source = analysis_by_id.get(item.reused_from_analysis_id)
            if source is None:
                # Source may be outside a limited evaluation window.
                source = session.get(
                    ReportAnalysisModel,
                    item.reused_from_analysis_id,
                )

            if source is None:
                continue

            if (
                item.report_fingerprint
                and item.report_fingerprint == source.report_fingerprint
                and item.server_id == source.server_id
                and source.created_at <= item.created_at
                and item.llm_called is False
            ):
                valid_reuse += 1

        # A potential miss is not labeled as a true recall error because
        # force=True may intentionally bypass reuse.
        potential_reuse_opportunities = 0
        potential_reuse_misses = 0
        seen_fingerprints: set[tuple[int, str]] = set()

        for item in analyses:
            if item.report_fingerprint:
                key = (item.server_id, item.report_fingerprint)
                if key in seen_fingerprints:
                    potential_reuse_opportunities += 1
                    if item.analysis_source != 'reused':
                        potential_reuse_misses += 1
                seen_fingerprints.add(key)

        assisted = [
            item
            for item in analyses
            if item.analysis_source == 'generated_with_context'
        ]

        threshold_violations = 0
        future_violations = 0
        scope_violations = 0
        compatibility_violations = 0
        health_agreements = 0
        health_comparisons = 0

        assisted_details: list[dict[str, Any]] = []

        for item in assisted:
            current_doc = document_by_analysis.get(item.id)
            used_sources = source_rows_by_analysis.get(item.id, [])

            item_detail = {
                'analysis_id': item.id,
                'report_id': item.report_id,
                'retrieval_score': item.retrieval_score,
                'sources': [],
            }

            for source_row in used_sources:
                historical_analysis = None
                historical_doc = None

                if source_row.source_analysis_id is not None:
                    historical_analysis = session.get(
                        ReportAnalysisModel,
                        source_row.source_analysis_id,
                    )
                    historical_doc = document_by_analysis.get(
                        source_row.source_analysis_id
                    )
                    if historical_doc is None:
                        historical_doc = session.scalar(
                            select(ReportRetrievalDocumentModel).where(
                                ReportRetrievalDocumentModel.analysis_id
                                == source_row.source_analysis_id
                            )
                        )

                score = source_row.similarity_score
                threshold_ok = (
                    score is not None
                    and score >= settings.rag_minimum_similarity
                )
                if not threshold_ok:
                    threshold_violations += 1

                temporal_ok = (
                    historical_analysis is not None
                    and historical_analysis.created_at <= item.created_at
                )
                if not temporal_ok:
                    future_violations += 1

                scope_ok = source_scope_matches(
                    current_doc,
                    historical_doc,
                )
                if not scope_ok:
                    scope_violations += 1

                compatible = False
                conflicts: list[dict[str, Any]] = []
                if current_doc is not None and historical_doc is not None:
                    result = checker.check(
                        current_normalized_report=current_doc.normalized_text,
                        historical_normalized_report=historical_doc.normalized_text,
                    )
                    compatible = result.compatible
                    conflicts = [asdict(conflict) for conflict in result.conflicts]

                if not compatible:
                    compatibility_violations += 1

                if (
                    historical_analysis is not None
                    and item.health_status is not None
                    and historical_analysis.health_status is not None
                ):
                    health_comparisons += 1
                    if item.health_status == historical_analysis.health_status:
                        health_agreements += 1

                item_detail['sources'].append(
                    {
                        'source_analysis_id': source_row.source_analysis_id,
                        'source_report_id': source_row.source_report_id,
                        'strategy': source_row.retrieval_strategy,
                        'similarity_score': score,
                        'rank': source_row.rank,
                        'threshold_ok': threshold_ok,
                        'temporal_ok': temporal_ok,
                        'scope_ok': scope_ok,
                        'compatible': compatible,
                        'conflicts': conflicts,
                        'metadata': source_row.source_metadata or {},
                    }
                )

            assisted_details.append(item_detail)

        duration_groups: dict[str, list[float]] = {}
        for item in analyses:
            if item.duration_ms is None:
                continue
            duration_groups.setdefault(
                item.analysis_source,
                [],
            ).append(float(item.duration_ms))

        avg_duration = {
            key: round(mean(values), 2)
            for key, values in duration_groups.items()
            if values
        }

        summary = EvaluationSummary(
            completed_analyses=len(analyses),
            reused=counts.get('reused', 0),
            assisted=counts.get('generated_with_context', 0),
            full=counts.get('generated', 0),
            llm_call_rate=(llm_calls / len(analyses)) if analyses else 0.0,
            exact_reuse_integrity=ratio(valid_reuse, len(reused_rows)),
            potential_exact_reuse_miss_rate=ratio(
                potential_reuse_misses,
                potential_reuse_opportunities,
            ),
            assisted_threshold_violations=threshold_violations,
            assisted_future_leakage_violations=future_violations,
            assisted_scope_violations=scope_violations,
            assisted_compatibility_violations=compatibility_violations,
            assisted_health_agreement_rate=ratio(
                health_agreements,
                health_comparisons,
            ),
            hnsw_index_present=fetch_hnsw_index_present(session),
            avg_duration_ms_by_source=avg_duration,
            retrieval_strategy_counts=dict(strategy_counts),
        )

        return {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'policy': settings.rag_policy_summary,
            'notes': {
                'exact_reuse_integrity': (
                    'Provable integrity metric: reused rows must point to an older '
                    'analysis on the same server with the same fingerprint and no LLM call.'
                ),
                'potential_exact_reuse_miss_rate': (
                    'Diagnostic only, not true recall. force=True can intentionally bypass reuse.'
                ),
                'assisted_health_agreement_rate': (
                    'Proxy metric only. Matching health status is not ground-truth relevance.'
                ),
            },
            'summary': asdict(summary),
            'assisted_details': assisted_details,
        }


def print_summary(report: dict[str, Any]) -> None:
    summary = report['summary']

    print('\nRAG End-to-End Evaluation')
    print('=' * 32)
    print(f"Completed analyses: {summary['completed_analyses']}")
    print(f"REUSE:              {summary['reused']}")
    print(f"ASSISTED:           {summary['assisted']}")
    print(f"FULL:               {summary['full']}")
    print(f"LLM call rate:      {summary['llm_call_rate']:.2%}")

    exact = summary['exact_reuse_integrity']
    if exact is not None:
        print(f"Exact reuse integrity: {exact:.2%}")

    miss = summary['potential_exact_reuse_miss_rate']
    if miss is not None:
        print(f"Potential reuse miss rate*: {miss:.2%}")

    agreement = summary['assisted_health_agreement_rate']
    if agreement is not None:
        print(f"Assisted health agreement*: {agreement:.2%}")

    print(
        'Threshold violations:  '
        f"{summary['assisted_threshold_violations']}"
    )
    print(
        'Future leakage:        '
        f"{summary['assisted_future_leakage_violations']}"
    )
    print(
        'Scope violations:      '
        f"{summary['assisted_scope_violations']}"
    )
    print(
        'Compatibility rejects: '
        f"{summary['assisted_compatibility_violations']}"
    )
    print(
        'HNSW index present:    '
        f"{summary['hnsw_index_present']}"
    )
    print('\n* Diagnostic/proxy metric, not labeled precision/recall.')


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Evaluate RAG/reuse behavior from production-like database history.'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Evaluate only the oldest N completed analyses.',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Optional JSON output path.',
    )
    args = parser.parse_args()

    report = evaluate_database(limit=args.limit)
    print_summary(report)

    output = args.output
    if output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = Path('artifacts') / f'rag_evaluation_{timestamp}.json'

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding='utf-8',
    )

    print(f'\nJSON report: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
