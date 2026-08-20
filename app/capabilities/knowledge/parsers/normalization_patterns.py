"""أنماط تطبيع النص."""
from __future__ import annotations
import re
_SPACE_RE = re.compile(r"[ \t]+")
_BLANKS_RE = re.compile(r"\n{3,}")
