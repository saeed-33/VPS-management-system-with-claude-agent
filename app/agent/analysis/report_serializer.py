import re
from typing import Any

from app.shared.dto.reports import (
    ReportDetailsDTO,
)


class ReportSerializer:
    _SENSITIVE_PATTERNS = [
        re.compile(
            r"(?i)"
            r"(password|passwd|token|secret|"
            r"api[_-]?key)"
            r"\s*[=:]\s*"
            r"([^\s\"']+)"
        ),
        re.compile(
            r"(?i)"
            r"(authorization:\s*bearer\s+)"
            r"([^\s]+)"
        ),
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
            r".*?"
            r"-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
    ]

    def __init__(
        self,
        *,
        max_report_characters: int,
        max_execution_characters: int = 12_000,
    ) -> None:
        self._max_report_characters = (
            max_report_characters
        )

        self._max_execution_characters = (
            max_execution_characters
        )

    def serialize(
        self,
        report: ReportDetailsDTO,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "report": {
                "id": report.id,
                "server": {
                    "id": report.server_id,
                    "name": report.server_name,
                    "host": report.server_host,
                },
                "status": report.status,
                "connection_successful": (
                    report.connection_successful
                ),
                "started_at": (
                    report.started_at.isoformat()
                ),
                "finished_at": (
                    report.finished_at.isoformat()
                ),
                "duration_ms": report.duration_ms,
                "commands_total": (
                    report.commands_total
                ),
                "commands_succeeded": (
                    report.commands_succeeded
                ),
                "commands_failed": (
                    report.commands_failed
                ),
                "error_message": self._clean(
                    report.error_message or ""
                ),
            },
            "executions": [
                {
                    "name": execution.command_name,
                    "command": self._clean(
                        execution.command_text
                    ),
                    "success": execution.success,
                    "exit_status": (
                        execution.exit_status
                    ),
                    "stdout": self._prepare_output(
                        execution.stdout
                    ),
                    "stderr": self._prepare_output(
                        execution.stderr
                    ),
                    "error_message": self._clean(
                        execution.error_message or ""
                    ),
                    "duration_ms": (
                        execution.duration_ms
                    ),
                }
                for execution in report.executions
            ],
        }

        return self._limit_complete_payload(
            payload
        )

    def _prepare_output(
        self,
        value: str,
    ) -> str:
        cleaned = self._clean(value)

        if (
            len(cleaned)
            <= self._max_execution_characters
        ):
            return cleaned

        return (
            cleaned[
                :self._max_execution_characters
            ]
            + "\n...[OUTPUT TRUNCATED]"
        )

    def _clean(
        self,
        value: str,
    ) -> str:
        result = value

        for pattern in self._SENSITIVE_PATTERNS:
            result = pattern.sub(
                self._replace_sensitive_match,
                result,
            )

        return result

    @staticmethod
    def _replace_sensitive_match(
        match: re.Match[str],
    ) -> str:
        if match.lastindex:
            return (
                match.group(1)
                + "[REDACTED]"
            )

        return "[PRIVATE KEY REDACTED]"

    def _limit_complete_payload(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        import json

        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )

        if (
            len(serialized)
            <= self._max_report_characters
        ):
            return payload

        executions = payload["executions"]

        while executions:
            executions.pop()

            serialized = json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            )

            if (
                len(serialized)
                <= self._max_report_characters
            ):
                payload["report"][
                    "truncated"
                ] = True

                return payload

        payload["report"]["truncated"] = True

        return payload