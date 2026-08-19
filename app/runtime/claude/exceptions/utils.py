"""أدوات وصف أخطاء Claude."""

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

