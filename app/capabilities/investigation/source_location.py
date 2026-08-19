"""
استخراج مواقع المصادر من نصوص نتائج التحقيق.

تتعرف الدالة على مراجع الملفات والأسطر في النصوص وتعيدها بصيغة موحدة لربط
الادعاءات بمواقع يمكن تدقيقها.
"""
from __future__ import annotations

import re

from app.core.contracts.source_location.source_location import SourceLocation


_SOURCE_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rb",
    ".php",
    ".cs",
)
_PYTHON_FRAME = re.compile(
    r'^\s*File ["\'](?P<path>[^"\']+)["\'], line (?P<line>\d+), in (?P<function>[^\s]+)\s*$',
    re.MULTILINE,
)
_GENERIC_LOCATION = re.compile(
    r'(?P<path>(?:[A-Za-z]:[\\/]|/|\.\.?[\\/])?[^\s:]+'
    r'\.(?:py|js|ts|tsx|jsx|java|go|rb|php|cs))'
    r':(?P<line>\d+)(?::(?P<column>\d+))?',
    re.IGNORECASE,
)
_PYTHON_EXCEPTION = re.compile(
    r'^\s*(?P<type>[A-Za-z_][\w.]*(?:Error|Exception|Interrupt|Warning))'
    r'(?::\s*(?P<message>.*))?\s*$',
    re.MULTILINE,
)
_TRANSPORT_MARKERS = (
    "ssh: connect to host",
    "paramiko",
    "known_hosts",
    "connection refused",
    "connection timed out",
)


def extract_source_locations(
    text: str,
    *,
    evidence_ids: tuple[str, ...] = (),
) -> tuple[SourceLocation, ...]:
    """
    يستخرج مراجع الملفات والأسطر من نص الدليل.
    """
    if not text.strip():
        return ()

    python_frames = list(_PYTHON_FRAME.finditer(text))
    if python_frames:
        frame = python_frames[-1]
        path = frame.group("path")
        exception = list(_PYTHON_EXCEPTION.finditer(text))
        terminal = exception[-1] if exception else None
        exception_type = terminal.group("type") if terminal else None
        message = terminal.group("message").strip() if terminal else ""
        reason = (
            f"{exception_type}: {message}".strip(": ")
            if exception_type
            else "Python traceback frame reported an application error."
        )
        return (
            SourceLocation(
                file_path=path,
                line_number=int(frame.group("line")),
                function=frame.group("function"),
                exception_type=exception_type,
                reason=reason,
                source="python_traceback",
                evidence_ids=tuple(dict.fromkeys(evidence_ids)),
            ),
        )

    lowered = text.casefold()
    if any(marker in lowered for marker in _TRANSPORT_MARKERS):
        return ()

    matches = list(_GENERIC_LOCATION.finditer(text))
    if not matches:
        return ()

    match = matches[-1]
    path = match.group("path")
    if not path.casefold().endswith(_SOURCE_EXTENSIONS):
        return ()

    return (
        SourceLocation(
            file_path=path,
            line_number=int(match.group("line")),
            column_number=(
                int(match.group("column"))
                if match.group("column")
                else None
            ),
            reason="Application source location reported by diagnostic output.",
            source="generic_path_line",
            evidence_ids=tuple(dict.fromkeys(evidence_ids)),
        ),
    )
