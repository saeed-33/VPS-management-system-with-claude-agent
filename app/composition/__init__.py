"""
نقطة الدخول إلى تركيب تطبيق مراقبة السيرفر.

تنشئ الحاوية العامة التي تربط المستودعات والخدمات ومكونات التشغيل، وتعرضها
لواجهات التطبيق دون نقل منطق المجال إلى طبقة التركيب.
"""
# نقطة تجميع رحلة مراقبة السيرفر وربط مراحلها بخدماتها المشتركة.

from app.composition.container_builder import (
    ApplicationContainer,
    build_container,
)


container = build_container()


__all__ = [
    "ApplicationContainer",
    "build_container",
    "container",
]
