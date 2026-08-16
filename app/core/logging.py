"""
مكوّن مشترك مثل config أو exceptions أو logging.

الموقع في المعمارية: Core foundation.
يُستدعى بواسطة: الطبقات الأعلى.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يعتمد على capabilities أو infrastructure.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import logging


def configure_logging(
    level: int = logging.INFO,
) -> None:
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core foundation.

    تُستدعى عندما يصل workflow إلى configure_logging؛ المدخلات المهمة: level.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )