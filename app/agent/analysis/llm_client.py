from abc import ABC, abstractmethod

from app.shared.dto.analysis import (
    ReportAnalysisResult,
)


class LLMAnalysisClient(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def analyze_report(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> ReportAnalysisResult:
        raise NotImplementedError

    async def health_check(self) -> None:
        """
        Raises an exception when the provider
        cannot be reached or is misconfigured.
        """
        return None