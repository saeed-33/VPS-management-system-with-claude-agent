# Project Status

<!-- DOC-STATUS: CURRENT -->

Last accepted diagnosis milestone: **Phase 4.20 complete**.

Current structural milestone: **C.14.11A — Structural Closure complete**.

## Current state

```text
Phase 4.20: complete
C.14.0–C.14.11: implemented and accepted
C.14.11A: complete
C.14.12: next, not started
Phase 5: blocked pending the C.14 runtime/readiness gates
diagnosis_readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
llm_provider: ollama
```

Historical structural milestones remain accepted:

```text
R.1 Runtime Package Boundary: complete
R.2 Tool Package Boundary: complete
R.3 Domain Services Boundary: complete
R.4 Admin Surface Alignment: complete
R.5 Documentation and Tests: complete
```

C.14.11A consolidates the repository around canonical application packages,
removes obsolete compatibility trees, preserves the Claude-visible MCP
contract, and synchronizes the Admin/tooling/documentation surfaces. It does
not implement C.14.12.

## Canonical responsibilities

```text
app/core            contracts, policies, configuration
app/capabilities    analysis, investigation, knowledge, monitoring
app/infrastructure  database, SSH, Ollama, and external adapters
app/interfaces      Admin HTTP/Web and Claude MCP interfaces
app/runtime         Claude runtime integration
app/composition     dependency wiring and bootstrap
tools/acceptance    runtime acceptance and evaluation
tools/dev           developer, inspection, seed, and documentation tooling
```

The `.mcp.json` entry point remains `tools/run_project_mcp_server.py`. The
project MCP server must preserve all 24 existing Claude-visible tool names and
their request/response contracts.

## Safety and product boundaries

Automatic remediation is not enabled. Production changes remain subject to
policy, explicit approval, sandbox validation, and the later readiness gates.
No OpenAI or LangGraph runtime path is part of the current production
architecture; Ollama is the configured provider.

## Gate sequence

The next allowed milestone after this closure is **C.14.12 — Runtime Readiness
Gate**. Phase 5 remains blocked until the applicable real-runtime, observability,
and safety/readiness evidence is accepted.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-13**

For the generated file inventory, see
[`docs/PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md).
<!-- PROJECT-DOC-METADATA:END -->
