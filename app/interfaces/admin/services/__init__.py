"""
خدمات مساندة لواجهات الإدارة.

تصدّر خدمات إنشاء PDF واختبار اتصال SSH التي تحتاجها مسارات الإدارة، مع إبقاء
التكاملات الخارجية خلف واجهات خدمات قابلة للحقن.
"""
from app.interfaces.admin.services.ssh_test_service import (
    SSHTestResult,
    SSHTestService,
)

__all__ = [
    "SSHTestService",
    "SSHTestResult",
]