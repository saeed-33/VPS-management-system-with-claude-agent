"""Analysis capability package with lazy public exports."""

from importlib import import_module

_MODULES = (
    "analysis_orchestrator",
    "client_factory",
    "llm_client",
    "report_analyzer",
    "retrieval.reuse_policy",
    "retrieval.full_text_retriever",
    "retrieval.hybrid_retriever",
    "retrieval.structured_compatibility",
)


def __getattr__(name: str):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / analysis.

    تُستدعى عندما يصل workflow إلى __getattr__؛ المدخلات المهمة: name.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    for module_name in _MODULES:
        module = import_module(f"{__name__}.{module_name}")
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
