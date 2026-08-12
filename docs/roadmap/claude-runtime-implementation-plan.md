# Claude Runtime Implementation Plan

## Operating Principle

Claude is the supervisory runtime. The application exposes durable tools,
records, policies, and administrative controls. Claude performs coordination,
task decomposition, specialist selection, synthesis, and next-step decisions by
calling those tools.

Before adding Python control flow, verify whether Claude can perform the same
coordination using tools. If yes, expose the needed tool contract and keep the
decision in Claude.

## Fixed Workflow

```text
periodic monitoring
 -> per-server Claude session
 -> monitoring completion
 -> exact historical report lookup
 -> exact match: reuse stored analysis
 -> similar match: pass top 3 similar reports to Ollama-backed analysis
 -> issue detection
 -> specialist selection
 -> specialist deep analysis
 -> aggregate specialist findings
 -> final analysis
 -> remediation proposal when needed
 -> isolated validation
 -> apply under policy or ask the user
```

This order is part of the product contract and must not be changed.

## Claude-Native Rule

Every phase must include a Claude-native capability check:

```text
Can Claude sequence this step?
Can Claude choose the next specialist?
Can Claude decide whether more evidence is needed?
Can Claude synthesize the result from structured tool outputs?
Can Claude produce the remediation plan from validated evidence?
```

When the answer is yes, Python must provide tools and schemas, not duplicate the
coordination logic.

Python remains responsible for:

```text
database persistence
SSH execution through registered commands
MCP/project tool boundaries
RAG retrieval
Ollama client calls
policy checks
sandbox validation
admin API and UI
audit logs
```

## Remaining Phases

### R.1 - Runtime Package Boundary

Status: **COMPLETE**

Claude runtime code lives under `app/runtime/claude/`.

Acceptance:

```text
no scheduler-facing class named switch
runtime entrypoint is ClaudeSupervisor
health exposes supervisor status
tests cover direct delegation to the Claude monitoring cycle
```

### R.2 - Tool Package Boundary

Status: **COMPLETE**

System-callable capabilities are exposed under `app/tools/`.

Target groups:

```text
app/tools/monitoring
app/tools/reports
app/tools/retrieval
app/tools/investigation
app/tools/specialists
app/tools/remediation
app/tools/ssh
```

Implemented:

```text
app/tools/project_boundary.py
app/tools/catalog.py
app/tools/monitoring/
app/tools/reports/
app/tools/retrieval/
app/tools/investigation/
app/tools/specialists/
app/tools/remediation/
app/tools/ssh/
app/mcp/project_tools.py
tests/test_project_tool_catalog.py
```

Acceptance:

```text
Claude calls project tools through explicit schemas
tool modules contain deterministic execution only
tool outputs are structured and persisted where needed
MCP remains a thin schema/compatibility boundary
```

### R.3 - Domain Services Boundary

Status: **COMPLETE**

Non-agent domain logic lives under `app/domain/`.

Target groups:

```text
app/domain/analysis
app/domain/investigation
app/domain/knowledge
app/domain/evaluation
```

Implemented:

```text
app/domain/analysis
app/domain/investigation
app/domain/knowledge
app/domain/evaluation
tests/test_domain_boundaries.py
```

Acceptance:

```text
domain services do not coordinate Claude sessions
domain services do not choose high-level workflow branches
domain services are callable from tools, API, and tests
domain modules do not import app.runtime or app.mcp
```

### R.4 - Admin Surface Alignment

Keep `app/admin/` as the human control plane.

Status: **COMPLETE**

Implemented:

```text
app/admin/api/system.py exposes supervisor status and grouped tool catalog
app/admin/web/templates/system.html displays runtime and tool groups
app/admin/web/routes.py registers the /system operator page
app/admin/web/templates/base.html links the system runtime view
tests/test_admin_system_api.py covers runtime/tool catalog response shape
tests/test_admin_system_web.py covers the system runtime page
tests/test_route_inventory.py covers the new web and API routes
```

Acceptance:

```text
admin screens show reports, jobs, specialists, evidence, remediation proposals
admin actions call shared/domain services
admin does not embed supervisory workflow logic
```

### R.5 - Documentation and Tests

Status: **COMPLETE**

Every phase must update:

```text
unit tests for moved modules
MCP/tool contract tests
runtime smoke tests
docs/PROJECT_STRUCTURE.md
docs/architecture/target-project-structure.md
docs/operations/claude-runtime.md
```

Implemented:

```text
docs/PROJECT_STRUCTURE.md documents generated file responsibilities
docs/testing/TEST_CATALOG.md documents current pytest coverage
docs/operations/claude-runtime.md matches configured Ollama defaults
tests/test_claude_runtime_documentation.py guards runtime documentation coverage
```

### C.14 - Real Claude-Native Orchestration

Status: **IN PROGRESS**

Goal:

```text
Claude Code session owns workflow sequencing and tool selection
project MCP server exposes capabilities to Claude Code
Python modules provide tools, policies, persistence, and validation
```

Implemented:

```text
.mcp.json registers the project-scoped vps MCP server
tools/run_project_mcp_server.py starts the stdio MCP server
app/mcp/server.py exposes initialize, tools/list, and tools/call
.claude/settings.json uses Claude Code permissions instead of project metadata
.claude/agents/*.md include YAML frontmatter, tools, MCP server, skills, and maxTurns
tests/test_claude_code_runtime_configuration.py validates Claude Code project configuration
tests/test_project_mcp_protocol_server.py validates the MCP protocol surface
```

Remaining:

```text
replace Python monitoring workflow sequencing with a Claude session launch
replace Python Specialist loop sequencing with Claude-selected tool calls
add runtime smoke tests for Claude session prompt and MCP tool availability
```

## Target Runtime Shape

```text
Scheduler
 -> ClaudeSupervisor
 -> Claude session
 -> Project MCP tools
 -> Domain services
 -> Repositories / SSH / Ollama / Sandbox
 -> Persisted jobs, reports, analyses, evidence, proposals
```

Claude owns the workflow. The project owns tools and records.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
