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


class DiagnosticToolRisk(StrEnum):
    READ_ONLY = "read_only"


class DiagnosticParameterKind(StrEnum):
    SERVICE = "service"
    INTEGER = "integer"
    PORT = "port"
    HOST = "host"
    PATH = "path"
    TEXT_TOKEN = "text_token"


@dataclass(slots=True, frozen=True)
class DiagnosticToolParameter:
    name: str
    kind: DiagnosticParameterKind
    required: bool = True
    default: Any = None
    minimum: int | None = None
    maximum: int | None = None
    description: str | None = None

    def validate(self, value: Any) -> Any:
        if value is None:
            if self.required and self.default is None:
                raise ValueError(
                    f"Missing required parameter: {self.name}"
                )
            return self.default

        if self.kind == DiagnosticParameterKind.INTEGER:
            if isinstance(value, bool):
                raise ValueError(
                    f"{self.name} must be an integer."
                )
            try:
                normalized = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{self.name} must be an integer."
                ) from exc

            if (
                self.minimum is not None
                and normalized < self.minimum
            ):
                raise ValueError(
                    f"{self.name} must be >= {self.minimum}."
                )

            if (
                self.maximum is not None
                and normalized > self.maximum
            ):
                raise ValueError(
                    f"{self.name} must be <= {self.maximum}."
                )

            return normalized

        if self.kind == DiagnosticParameterKind.PORT:
            try:
                port = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{self.name} must be a TCP/UDP port."
                ) from exc

            if not 1 <= port <= 65535:
                raise ValueError(
                    f"{self.name} must be between 1 and 65535."
                )

            return port

        if not isinstance(value, str):
            raise ValueError(
                f"{self.name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{self.name} must not be empty."
            )

        if self.kind == DiagnosticParameterKind.SERVICE:
            if not _SAFE_NAME_RE.fullmatch(normalized):
                raise ValueError(
                    f"Unsafe service name: {normalized!r}"
                )
            return normalized

        if self.kind == DiagnosticParameterKind.TEXT_TOKEN:
            if not _SAFE_NAME_RE.fullmatch(normalized):
                raise ValueError(
                    f"Unsafe token: {normalized!r}"
                )
            return normalized

        if self.kind == DiagnosticParameterKind.PATH:
            if not _SAFE_PATH_RE.fullmatch(normalized):
                raise ValueError(
                    f"Unsafe absolute path: {normalized!r}"
                )
            if ".." in normalized.split("/"):
                raise ValueError(
                    "Path traversal is not allowed."
                )
            return normalized

        if self.kind == DiagnosticParameterKind.HOST:
            try:
                ipaddress.ip_address(normalized)
                return normalized
            except ValueError:
                pass

            if (
                len(normalized) > 253
                or not re.fullmatch(
                    r"[A-Za-z0-9.-]+",
                    normalized,
                )
            ):
                raise ValueError(
                    f"Unsafe host value: {normalized!r}"
                )

            return normalized.casefold()

        raise ValueError(
            f"Unsupported parameter kind: {self.kind}"
        )


@dataclass(slots=True, frozen=True)
class DiagnosticToolDefinition:
    tool_id: str
    name: str
    description: str
    domains: tuple[str, ...]
    parameters: tuple[DiagnosticToolParameter, ...]
    command_template: tuple[str, ...]
    timeout_seconds: float
    requires_sudo: bool = False
    risk: DiagnosticToolRisk = DiagnosticToolRisk.READ_ONLY
    output_limit_chars: int = 20_000
    metadata: Mapping[str, Any] = MappingProxyType({})

    def render_command(
        self,
        arguments: Mapping[str, Any] | None = None,
    ) -> str:
        raw = dict(arguments or {})
        known = {
            item.name
            for item in self.parameters
        }

        unknown = set(raw) - known

        if unknown:
            raise ValueError(
                "Unknown tool parameters: "
                + ", ".join(sorted(unknown))
            )

        values: dict[str, Any] = {}

        for parameter in self.parameters:
            values[parameter.name] = parameter.validate(
                raw.get(parameter.name)
            )

        tokens: list[str] = []

        if self.requires_sudo:
            tokens.extend(
                ["sudo", "-n"]
            )

        for token in self.command_template:
            if (
                token.startswith("{")
                and token.endswith("}")
            ):
                key = token[1:-1]

                if key not in values:
                    raise ValueError(
                        f"Unknown command placeholder: {key}"
                    )

                value = values[key]

                if value is None:
                    continue

                tokens.append(str(value))
            else:
                tokens.append(token)

        return shlex.join(tokens)


@dataclass(slots=True, frozen=True)
class DiagnosticToolCall:
    tool_id: str
    arguments: Mapping[str, Any]


class DiagnosticToolRegistry:
    def __init__(
        self,
        definitions: tuple[
            DiagnosticToolDefinition,
            ...
        ],
    ) -> None:
        by_id: dict[
            str,
            DiagnosticToolDefinition,
        ] = {}

        for definition in definitions:
            tool_id = (
                definition.tool_id
                .strip()
                .casefold()
            )

            if not tool_id:
                raise ValueError(
                    "Diagnostic tool ID must not be empty."
                )

            if tool_id in by_id:
                raise ValueError(
                    f"Duplicate diagnostic tool ID: {tool_id}"
                )

            if definition.timeout_seconds <= 0:
                raise ValueError(
                    f"{tool_id}: timeout_seconds must be > 0."
                )

            if definition.output_limit_chars < 100:
                raise ValueError(
                    f"{tool_id}: output_limit_chars must be >= 100."
                )

            by_id[tool_id] = definition

        self._definitions = tuple(
            sorted(
                by_id.values(),
                key=lambda item: item.tool_id,
            )
        )
        self._by_id = MappingProxyType(
            by_id
        )

    @property
    def definitions(
        self,
    ) -> tuple[
        DiagnosticToolDefinition,
        ...
    ]:
        return self._definitions

    def get(
        self,
        tool_id: str,
    ) -> DiagnosticToolDefinition | None:
        return self._by_id.get(
            tool_id.strip().casefold()
        )

    def require(
        self,
        tool_id: str,
    ) -> DiagnosticToolDefinition:
        definition = self.get(tool_id)

        if definition is None:
            raise LookupError(
                f"Unknown diagnostic tool: {tool_id}"
            )

        return definition

    def allowed_for_specialist(
        self,
        allowed_tool_ids: tuple[str, ...],
    ) -> tuple[
        DiagnosticToolDefinition,
        ...
    ]:
        result = []

        for tool_id in allowed_tool_ids:
            definition = self.require(
                tool_id
            )

            if definition not in result:
                result.append(definition)

        return tuple(result)

    def render_call(
        self,
        call: DiagnosticToolCall,
        *,
        allowed_tool_ids: tuple[str, ...],
    ) -> str:
        allowed = {
            value.strip().casefold()
            for value in allowed_tool_ids
            if value.strip()
        }

        normalized_id = (
            call.tool_id
            .strip()
            .casefold()
        )

        if normalized_id not in allowed:
            raise PermissionError(
                f"Tool is not allowed for this Specialist: "
                f"{normalized_id}"
            )

        return self.require(
            normalized_id
        ).render_command(
            call.arguments
        )


def build_default_diagnostic_tool_registry() -> DiagnosticToolRegistry:
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
