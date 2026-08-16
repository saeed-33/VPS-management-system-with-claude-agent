"""
الاستراتيجيات التي تحدد كيف تقارن المراقبة مخرجات فحصين.
"""
from enum import StrEnum


class FingerprintStrategy(StrEnum):
    """
    طرق استخراج بصمة من نتيجة الفحص لمعرفة هل تغيرت حالة السيرفر.
    """
    FULL_OUTPUT = "full_output"
    STATUS_ONLY = "status_only"
    CANONICAL_LINES = "canonical_lines"
    ERROR_SIGNATURE = "error_signature"
    EXCLUDE_OUTPUT = "exclude_output"