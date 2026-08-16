"""مصدر إعدادات التطبيق وقواعد صلاحية تشغيله.

تجمع `Settings` إعدادات قاعدة البيانات وSSH وLLM وRAG والمراقبة والمعالجة،
وتتحقق من أن التركيبات غير الآمنة لا تسمح للتطبيق بالبدء بحالة مضللة أو خطرة."""
from pathlib import Path
from typing import Literal
from pydantic import Field, model_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from sqlalchemy import URL


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """
    يمثل الإعدادات التي تحكم رحلة المراقبة والتحليل والمعالجة في بيئة التشغيل.

    لا تكتفي هذه البيانات بتوفير القيم؛ فالمراجعات اللاحقة تمنع تفعيل RAG أو
    runtime أو المعالجة الذاتية عندما تكون شروط السلامة والاعتماد غير مكتملة.
    """
    llm_enabled: bool = False

    rag_exact_reuse_enabled: bool = True

    llm_provider: Literal["ollama"] = "ollama"

    llm_analysis_timeout_seconds: float = Field(
        default=120.0,
        gt=0,
    )

    llm_max_report_characters: int = Field(
        default=50_000,
        ge=1_000,
    )


    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:8b"

    # إعدادات تشغيل جلسة Claude الفعلية.
    claude_runtime_enabled: bool = False
    claude_runtime_model: str | None = None
    claude_runtime_timeout_seconds: float = Field(
        default=300.0,
        gt=0,
    )
    claude_runtime_max_turns: int = Field(
        default=20,
        ge=1,
        le=100,
    )
    claude_runtime_ollama_executable: str = "ollama"
    claude_runtime_executable: str = "claude"
    claude_runtime_agent: Literal[
        "server-supervisor",
    ] = "server-supervisor"

    # قبول اختبارات المعالجة الفعلية يحتاج اختيارًا صريحًا من إعدادين؛ تبقى
    # القيم غير مؤثرة ما لم يطلب المستخدم اختبار الأثر عمدًا.
    real_phase5_acceptance_enabled: bool = False
    automatic_remediation_allowed: bool = False
    autonomous_remediation_max_risk: Literal["low"] = "low"
    autonomous_remediation_hard_allowed_actions: str = "start_service"
    safe_remediation_server_id: int | None = None
    safe_remediation_server_name: str = ""
    safe_remediation_service: str = ""
    phase6_native_sandbox_attestation_file: Path | None = None
    phase6_require_wsl2: bool = True

    app_name: str = "AI VPS Management"
    # القيمة الافتراضية آمنة للإنتاج، ويمكن للتطوير المحلي تفعيل التصحيح صراحة.
    debug: bool = False

    postgres_host: str = "127.0.0.1"

    postgres_port: int = Field(
        default=5432,
        ge=1,
        le=65535,
    )

    postgres_db: str
    postgres_user: str
    postgres_password: str

    default_ssh_private_key_path: Path
    ssh_known_hosts_path: Path
    monitor_polling_interval_seconds: float = Field(
        default=5.0,
        gt=0,
    )

    default_monitor_interval_seconds: int = Field(
        default=60,
        ge=5,
    )

    rag_vector_enabled: bool = True
    rag_assisted_enabled: bool = True
    rag_structured_compatibility_enabled: bool = True
    rag_full_text_enabled: bool = True
    rag_full_text_candidate_limit: int = Field(
        default=20,
        ge=1,
        le=200,
    )
    rag_full_text_minimum_rank: float = Field(
        default=0.0,
        ge=0.0,
    )
    rag_minimum_similarity: float = Field(
        default=0.72,
        ge=0.0,
        le=1.0,
    )
    rag_context_top_k: int = Field(default=3, ge=1, le=10)
    rag_rrf_k: int = Field(default=60, ge=1, le=1000)
    rag_hnsw_ef_search: int = Field(
        default=100,
        ge=10,
        le=2000,
    )
    embedding_provider: Literal["ollama"] = "ollama"
    ollama_embedding_model: str = "nomic-embed-text"
    embedding_dimensions: int = Field(default=768, ge=1)
    embedding_timeout_seconds: float = Field(default=60.0, gt=0)
    rag_top_k: int = Field(default=5, ge=1, le=50)
    pdf_font_path: Path = (
        PROJECT_ROOT / "assets" / "fonts" / "NotoNaskhArabic-Regular.ttf"
    )

    command_timeout_seconds: float = Field(
        default=20.0,
        gt=0,
    )

    ssh_connect_timeout_seconds: float = Field(
        default=15.0,
        gt=0,
    )

    max_concurrent_servers: int = Field(
        default=5,
        ge=1,
        le=100,
    )

    database_echo: bool = False

    # مصادقة الإدارة مستقلة عن جلسة Claude وأدوات MCP. السر الفارغ يجعل
    # الجلسات مؤقتة وتنتهي بعد إعادة التشغيل، لذلك يضبط النشر سرًا ثابتًا.
    admin_session_secret: str = ""
    admin_session_cookie_name: str = "admin_session"
    admin_session_ttl_seconds: int = Field(
        default=8 * 60 * 60,
        ge=300,
    )
    admin_session_secure: bool = False

    @model_validator(mode="after")
    def validate_rag_policy(self) -> "Settings":
        """
        يتحقق من أن إعدادات استرجاع المعرفة يمكنها إنتاج سياق موثوق للتحليل.

        يضمن أن البحث المساعد يمر عبر البحث الدلالي، وأن حجم السياق لا يتجاوز
        مجموعة المرشحين المؤهلين قبل وصولها إلى النموذج.
        """
        if (
            self.rag_assisted_enabled
            and not self.rag_vector_enabled
        ):
            raise ValueError(
                "RAG_ASSISTED_ENABLED requires "
                "RAG_VECTOR_ENABLED because historical "
                "context must pass semantic similarity."
            )

        if (
            self.rag_full_text_enabled
            and not self.rag_vector_enabled
        ):
            raise ValueError(
                "RAG_FULL_TEXT_ENABLED currently requires "
                "RAG_VECTOR_ENABLED because both use the "
                "retrieval-document indexing pipeline."
            )

        if (
            self.rag_assisted_enabled
            and self.rag_context_top_k > self.rag_top_k
        ):
            raise ValueError(
                "RAG_CONTEXT_TOP_K must be less than or "
                "equal to RAG_TOP_K because only "
                "vector-qualified candidates may enter "
                "the LLM context."
            )

        return self

    @model_validator(mode="after")
    def validate_admin_deployment_security(self) -> "Settings":
        """
        يمنع تشغيل الإدارة في بيئة الإنتاج بإعداد جلسة ضعيف أو غير آمن.

        يسمح بإعدادات التطوير المرنة، لكنه يفرض سرًا ثابتًا وcookie آمنة عند
        تعطيل وضع التصحيح حتى لا يمكن انتحال جلسة المدير.
        """
        secret = self.admin_session_secret.strip()

        if self.debug:
            if secret and len(secret) < 32:
                raise ValueError(
                    "ADMIN_SESSION_SECRET must be at least 32 characters when provided."
                )
            return self

        if len(secret) < 32:
            raise ValueError(
                "Production requires ADMIN_SESSION_SECRET with at least 32 characters."
            )

        if not self.admin_session_secure:
            raise ValueError(
                "Production requires ADMIN_SESSION_SECURE=true behind HTTPS."
            )

        return self

    @model_validator(mode="after")
    def validate_claude_runtime(self) -> "Settings":
        """
        يتحقق من شروط تشغيل Claude قبل بدء دورة مراقبة فعلية.

        يربط تفعيل runtime بتفعيل LLM ومزود Ollama ونموذج صالح، حتى لا تبدأ
        الجدولة بمشغل لا يستطيع تنفيذ الأدوات المطلوبة.
        """
        if not self.claude_runtime_enabled:
            return self

        if not self.llm_enabled:
            raise ValueError(
                "CLAUDE_RUNTIME_ENABLED requires LLM_ENABLED."
            )

        if self.llm_provider != "ollama":
            raise ValueError(
                "CLAUDE_RUNTIME_ENABLED requires LLM_PROVIDER=ollama."
            )

        if not self.effective_claude_runtime_model:
            raise ValueError(
                "Claude runtime model must not be empty."
            )

        if not self.claude_runtime_ollama_executable.strip():
            raise ValueError(
                "CLAUDE_RUNTIME_OLLAMA_EXECUTABLE must not be empty."
            )

        return self

    @property
    def effective_claude_runtime_model(self) -> str:
        """يعيد نموذج runtime الصريح أو نموذج Ollama الافتراضي عند غيابه."""
        configured = (
            self.claude_runtime_model or ""
        ).strip()

        if configured:
            return configured

        return self.ollama_model.strip()

    @property
    def rag_retrieval_enabled(self) -> bool:
        """يحدد هل يوجد مسار بحث واحد على الأقل يمكنه تزويد التحليل بسياق سابق."""
        return (
            self.rag_vector_enabled
            or self.rag_full_text_enabled
        )

    @property
    def rag_candidate_budget(self) -> int:
        """يحسب الحد المجمع للمرشحين الذين قد تدخلهم سياسة الاسترجاع للمقارنة."""
        total = 0

        if self.rag_vector_enabled:
            total += self.rag_top_k

        if self.rag_full_text_enabled:
            total += self.rag_full_text_candidate_limit

        return total

    @property
    def rag_policy_summary(self) -> dict[str, object]:
        """يعرض إعدادات RAG الفعالة في شكل مناسب للسجل وفحص الحالة."""
        return {
            "exact_reuse": self.rag_exact_reuse_enabled,
            "assisted": self.rag_assisted_enabled,
            "vector": self.rag_vector_enabled,
            "full_text": self.rag_full_text_enabled,
            "structured_compatibility": (
                self.rag_structured_compatibility_enabled
            ),
            "minimum_similarity": (
                self.rag_minimum_similarity
            ),
            "vector_candidate_limit": self.rag_top_k,
            "full_text_candidate_limit": (
                self.rag_full_text_candidate_limit
            ),
            "context_top_k": self.rag_context_top_k,
            "rrf_k": self.rag_rrf_k,
            "hnsw_ef_search": self.rag_hnsw_ef_search,
            "candidate_budget": self.rag_candidate_budget,
        }

    @property
    def database_url(self) -> URL:
        """يبني عنوان اتصال PostgreSQL من أجزاء إعدادات قاعدة البيانات."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
