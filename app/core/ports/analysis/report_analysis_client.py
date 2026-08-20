"""
العقد المجرد لعملاء تحليل تقارير المراقبة.

يحدد هذا الملف البيانات الوصفية للمزوّد والنموذج، وطريقة إرسال المطالبات
وإرجاع نتيجة تحليل منظمة، مع فحص صحة اختياري للتكامل.
"""
from abc import ABC, abstractmethod

from app.core.contracts.analysis.report_analysis_result import ReportAnalysisResult


class LLMAnalysisClient(ABC):
    """
    يعرّف الواجهة التي يجب أن يطبقها أي مزوّد لتحليل تقرير المراقبة وإرجاع النتيجة المنظمة.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        يعيد الاسم الثابت لمزوّد النموذج الذي ينفذ عقد التحليل.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        يعيد اسم النموذج المستخدم لتحليل التقارير.
        """
        raise NotImplementedError

    @abstractmethod
    async def analyze_report(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> ReportAnalysisResult:
        """
        يرسل تعليمات النظام والمستخدم إلى المزوّد ويعيد نتيجة التحليل المنظمة.
        """
        raise NotImplementedError

    async def health_check(self) -> None:
        """
        يوفّر نقطة فحص صحة افتراضية للتكاملات التي لا تحتاج طلبًا إضافيًا.
        """
        return None
