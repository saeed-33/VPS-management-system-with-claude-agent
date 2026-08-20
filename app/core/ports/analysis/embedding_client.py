"""
العقد المجرد لخدمات تحويل التقارير إلى متجهات.

يحدد بيانات المزوّد والنموذج والأبعاد، وطريقة إنتاج embedding يستخدمه البحث
المتجهي في مستودع الاسترجاع.
"""
from abc import ABC, abstractmethod


class EmbeddingClient(ABC):
    """
    يعرّف الواجهة المشتركة لأي مزوّد يحوّل نص التقرير إلى متجه قابل للبحث.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        يعيد اسم مزوّد embedding المنفذ للعقد.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        يعيد اسم نموذج embedding المستخدم في البحث.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """
        يعيد عدد أبعاد المتجهات التي ينتجها المزوّد.
        """
        raise NotImplementedError

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        يحوّل النص إلى متجه embedding يمكن تخزينه ومقارنته بمتجهات التقارير السابقة.
        """
        raise NotImplementedError

    async def close(self) -> None:
        """Release provider resources owned by the embedding client."""
        return None
