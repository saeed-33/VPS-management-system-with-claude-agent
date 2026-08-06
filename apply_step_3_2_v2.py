from __future__ import annotations

from pathlib import Path
import py_compile
import shutil
import sys
from datetime import datetime


ROOT = Path(__file__).resolve().parent
BACKUP_ROOT = ROOT / ".step_3_2_backup" / datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

TOUCHED_FILES = [
    "app/agent/analysis/retrieval/reuse_policy.py",
    "app/agent/analysis/retrieval/__init__.py",
    "app/agent/analysis/analysis_orchestrator.py",
    "app/bootstrap.py",
]


def file_path(path: str) -> Path:
    return ROOT / path


def read(path: str) -> str:
    target = file_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return target.read_text(encoding="utf-8")


def backup(path: str) -> None:
    source = file_path(path)
    if not source.exists():
        return
    destination = BACKUP_ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def write(path: str, content: str) -> None:
    target = file_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"Updated: {path}")


def replace_once(content: str, old: str, new: str, path: str) -> str:
    if new in content:
        return content
    if old not in content:
        raise RuntimeError(
            f"Expected code block was not found in: {path}\n"
            "The file differs from the reviewed GitHub version."
        )
    return content.replace(old, new, 1)


def create_reuse_policy() -> None:
    path = "app/agent/analysis/retrieval/reuse_policy.py"
    content = """from dataclasses import dataclass
from enum import StrEnum


class AnalysisDecision(StrEnum):
    REUSE = \"reuse\"
    ASSISTED = \"assisted\"
    FULL = \"full\"


@dataclass(slots=True, frozen=True)
class AnalysisDecisionResult:
    decision: AnalysisDecision
    reason: str


class AnalysisReusePolicy:
    \"\"\"
    Central policy for selecting the report analysis path.

    Direct reuse remains restricted to exact fingerprint matches.
    Semantic or vector similarity may provide assisted context only.
    \"\"\"

    def decide(
        self,
        *,
        fingerprint_match: bool,
        historical_context_available: bool,
        assisted_enabled: bool,
        force: bool = False,
    ) -> AnalysisDecisionResult:
        if force:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.FULL,
                reason=\"forced_analysis\",
            )

        if fingerprint_match:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.REUSE,
                reason=\"exact_fingerprint_match\",
            )

        if assisted_enabled and historical_context_available:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.ASSISTED,
                reason=\"historical_context_available\",
            )

        return AnalysisDecisionResult(
            decision=AnalysisDecision.FULL,
            reason=\"no_usable_historical_context\",
        )
"""
    write(path, content)


def update_retrieval_init() -> None:
    path = "app/agent/analysis/retrieval/__init__.py"
    content = read(path)
    import_block = """from app.agent.analysis.retrieval.reuse_policy import (
    AnalysisDecision,
    AnalysisDecisionResult,
    AnalysisReusePolicy,
)
"""
    if "AnalysisReusePolicy" not in content:
        content = content.rstrip() + "\n\n" + import_block
    write(path, content.rstrip() + "\n")


def update_orchestrator() -> None:
    path = "app/agent/analysis/analysis_orchestrator.py"
    content = read(path)

    import_anchor = """from app.agent.analysis.retrieval.rag_retriever import (
    RagRetriever,
)
"""
    import_replacement = import_anchor + """from app.agent.analysis.retrieval.reuse_policy import (
    AnalysisDecision,
    AnalysisReusePolicy,
)
"""
    content = replace_once(content, import_anchor, import_replacement, path)

    constructor_anchor = """        rag_context_builder: RagContextBuilder | None = None,
        analysis_source_repository: AnalysisSourceRepository | None = None,
"""
    constructor_replacement = """        rag_context_builder: RagContextBuilder | None = None,
        analysis_source_repository: AnalysisSourceRepository | None = None,
        rag_assisted_enabled: bool = True,
        analysis_reuse_policy: AnalysisReusePolicy | None = None,
"""
    content = replace_once(content, constructor_anchor, constructor_replacement, path)

    assignment_anchor = """        self._analysis_source_repository = (
            analysis_source_repository
        )

        self._fingerprint_service = (
"""
    assignment_replacement = """        self._analysis_source_repository = (
            analysis_source_repository
        )
        self._rag_assisted_enabled = rag_assisted_enabled
        self._reuse_policy = (
            analysis_reuse_policy
            or AnalysisReusePolicy()
        )

        self._fingerprint_service = (
"""
    content = replace_once(content, assignment_anchor, assignment_replacement, path)

    exact_anchor = """            if reusable_analysis is not None:
                reused = (
"""
    exact_replacement = """            exact_decision = self._reuse_policy.decide(
                fingerprint_match=(
                    reusable_analysis is not None
                ),
                historical_context_available=False,
                assisted_enabled=False,
                force=force,
            )

            if (
                reusable_analysis is not None
                and exact_decision.decision
                == AnalysisDecision.REUSE
            ):
                logger.info(
                    \"Analysis decision | report_id=%s | \"
                    \"decision=%s | reason=%s\",
                    report_id,
                    exact_decision.decision.value,
                    exact_decision.reason,
                )

                reused = (
"""
    content = replace_once(content, exact_anchor, exact_replacement, path)

    malformed = """                        normalized_report=normalized_report,            server_id=server_id,
"""
    formatted = """                        normalized_report=normalized_report,
                        server_id=server_id,
"""
    if malformed in content:
        content = content.replace(malformed, formatted, 1)

    analyze_anchor = """        analysis_id = await (
            self._report_analyzer.analyze(
"""
    decision_block = """        analysis_decision = self._reuse_policy.decide(
            fingerprint_match=False,
            historical_context_available=bool(
                retrieved_contexts
            ),
            assisted_enabled=(
                self._rag_assisted_enabled
            ),
            force=force,
        )

        if (
            analysis_decision.decision
            == AnalysisDecision.FULL
        ):
            retrieved_contexts = []
            rag_prompt_context = []

        logger.info(
            \"Analysis decision | report_id=%s | \"
            \"decision=%s | reason=%s | contexts=%s\",
            report_id,
            analysis_decision.decision.value,
            analysis_decision.reason,
            len(retrieved_contexts),
        )

"""
    if decision_block not in content:
        if analyze_anchor not in content:
            raise RuntimeError(f"Analyze call was not found in: {path}")
        content = content.replace(analyze_anchor, decision_block + analyze_anchor, 1)

    metadata_anchor = """            analysis_source=\"generated\",
            reused_from_analysis_id=None,
            retrieval_strategy=\"vector\"
            if retrieved_contexts
            else None,
"""
    metadata_replacement = """            analysis_source=(
                \"generated_with_context\"
                if analysis_decision.decision
                == AnalysisDecision.ASSISTED
                else \"generated\"
            ),
            reused_from_analysis_id=None,
            retrieval_strategy=(
                \"vector\"
                if analysis_decision.decision
                == AnalysisDecision.ASSISTED
                else None
            ),
"""
    content = replace_once(content, metadata_anchor, metadata_replacement, path)

    score_anchor = """            retrieval_score=(
                retrieved_contexts[0].score
                if retrieved_contexts
                else None
            ),
"""
    score_replacement = """            retrieval_score=(
                retrieved_contexts[0].score
                if (
                    analysis_decision.decision
                    == AnalysisDecision.ASSISTED
                    and retrieved_contexts
                )
                else None
            ),
"""
    content = replace_once(content, score_anchor, score_replacement, path)

    write(path, content)


