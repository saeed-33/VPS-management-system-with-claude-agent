"""
تصنيف أخطاء تشغيل Claude من لحظة إنشاء العملية حتى قراءة النتيجة.

تساعد الأنواع هنا على التمييز بين فشل العملية، ومخرجات غير منظمة، ومحاولة
استخدام أداة غير مسموحة، حتى تحفظ الخدمة سبب الفشل بدل إخفائه.
"""


def describe_exception(
    exc: BaseException,
    *,
    fallback: str,
) -> str:
    """
    يعيد وصفًا تشخيصيًا غير فارغ حتى لا تختفي أخطاء الاستثناءات الصامتة.

    بعض أخطاء العمليات أو المكتبات قد تملك ``str(exc)`` فارغًا، ولذلك نضمّن
    اسم النوع و``repr`` عند توفره، ثم نستخدم سببًا ثابتًا عند غياب أي تفاصيل.
    """
    message = str(exc).strip()
    if message:
        return message

    details = repr(exc).strip()
    empty_repr = f"{type(exc).__name__}()"
    if details and details != empty_repr:
        return f"{type(exc).__name__}: {details}"

    return f"{type(exc).__name__}: {fallback}"


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
