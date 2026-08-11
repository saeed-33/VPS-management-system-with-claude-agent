from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx


@dataclass(slots=True, frozen=True)
class LoadedKnowledgeContent:
    content: bytes
    canonical_uri: str
    media_type: str | None
    title_hint: str | None = None


class KnowledgeSourceLoader:
    def __init__(
        self,
        *,
        timeout_seconds: float = 20.0,
        max_bytes: int = 25 * 1024 * 1024,
        user_agent: str = "chat-system-knowledge-ingestion/1.0",
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0.")
        if max_bytes < 1:
            raise ValueError("max_bytes must be >= 1.")

        self._timeout_seconds = timeout_seconds
        self._max_bytes = max_bytes
        self._user_agent = user_agent

    def load(self, source) -> LoadedKnowledgeContent:
        source_type = str(source.source_type).strip().casefold()

        if source_type == "inline":
            return self._load_inline(source)

        if source_type == "file":
            return self._load_file(source)

        if source_type == "url":
            return self._load_url(source)

        raise ValueError(
            f"Unsupported knowledge source type: {source_type}"
        )

    def _load_inline(self, source) -> LoadedKnowledgeContent:
        content = str(source.inline_content or "").strip()

        if not content:
            raise ValueError(
                "Inline knowledge source has no content."
            )

        return LoadedKnowledgeContent(
            content=content.encode("utf-8"),
            canonical_uri=f"inline://knowledge-source/{source.slug}",
            media_type="text/plain",
            title_hint=source.name,
        )

    def _load_file(self, source) -> LoadedKnowledgeContent:
        raw_uri = str(source.source_uri or "").strip()

        if not raw_uri:
            raise ValueError(
                "File knowledge source has no source_uri."
            )

        parsed = urlparse(raw_uri)

        if parsed.scheme == "file":
            path = Path(parsed.path)
        else:
            path = Path(raw_uri)

        path = path.expanduser().resolve()

        if not path.is_file():
            raise FileNotFoundError(
                f"Knowledge source file not found: {path}"
            )

        size = path.stat().st_size

        if size > self._max_bytes:
            raise ValueError(
                f"Knowledge source exceeds max_bytes: {size} > {self._max_bytes}"
            )

        return LoadedKnowledgeContent(
            content=path.read_bytes(),
            canonical_uri=path.as_uri(),
            media_type=self._media_type_for_suffix(path.suffix),
            title_hint=path.name,
        )

    def _load_url(self, source) -> LoadedKnowledgeContent:
        url = str(source.source_uri or "").strip()

        if not url:
            raise ValueError(
                "URL knowledge source has no source_uri."
            )

        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "Knowledge URL must use http or https."
            )

        with httpx.Client(
            timeout=self._timeout_seconds,
            follow_redirects=True,
            headers={
                "User-Agent": self._user_agent,
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/pdf,text/plain,text/markdown;q=0.9,*/*;q=0.1"
                ),
            },
        ) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()

                chunks: list[bytes] = []
                total = 0

                for chunk in response.iter_bytes():
                    total += len(chunk)

                    if total > self._max_bytes:
                        raise ValueError(
                            "Knowledge URL response exceeds max_bytes."
                        )

                    chunks.append(chunk)

                content = b"".join(chunks)

                return LoadedKnowledgeContent(
                    content=content,
                    canonical_uri=str(response.url),
                    media_type=response.headers.get("content-type"),
                    title_hint=source.name,
                )

    @staticmethod
    def _media_type_for_suffix(
        suffix: str,
    ) -> str | None:
        return {
            ".pdf": "application/pdf",
            ".html": "text/html",
            ".htm": "text/html",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".markdown": "text/markdown",
        }.get(suffix.casefold())
