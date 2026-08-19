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

from .diagnostic_parameter_kind import DiagnosticParameterKind

from .diagnostic_tool_definition import DiagnosticToolDefinition

from .diagnostic_tool_parameter import DiagnosticToolParameter

from .diagnostic_tool_registry import DiagnosticToolRegistry

def build_default_diagnostic_tool_registry() -> DiagnosticToolRegistry:
    """
    ينشئ سجل أدوات القراءة القياسية لفحص الخدمات والموارد والشبكة وقواعد البيانات.
    """
    service = DiagnosticToolParameter(
        name="service",
        kind=DiagnosticParameterKind.SERVICE,
        description="systemd unit name, e.g. nginx or ssh",
    )

    lines = DiagnosticToolParameter(
        name="lines",
        kind=DiagnosticParameterKind.INTEGER,
        required=False,
        default=120,
        minimum=10,
        maximum=500,
    )

    host = DiagnosticToolParameter(
        name="host",
        kind=DiagnosticParameterKind.HOST,
    )

    port = DiagnosticToolParameter(
        name="port",
        kind=DiagnosticParameterKind.PORT,
    )

    path = DiagnosticToolParameter(
        name="path",
        kind=DiagnosticParameterKind.PATH,
    )

    definitions = (
        DiagnosticToolDefinition(
            tool_id="systemd-status",
            name="Systemd Unit Status",
            description=(
                "Read current systemd unit status without paging."
            ),
            domains=("systemd", "service", "process"),
            parameters=(service,),
            command_template=(
                "systemctl",
                "--no-pager",
                "--full",
                "status",
                "{service}",
            ),
            timeout_seconds=12,
        ),
        DiagnosticToolDefinition(
            tool_id="systemd-failed",
            name="Failed Systemd Units",
            description="List failed systemd units.",
            domains=("systemd", "service"),
            parameters=(),
            command_template=(
                "systemctl",
                "--failed",
                "--no-pager",
                "--plain",
            ),
            timeout_seconds=10,
        ),
        DiagnosticToolDefinition(
            tool_id="journal-unit",
            name="Unit Journal",
            description=(
                "Read recent journal entries for one systemd unit."
            ),
            domains=("systemd", "service", "journal"),
            parameters=(service, lines),
            command_template=(
                "journalctl",
                "--no-pager",
                "--output=short-iso",
                "-u",
                "{service}",
                "-n",
                "{lines}",
            ),
            timeout_seconds=15,
        ),
        DiagnosticToolDefinition(
            tool_id="process-top-cpu",
            name="Top CPU Processes",
            description="Read processes ordered by CPU consumption.",
            domains=("cpu", "process", "performance"),
            parameters=(),
            command_template=(
                "ps",
                "-eo",
                "pid,ppid,user,stat,comm,%cpu,%mem,etime",
                "--sort=-%cpu",
            ),
            timeout_seconds=10,
            output_limit_chars=12_000,
        ),
        DiagnosticToolDefinition(
            tool_id="process-top-memory",
            name="Top Memory Processes",
            description="Read processes ordered by memory consumption.",
            domains=("memory", "process", "performance"),
            parameters=(),
            command_template=(
                "ps",
                "-eo",
                "pid,ppid,user,stat,comm,%cpu,%mem,rss,vsz,etime",
                "--sort=-%mem",
            ),
            timeout_seconds=10,
            output_limit_chars=12_000,
        ),
        DiagnosticToolDefinition(
            tool_id="memory-summary",
            name="Memory Summary",
            description="Read system memory and swap totals.",
            domains=("memory", "swap"),
            parameters=(),
            command_template=(
                "free",
                "-m",
            ),
            timeout_seconds=8,
        ),
        DiagnosticToolDefinition(
            tool_id="vmstat-sample",
            name="VMStat Sample",
            description=(
                "Read a short CPU, run queue, memory, swap and I/O sample."
            ),
            domains=(
                "cpu",
                "memory",
                "swap",
                "io",
                "performance",
            ),
            parameters=(),
            command_template=(
                "vmstat",
                "1",
                "5",
            ),
            timeout_seconds=10,
        ),
        DiagnosticToolDefinition(
            tool_id="disk-filesystems",
            name="Filesystem Usage",
            description="Read mounted filesystem capacity and usage.",
            domains=("disk", "filesystem", "storage"),
            parameters=(),
            command_template=(
                "df",
                "-hT",
            ),
            timeout_seconds=10,
        ),
        DiagnosticToolDefinition(
            tool_id="disk-path",
            name="Path Filesystem Usage",
            description=(
                "Read filesystem capacity for one absolute path."
            ),
            domains=("disk", "filesystem", "storage"),
            parameters=(path,),
            command_template=(
                "df",
                "-hT",
                "{path}",
            ),
            timeout_seconds=10,
        ),
        DiagnosticToolDefinition(
            tool_id="disk-inodes",
            name="Filesystem Inodes",
            description="Read inode consumption.",
            domains=("disk", "filesystem", "inode"),
            parameters=(),
            command_template=(
                "df",
                "-ih",
            ),
            timeout_seconds=10,
        ),
        DiagnosticToolDefinition(
            tool_id="network-listeners",
            name="Network Listeners",
            description=(
                "Read TCP/UDP listening sockets and owning processes."
            ),
            domains=("network", "socket", "connectivity"),
            parameters=(),
            command_template=(
                "ss",
                "-lntup",
            ),
            timeout_seconds=10,
            requires_sudo=False,
        ),
        DiagnosticToolDefinition(
            tool_id="network-sockets",
            name="Network Socket Summary",
            description="Read socket statistics.",
            domains=("network", "socket"),
            parameters=(),
            command_template=(
                "ss",
                "-s",
            ),
            timeout_seconds=8,
        ),
        DiagnosticToolDefinition(
            tool_id="network-route",
            name="IP Routes",
            description="Read kernel IP routing table.",
            domains=("network", "routing", "connectivity"),
            parameters=(),
            command_template=(
                "ip",
                "route",
                "show",
            ),
            timeout_seconds=8,
        ),
        DiagnosticToolDefinition(
            tool_id="network-connect",
            name="TCP Connect Probe",
            description=(
                "Perform a bounded TCP connection probe using netcat."
            ),
            domains=("network", "connectivity", "socket"),
            parameters=(host, port),
            command_template=(
                "nc",
                "-zvw3",
                "{host}",
                "{port}",
            ),
            timeout_seconds=6,
        ),
        DiagnosticToolDefinition(
            tool_id="nginx-config-test",
            name="NGINX Configuration Test",
            description=(
                "Ask nginx to parse and validate configuration only."
            ),
            domains=("nginx", "http", "proxy", "tls"),
            parameters=(),
            command_template=(
                "nginx",
                "-t",
            ),
            timeout_seconds=12,
        ),
        DiagnosticToolDefinition(
            tool_id="nginx-version",
            name="NGINX Build Information",
            description="Read nginx version and build flags.",
            domains=("nginx", "http"),
            parameters=(),
            command_template=(
                "nginx",
                "-V",
            ),
            timeout_seconds=8,
        ),
        DiagnosticToolDefinition(
            tool_id="docker-ps",
            name="Docker Container List",
            description="Read Docker container state.",
            domains=("docker", "container", "runtime"),
            parameters=(),
            command_template=(
                "docker",
                "ps",
                "--no-trunc",
            ),
            timeout_seconds=12,
        ),
        DiagnosticToolDefinition(
            tool_id="postgres-ready",
            name="PostgreSQL Readiness",
            description=(
                "Check PostgreSQL server readiness without changing data."
            ),
            domains=("postgresql", "database", "connectivity"),
            parameters=(),
            command_template=(
                "pg_isready",
            ),
            timeout_seconds=8,
        ),
    )

    return DiagnosticToolRegistry(
        definitions
    )
