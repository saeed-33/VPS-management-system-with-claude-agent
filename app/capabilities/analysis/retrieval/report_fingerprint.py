"""
حساب بصمة مستقرة للتقرير بعد تطبيعه.

يحوّل النص المطبع إلى SHA-256 لاستخدامه في اكتشاف الحالة المطابقة وإعادة
استخدام التحليل السابق دون استنتاج تشابه غير مثبت.
"""
import hashlib


class ReportFingerprintService:
    """
    يوفر خدمة تحويل التقرير المطبع إلى بصمة ثابتة قابلة للمقارنة.
    """
    def create(
        self,
        normalized_report: str,
    ) -> str:
        """
        يحسب SHA-256 للنص المطبع ليكون معرفًا ثابتًا للحالات المتطابقة.
        """
        return hashlib.sha256(
            normalized_report.encode(
                "utf-8"
            )
        ).hexdigest()