def update_bootstrap() -> None:
    path = "app/bootstrap.py"
    content = read(path)

    old_rag_block = """    if (
        settings.rag_vector_enabled
        and settings.rag_assisted_enabled
    ):
        embedding_client = create_embedding_client(settings)
        retrieval_indexer = RetrievalIndexer(
            analysis_repository=analysis_repository,
            retrieval_repository=retrieval_repository,
            embedding_client=embedding_client,
        )
        rag_retriever = RagRetriever(
            embedding_client=embedding_client,
            retrieval_repository=retrieval_repository,
            analysis_repository=analysis_repository,
            top_k=settings.rag_context_top_k,
            minimum_score=settings.rag_minimum_similarity,
        )
        rag_context_builder = RagContextBuilder()
"""
    new_rag_block = """    if settings.rag_vector_enabled:
        embedding_client = create_embedding_client(
            settings
        )
        retrieval_indexer = RetrievalIndexer(
            analysis_repository=analysis_repository,
            retrieval_repository=retrieval_repository,
            embedding_client=embedding_client,
        )

        if settings.rag_assisted_enabled:
            rag_retriever = RagRetriever(
                embedding_client=embedding_client,
                retrieval_repository=retrieval_repository,
                analysis_repository=analysis_repository,
                top_k=settings.rag_context_top_k,
                minimum_score=(
                    settings.rag_minimum_similarity
                ),
            )
            rag_context_builder = RagContextBuilder()
"""
    content = replace_once(content, old_rag_block, new_rag_block, path)

    orchestrator_anchor = """                analysis_source_repository=(
                    analysis_source_repository
                ),
"""
    orchestrator_replacement = """                analysis_source_repository=(
                    analysis_source_repository
                ),
                rag_assisted_enabled=(
                    settings.rag_assisted_enabled
                ),
"""
    content = replace_once(content, orchestrator_anchor, orchestrator_replacement, path)

    write(path, content)


def validate() -> None:
    for path in TOUCHED_FILES:
        target = file_path(path)
        if target.suffix == ".py":
            py_compile.compile(str(target), doraise=True)
    print("Syntax validation passed.")


def restore_backups() -> None:
    if not BACKUP_ROOT.exists():
        return
    for path in TOUCHED_FILES:
        backup_file = BACKUP_ROOT / path
        if not backup_file.exists():
            continue
        destination = file_path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_file, destination)
    print(f"Changes were rolled back from: {BACKUP_ROOT}")


def main() -> int:
    for path in TOUCHED_FILES:
        backup(path)

    try:
        create_reuse_policy()
        update_retrieval_init()
        update_orchestrator()
        update_bootstrap()
        validate()
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        restore_backups()
        return 1

    print(
        "\nStep 3.2 applied successfully.\n"
        f"Backup directory: {BACKUP_ROOT}\n\n"
        "Next commands:\n"
        "  python -m compileall `\n"
        "      app\\admin `\n"
        "      app\\agent `\n"
        "      app\\shared `\n"
        "      app\\bootstrap.py `\n"
        "      app\\main.py\n\n"
        "  python -m uvicorn app.main:app --reload\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
