"""
جزء من Retrieval/RAG لتطبيع report أو استرجاع context أو الفهرسة.

الموقع في المعمارية: Application capability / retrieval.
يُستدعى بواسطة: Analysis orchestrator وخدمات الفهرسة.
يعتمد مباشرة على: app.core.contracts.reports، app.core.policies.fingerprint_strategy.
الحد المعماري: ينتهي عند context مع provenance؛ reasoning مسؤولية أعلى.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import hashlib
import json
import re
from typing import Any

from app.core.contracts.reports import (
    ReportDetailsDTO,
)
from app.core.policies.fingerprint_strategy import (
    FingerprintStrategy,
)


class ReportNormalizer:
    """
    يمثل ReportNormalizer مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    _MULTIPLE_SPACES = re.compile(r"[ \t]+")
    _MULTIPLE_EMPTY_LINES = re.compile(r"\n{3,}")

    _ANSI_ESCAPE = re.compile(
        r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
    )

    _ISO_TIMESTAMP = re.compile(
        r"\b"
        r"\d{4}-\d{2}-\d{2}"
        r"[T ]"
        r"\d{2}:\d{2}:\d{2}"
        r"(?:\.\d+)?"
        r"(?:Z|[+-]\d{2}:\d{2})?"
        r"\b"
    )

    def normalize(
        self,
        report: ReportDetailsDTO,
    ) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى normalize؛ المدخلات المهمة: report.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        payload: dict[str, Any] = {
            "server_id": report.server_id,
            "monitoring_profile_id": (
                report.monitoring_profile_id
            ),
            "command_set_hash": self.command_set_hash(
                report
            ),
            "status": self._enum_value(
                report.status
            ),
            "connection_successful": (
                report.connection_successful
            ),
            "error_message": self._normalize_error(
                report.error_message or ""
            ),
            "commands_total": report.commands_total,
            "commands_succeeded": (
                report.commands_succeeded
            ),
            "commands_failed": (
                report.commands_failed
            ),
            "executions": [
                self._normalize_execution(execution)
                for execution in sorted(
                    report.executions,
                    key=lambda item: (
                        item.execution_order,
                        item.command_id or 0,
                    ),
                )
            ],
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def command_set_hash(
        self,
        report: ReportDetailsDTO,
    ) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى command_set_hash؛ المدخلات المهمة: report.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        command_set = [
            {
                "command_id": execution.command_id,
                "command_name": self._normalize_text(
                    execution.command_name
                ),
                "command_text": self._normalize_text(
                    execution.command_text
                ),
                "execution_order": execution.execution_order,
            }
            for execution in sorted(
                report.executions,
                key=lambda item: (
                    item.execution_order,
                    item.command_id or 0,
                ),
            )
        ]

        canonical = json.dumps(
            command_set,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

    def _normalize_execution(
        self,
        execution,
    ) -> dict[str, Any]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _normalize_execution؛ المدخلات المهمة: execution.
        تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        strategy = FingerprintStrategy(
            execution.fingerprint_strategy
        )

        result: dict[str, Any] = {
            "command_id": execution.command_id,
            "command_name": self._normalize_text(
                execution.command_name
            ),
            "command_text": self._normalize_text(
                execution.command_text
            ),
            "execution_order": (
                execution.execution_order
            ),
            "success": execution.success,
            "exit_status": execution.exit_status,
            "strategy": strategy.value,
            "error_message": self._normalize_error(
                execution.error_message or ""
            ),
        }

        if strategy == FingerprintStrategy.STATUS_ONLY:
            return result

        if strategy == FingerprintStrategy.EXCLUDE_OUTPUT:
            return result

        if strategy == FingerprintStrategy.CANONICAL_LINES:
            result["stdout"] = self._canonicalize_lines(
                execution.stdout or ""
            )
            result["stderr"] = self._canonicalize_lines(
                execution.stderr or ""
            )
            return result

        if strategy == FingerprintStrategy.ERROR_SIGNATURE:
            result["stdout"] = self._error_signature(
                execution.stdout or "",
                execution.fingerprint_config,
            )
            result["stderr"] = self._error_signature(
                execution.stderr or "",
                execution.fingerprint_config,
            )
            return result

        result["stdout"] = self._normalize_text(
            execution.stdout or ""
        )
        result["stderr"] = self._normalize_text(
            execution.stderr or ""
        )

        return result

    def _canonicalize_lines(
        self,
        value: str,
    ) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _canonicalize_lines؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        normalized_lines = {
            self._normalize_text(line)
            for line in value.splitlines()
            if self._normalize_text(line)
        }

        return "\n".join(
            sorted(normalized_lines)
        )

    def _error_signature(
        self,
        value: str,
        config: dict,
    ) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _error_signature؛ المدخلات المهمة: value، config.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        normalized = self._normalize_text(value)

        remove_timestamps = config.get(
            "remove_timestamps",
            True,
        )

        if remove_timestamps:
            normalized = self._ISO_TIMESTAMP.sub(
                "[TIMESTAMP]",
                normalized,
            )

        return normalized

    def _normalize_error(
        self,
        value: str,
    ) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _normalize_error؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        normalized = self._normalize_text(value)

        return self._ISO_TIMESTAMP.sub(
            "[TIMESTAMP]",
            normalized,
        )

    def _normalize_text(
        self,
        value: str,
    ) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _normalize_text؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        value = value.replace(
            "\r\n",
            "\n",
        ).replace(
            "\r",
            "\n",
        )

        value = self._ANSI_ESCAPE.sub(
            "",
            value,
        )

        lines = [
            self._MULTIPLE_SPACES.sub(
                " ",
                line,
            ).strip()
            for line in value.splitlines()
        ]

        normalized = "\n".join(lines).strip()

        return self._MULTIPLE_EMPTY_LINES.sub(
            "\n\n",
            normalized,
        )

    @staticmethod
    def _enum_value(value: Any) -> Any:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _enum_value؛ المدخلات المهمة: value.
        تعيد Any أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return getattr(value, "value", value)