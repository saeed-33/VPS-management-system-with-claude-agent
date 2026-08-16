"""
واجهة حزمة التحليل.

توفّر استيرادًا كسولًا لمكونات التحليل والاسترجاع المرتبطة به، لتقليل تكلفة
تحميل الوحدات مع إبقاء واجهة الحزمة موحّدة أمام طبقة التركيب.
"""

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
    يحمّل وحدات التحليل المعروفة عند الطلب ويعيد الرمز المطلوب من أول وحدة تصدّره.
    """
    for module_name in _MODULES:
        module = import_module(f"{__name__}.{module_name}")
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
