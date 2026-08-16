"""
عميل Ollama يترجم contracts الداخلية إلى HTTP model calls ويعيد DTOs.

الموقع في المعمارية: LLM infrastructure.
يُستدعى بواسطة: capabilities عبر protocol/client factory.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.embedding_client.
الحد المعماري: Ollama مزود model فقط؛ لا يمنح النص صلاحية policy أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import httpx

from app.capabilities.analysis.retrieval.embedding_client import EmbeddingClient


class OllamaEmbeddingClient(EmbeddingClient):
    """
    يمثل OllamaEmbeddingClient مسؤولية محددة داخل طبقة LLM infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities عبر protocol/client factory
    ويعتمد على EmbeddingClient وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, *, base_url: str, model: str, dimensions: int, timeout_seconds: float = 60.0) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: base_url، model، dimensions، timeout_seconds.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى provider_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return "ollama"

    @property
    def model_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى model_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._model

    @property
    def dimensions(self) -> int:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى dimensions؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._dimensions

    async def embed(self, text: str) -> list[float]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى embed؛ المدخلات المهمة: text.
        تعيد list[float] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
