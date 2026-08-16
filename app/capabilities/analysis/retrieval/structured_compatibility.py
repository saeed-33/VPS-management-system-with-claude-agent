"""
جزء من Retrieval/RAG لتطبيع report أو استرجاع context أو الفهرسة.

الموقع في المعمارية: Application capability / retrieval.
يُستدعى بواسطة: Analysis orchestrator وخدمات الفهرسة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: ينتهي عند context مع provenance؛ reasoning مسؤولية أعلى.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class CompatibilityConflict:
    """
    يمثل CompatibilityConflict مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    field: str
    current: Any
    historical: Any
    command_id: int | None = None


@dataclass(slots=True, frozen=True)
class CompatibilityResult:
    """
    يمثل CompatibilityResult مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    compatible: bool
    conflicts: list[CompatibilityConflict] = field(
        default_factory=list
    )


class StructuredCompatibilityChecker:
    """
    يمثل StructuredCompatibilityChecker مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def check(
        self,
        *,
        current_normalized_report: str,
        historical_normalized_report: str,
    ) -> CompatibilityResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى check؛ المدخلات المهمة: current_normalized_report، historical_normalized_report.
        تعيد CompatibilityResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        current = self._parse(current_normalized_report)
        historical = self._parse(historical_normalized_report)

        if current is None or historical is None:
            return CompatibilityResult(
                compatible=False,
                conflicts=[
                    CompatibilityConflict(
                        field="normalized_report",
                        current="valid" if current is not None else "invalid",
                        historical=(
                            "valid" if historical is not None else "invalid"
                        ),
                    )
                ],
            )

        conflicts: list[CompatibilityConflict] = []

        self._compare_scalar(
            conflicts,
            field_name="connection_successful",
            current=current.get("connection_successful"),
            historical=historical.get("connection_successful"),
        )

        current_exec = self._execution_map(current)
        historical_exec = self._execution_map(historical)

        for command_id in sorted(
            current_exec.keys() & historical_exec.keys()
        ):
            current_item = current_exec[command_id]
            historical_item = historical_exec[command_id]

            self._compare_scalar(
                conflicts,
                field_name="success",
                current=current_item.get("success"),
                historical=historical_item.get("success"),
                command_id=command_id,
            )

            current_exit = current_item.get("exit_status")
            historical_exit = historical_item.get("exit_status")

            if (
                current_exit is not None
                and historical_exit is not None
                and self._exit_class(current_exit)
                != self._exit_class(historical_exit)
            ):
                conflicts.append(
                    CompatibilityConflict(
                        field="exit_status_class",
                        current=current_exit,
                        historical=historical_exit,
                        command_id=command_id,
                    )
                )

        current_errors = self._error_signatures(current)
        historical_errors = self._error_signatures(historical)

        if (
            current_errors
            and historical_errors
            and current_errors.isdisjoint(historical_errors)
        ):
            conflicts.append(
                CompatibilityConflict(
                    field="error_signatures",
                    current=sorted(current_errors),
                    historical=sorted(historical_errors),
                )
            )

        return CompatibilityResult(
            compatible=not conflicts,
            conflicts=conflicts,
        )

    @staticmethod
    def _parse(value: str) -> dict | None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _parse؛ المدخلات المهمة: value.
        تعيد dict | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return None

        return parsed if isinstance(parsed, dict) else None

    @staticmethod
    def _compare_scalar(
        conflicts: list[CompatibilityConflict],
        *,
        field_name: str,
        current: Any,
        historical: Any,
        command_id: int | None = None,
    ) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _compare_scalar؛ المدخلات المهمة: conflicts، field_name، current، historical، command_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if current is None or historical is None:
            return

        if current != historical:
            conflicts.append(
                CompatibilityConflict(
                    field=field_name,
                    current=current,
                    historical=historical,
                    command_id=command_id,
                )
            )

    @staticmethod
    def _execution_map(payload: dict) -> dict[int, dict]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _execution_map؛ المدخلات المهمة: payload.
        تعيد dict[int, dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        result: dict[int, dict] = {}

        for execution in payload.get("executions", []):
            if not isinstance(execution, dict):
                continue

            command_id = execution.get("command_id")
            if isinstance(command_id, int):
                result[command_id] = execution

        return result

    @staticmethod
    def _exit_class(value: Any) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _exit_class؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            return str(value)

        return "success" if numeric == 0 else "failure"

    @staticmethod
    def _error_signatures(payload: dict) -> set[str]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _error_signatures؛ المدخلات المهمة: payload.
        تعيد set[str] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        signatures: set[str] = set()

        report_error = payload.get("error_message")
        if isinstance(report_error, str) and report_error.strip():
            signatures.add(report_error.strip())

        for execution in payload.get("executions", []):
            if not isinstance(execution, dict):
                continue

            for field_name in ("error_message", "stderr"):
                value = execution.get(field_name)
                if isinstance(value, str) and value.strip():
                    signatures.add(value.strip())

        return signatures
