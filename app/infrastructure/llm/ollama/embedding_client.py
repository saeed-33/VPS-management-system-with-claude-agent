"""
تحويل نص التقرير أو المعرفة إلى متجه لاستخدامه في البحث الدلالي.
"""
import httpx

from app.core.ports.analysis.embedding_client import EmbeddingClient


class OllamaEmbeddingClient(EmbeddingClient):
    """
    عميل يولد متجهات Ollama ويتحقق من أبعادها قبل إدخالها إلى فهرس RAG.
    """
    def __init__(self, *, base_url: str, model: str, dimensions: int, timeout_seconds: float = 60.0) -> None:
        """
        يهيئ عنوان Ollama والنموذج وأبعاد المتجه ومهلة الطلب.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        """
        يعيد اسم مزود التضمين المستخدم في فهرس المعرفة.
        """
        return "ollama"

    @property
    def model_name(self) -> str:
        """
        يعيد اسم نموذج التضمين الذي أنتج المتجه.
        """
        return self._model

    @property
    def dimensions(self) -> int:
        """
        يعيد عدد الأبعاد المتوقع لكل متجه قبل حفظه.
        """
        return self._dimensions

    async def embed(self, text: str) -> list[float]:
        """
        يرسل نصًا إلى Ollama ويعيد متجهًا مطابقًا للأبعاد المطلوبة أو يرفضه.
        """
        if not text.strip():
            raise ValueError("Cannot embed empty text.")

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": text},
            )
            response.raise_for_status()
            payload = response.json()

        embeddings = payload.get("embeddings") or []
        if not embeddings:
            raise RuntimeError("Ollama returned no embedding.")

        vector = [float(value) for value in embeddings[0]]
        if len(vector) != self._dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self._dimensions}, got {len(vector)}."
            )
        return vector
