"""Investigation capability package with lazy public exports."""

from importlib import import_module

_MODULES = (
    "execution_contracts",
    "persistence_service",
    "investigation_router",
    "specialist_registry",
    "specialist_investigation_loop",
    "evidence_collection",
    "correlation",
    "final_diagnosis_synthesizer",
    "runtime_snapshot_service",
    "specialist_context",
    "specialist_reasoning_agent",
    "specialist_reasoning_client",
)


def __getattr__(name: str):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

    تُستدعى عندما يصل workflow إلى __getattr__؛ المدخلات المهمة: name.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    for module_name in _MODULES:
        module = import_module(f"{__name__}.{module_name}")
        if hasattr(module, name):
            return getattr(module, name)
    if name in {
        "EvidenceKind",
        "EvidenceReference",
        "InvestigationBudget",
        "InvestigationFinding",
        "InvestigationHypothesis",
        "InvestigationStatus",
        "KnowledgeSourceReference",
        "KnowledgeSourceType",
        "ServerInvestigationState",
        "SpecialistResult",
        "SpecialistTask",
        "SpecialistTaskStatus",
    }:
        module = import_module("app.core.contracts.investigation")
        return getattr(module, name)
    if name.startswith("DiagnosticPolicy"):
        module = import_module("app.core.policies.diagnostic_policy")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
