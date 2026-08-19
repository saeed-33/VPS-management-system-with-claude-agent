"""
مخططات إدارة السيرفرات واختبار SSH.

تتحقق من طلبات إنشاء وتعديل السيرفر وتصف الاستجابة الإدارية ونتيجة اختبار
الاتصال دون تضمين منطق الاتصال داخل النماذج.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SSHTestResponse(BaseModel):
    """
    يمثل نتيجة اختبار اتصال SSH الإداري.
    """
    success: bool
    message: str
    hostname: str | None = None

