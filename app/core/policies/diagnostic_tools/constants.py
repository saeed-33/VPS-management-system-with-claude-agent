"""
تعريف أدوات التشخيص الآمنة ومعاملاتها وقائمة الأدوات المتاحة.

تصف الأداة أمر القراءة ومعاملاته وحدود الوقت والمخرجات، وتتحقق من القيم قبل
تحويلها إلى أمر مضبوط لا يقبل نص shell حرًا.
"""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import ipaddress

import re

import shlex

from types import MappingProxyType

from typing import Any, Mapping

_SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9_.@:-]+$")

_SAFE_PATH_RE = re.compile(r"^/[A-Za-z0-9_./@:+-]+$")
