"""
جزء من Analysis لتحويل report إلى analysis مع Retrieval وLLM.

الموقع في المعمارية: Application capability / analysis.
يُستدعى بواسطة: MCP أو مسارات ما بعد Monitoring.
يعتمد مباشرة على: app.core.contracts.analysis.
الحد المعماري: لا ينفذ SSH أو Investigation أو Remediation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from abc import ABC, abstractmethod

from app.core.contracts.analysis import (
    ReportAnalysisResult,
)


class LLMAnalysisClient(ABC):
    """
    يمثل LLMAnalysisClient مسؤولية محددة داخل طبقة Application capability / analysis.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو مسارات ما بعد Monitoring
    ويعتمد على ABC وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / analysis.

        تُستدعى عندما يصل workflow إلى provider_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / analysis.

        تُستدعى عندما يصل workflow إلى model_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / analysis.

        تُستدعى عندما يصل workflow إلى analyze_report؛ المدخلات المهمة: system_prompt، user_prompt.
        تعيد ReportAnalysisResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        raise NotImplementedError

    async def health_check(self) -> None:
        """
        Raises an exception when the provider
        cannot be reached or is misconfigured.
        """
        return None