"""Class extracted from diagnostic_tools during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import ipaddress

import re

import shlex

from types import MappingProxyType

from typing import Any, Mapping

class DiagnosticParameterKind(StrEnum):
    """
    أنواع المعاملات التي يمكن التحقق منها قبل بناء أمر التشخيص.
    """
    SERVICE = "service"
    INTEGER = "integer"
    PORT = "port"
    HOST = "host"
    PATH = "path"
    TEXT_TOKEN = "text_token"
