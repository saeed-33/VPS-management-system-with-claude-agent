"""
جزء من Knowledge ingestion/indexing/retrieval لتغذية RAG بمصادر قابلة للتتبع.

الموقع في المعمارية: Application capability / knowledge.
يُستدعى بواسطة: أدوات الإدارة أو Retrieval.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يخلط knowledge retrieval مع reasoning.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum

class KnowledgeDocumentStatus(StrEnum):
    """
    يمثل KnowledgeDocumentStatus مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على StrEnum وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    PENDING = "pending"
    FETCHED = "fetched"
    PARSED = "parsed"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    FAILED = "failed"

@dataclass(slots=True, frozen=True)
class ParsedKnowledgeDocument:
    """
    يمثل ParsedKnowledgeDocument مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    canonical_uri: str
    title: str | None
    media_type: str | None
    text: str
    page_count: int | None = None
    parser_name: str | None = None
    parser_version: str | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self.canonical_uri.strip():
            raise ValueError("canonical_uri must not be empty.")
        if not self.text.strip():
            raise ValueError("Parsed document text must not be empty.")
        if self.page_count is not None and self.page_count < 1:
            raise ValueError("page_count must be >= 1 when provided.")

@dataclass(slots=True, frozen=True)
class KnowledgeChunkDraft:
    """
    يمثل KnowledgeChunkDraft مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    chunk_index: int
    content: str
    section_title: str | None = None
    page_number: int | None = None
    token_count: int | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be >= 0.")
        if not self.content.strip():
            raise ValueError("chunk content must not be empty.")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("page_number must be >= 1 when provided.")
        if self.token_count is not None and self.token_count < 1:
            raise ValueError("token_count must be >= 1 when provided.")
