"""
واجهة قدرات معالجة المشكلات.

تصدّر الخدمة التي تربط الاقتراح والتحقق والموافقة والتنفيذ والتراجع، مع إبقاء
الأثر التشغيلي لكل تغيير قابلًا للتدقيق.
"""

from app.capabilities.remediation.service import RemediationService

__all__ = ["RemediationService"]
