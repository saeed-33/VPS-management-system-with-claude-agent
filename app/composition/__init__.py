"""
يركب dependencies ويربط repositories والخدمات والـruntime.

الموقع في المعمارية: Bootstrap / dependency composition.
يُستدعى بواسطة: app.main أو الاختبارات عند إنشاء container.
يعتمد مباشرة على: app.composition.builder.
الحد المعماري: لا ينفذ workflow business؛ دوره wiring وترتيب الإنشاء.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
# Application composition root.
# This package owns dependency construction and wiring only.

from app.composition.builder import (
    ApplicationContainer,
    build_container,
)


container = build_container()


__all__ = [
    "ApplicationContainer",
    "build_container",
    "container",
]
