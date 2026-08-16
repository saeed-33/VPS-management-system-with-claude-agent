"""
بنية قاعدة البيانات من engine/session/base.

الموقع في المعمارية: Database infrastructure.
يُستدعى بواسطة: composition وrepositories.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يقرر domain behavior؛ يوفر الاتصال والجلسات.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    يمثل Base مسؤولية محددة داخل طبقة Database infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition وrepositories
    ويعتمد على DeclarativeBase وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    pass