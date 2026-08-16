"""
تصنيف أخطاء تشغيل Claude من لحظة إنشاء العملية حتى قراءة النتيجة.

تساعد الأنواع هنا على التمييز بين فشل العملية، ومخرجات غير منظمة، ومحاولة
استخدام أداة غير مسموحة، حتى تحفظ الخدمة سبب الفشل بدل إخفائه.
"""
class ClaudeRuntimeError(RuntimeError):
    """
    النوع الأساسي لأخطاء دورة تشغيل Claude التي يجب تسجيلها كفشل مضبوط.
    """


class ClaudeStructuredOutputError(ClaudeRuntimeError):
    """
    خطأ يصف مخرجًا من Claude لا يمكن تحويله إلى نتيجة منظمة.
    """


class ClaudeToolAccessError(ClaudeRuntimeError):
    """
    خطأ يوضح أن الجلسة طلبت أدوات تشغيلية دون تفعيل صلاحيتها.
    """


class ClaudeProcessExecutionError(ClaudeRuntimeError):
    """
    خطأ يصف عدم قدرة النظام على إنشاء عملية Claude أو تشغيلها.
    """


class ClaudeProcessOutputError(ClaudeRuntimeError):
    """
    خطأ يصف مخرجًا فارغًا أو غير صالح أو لا يثبت اكتمال جلسة Claude.
    """
