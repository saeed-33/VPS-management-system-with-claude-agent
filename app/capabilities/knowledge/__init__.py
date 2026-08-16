"""
واجهة قدرات مصادر المعرفة.

تجمع الاستيراد الكسول لمكونات التحميل والتحليل والتقطيع والفهرسة والاسترجاع،
بحيث تبقى رحلة المصدر من محتواه الخام إلى سياق البحث واضحة وقابلة للتتبع.
"""

from importlib import import_module

_MODULES = (
    "chunker",
    "chunking_service",
    "indexer",
    "ingestion_contracts",
    "ingestion_service",
    "parsers",
    "retrieval",
    "source_loader",
    "source_registry",
)


def __getattr__(name: str):
    """
    يحمّل وحدات المعرفة عند الطلب ويعيد الرمز من أول وحدة معروفة تصدّره.
    """
    for module_name in _MODULES:
        module = import_module(f"{__name__}.{module_name}")
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
