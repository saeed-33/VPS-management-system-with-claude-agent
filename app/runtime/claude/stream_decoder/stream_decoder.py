"""
قراءة مخرجات Claude بصيغة JSON المفردة أو stream-json.

تستخرج معرف الجلسة والنتيجة والعدادات والأدوات وخوادم MCP، وترفض الجلسة التي
لا تثبت اتصال أداة VPS وتنفيذ الفحوص التشغيلية المطلوبة.
"""
from __future__ import annotations

import json

from app.runtime.claude.exceptions.process_output_error import ClaudeProcessOutputError
from app.runtime.claude.models.raw_result import ClaudeRawResult

from .content_extractor import _ContentExtractorMixin
from .envelope_decoder import _EnvelopeDecoderMixin
from .result_metadata import _ResultMetadataMixin


class ClaudeCliJsonDecoder(_EnvelopeDecoderMixin, _ContentExtractorMixin, _ResultMetadataMixin):
    """
    محلل يتحقق من بنية مخرجات Claude ويستخرج منها دليل تنفيذ دورة VPS التشغيلية.
    """


    _REQUIRED_VPS_TOOLS = frozenset(
        {
            "mcp__vps__run_monitoring",
            "mcp__vps__analyze_report",
        }
    )
