"""
Policy أو registry حتمي يقرر السماح أو الرفض أو التصنيف قبل التنفيذ.

الموقع في المعمارية: Core policy.
يُستدعى بواسطة: capabilities وMCP handlers.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا تنفذ SSH أو LLM أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from enum import StrEnum


class FingerprintStrategy(StrEnum):
    """
    يمثل FingerprintStrategy مسؤولية محددة داخل طبقة Core policy.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وMCP handlers
    ويعتمد على StrEnum وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    FULL_OUTPUT = "full_output"
    STATUS_ONLY = "status_only"
    CANONICAL_LINES = "canonical_lines"
    ERROR_SIGNATURE = "error_signature"
    EXCLUDE_OUTPUT = "exclude_output"