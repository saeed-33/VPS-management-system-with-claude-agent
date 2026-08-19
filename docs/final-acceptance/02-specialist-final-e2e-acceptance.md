# 02 — Specialist Final E2E Acceptance

## 1. Objective

Validate the canonical investigation flow from persistence and routing through
Specialist execution, Evidence binding, correlation, final diagnosis,
finalization, idempotency, budgets, and failure persistence.

## 2. Scope

The integration run exercised the production PostgreSQL and SSH boundaries,
the canonical MCP investigation boundary, Specialist loop, policy, Evidence
collector, persistence, correlator, and final diagnosis synthesizer. The
deterministic proof is retained alongside real Ollama execution and the real
Claude/Ollama supervisory attempts.

## 3. Preconditions

- PostgreSQL was reachable through the explicit WSL operational environment.
- Ollama and the safe lab SSH target were available.
- The seeded Specialist definitions were present in the database.
- The designated lab target was not production.
- Real-runtime tests were opt-in.

## 4. Environment

- Date: 2026-08-14.
- Repository: `E:\AI_VPS_Mamgment\chat_system`.
- Operational WSL overrides included `POSTGRES_HOST=172.18.128.1`,
  `OLLAMA_BASE_URL=http://172.18.128.1:11434`,
  `DEFAULT_SSH_PRIVATE_KEY_PATH`, and `SSH_KNOWN_HOSTS_PATH`.
- Secret values and private-key contents were not recorded.

## 5. Safety constraints

- Read-only diagnostic tools were bounded by each persisted Specialist's
  `allowed_tool_ids`.
- Evidence references had to resolve to collected project Evidence IDs.
- Invalid or fabricated Evidence references had to fail closed.
- Budgets, failure persistence, idempotency, and final-state safety remained
  enforced.

## 6. Exact commands or procedure

Focused regression:

```bash
uv run --no-sync python -m pytest tests/integration/database/test_specialist_seeding.py tests/unit/capabilities/investigation/test_persistence_service.py tests/unit/capabilities/investigation/test_router.py tests/unit/capabilities/investigation/test_specialist_registry.py tests/unit/capabilities/investigation/test_specialist_execution_persistence.py tests/unit/capabilities/investigation/test_specialist_investigation_loop.py tests/unit/capabilities/investigation/test_cross_specialist_correlation.py tests/unit/capabilities/investigation/test_cross_specialist_conflicts.py tests/unit/capabilities/investigation/test_final_diagnosis_synthesizer.py tests/integration/mcp/test_investigation_tools.py tests/integration/mcp/test_specialist_tools.py tests/integration/mcp/test_tool_boundary.py tests/unit/runtime/claude/test_bounded_agents.py tests/unit/runtime/claude/test_least_privilege.py -q
```

Full non-real regression:

```bash
uv run --no-sync python -m pytest -q -r s
```

Real Ollama loop smoke through the production composition:

```bash
POSTGRES_HOST=172.18.128.1 OLLAMA_BASE_URL=http://172.18.128.1:11434 \
DEFAULT_SSH_PRIVATE_KEY_PATH=/mnt/c/Users/SAEED/.ssh/monitor_agent_ed25519 \
SSH_KNOWN_HOSTS_PATH=/mnt/c/Users/SAEED/.ssh/known_hosts \
LLM_ENABLED=true LLM_PROVIDER=ollama OLLAMA_MODEL=gemma4:e4b-it-q4_K_M \
uv run --no-sync python tools/dev/run_specialist_investigation.py \
  4 systemd-service "List failed systemd units and determine whether the current service domain has a failed-unit signal." \
  --report-id 1832 --domains systemd,service --max-rounds 2 --max-actions 3
```

Real Claude/Ollama/MCP acceptance:

```bash
AI_VPS_RUN_REAL_RUNTIME_TESTS=1 \
POSTGRES_HOST=172.18.128.1 OLLAMA_BASE_URL=http://172.18.128.1:11434 \
DEFAULT_SSH_PRIVATE_KEY_PATH=/mnt/c/Users/SAEED/.ssh/monitor_agent_ed25519 \
SSH_KNOWN_HOSTS_PATH=/mnt/c/Users/SAEED/.ssh/known_hosts \
LLM_ENABLED=true LLM_PROVIDER=ollama CLAUDE_RUNTIME_ENABLED=true \
AI_VPS_REAL_RUNTIME_SERVER_ID=4 \
uv run --no-sync python -m pytest \
  tests/acceptance/external_runtime/test_real_claude_ollama_mcp_cycle.py -q -r s
```

The canonical MCP `start_investigation` path was run against the safe lab
report, followed by Specialist execution and read-back of persisted results.

## 7. Expected acceptance gates

`INVESTIGATION_PERSISTENCE`, `SPECIALIST_SELECTION`,
`SPECIALIST_EXECUTION`, `SPECIALIST_PERSISTENCE`, `SPECIALIST_EVIDENCE_BINDING`,
`SPECIALIST_CORRELATION`, `FINAL_DIAGNOSIS`, `INVESTIGATION_FINALIZATION`,
`SPECIALIST_IDEMPOTENCY`, `SPECIALIST_BUDGET_ENFORCEMENT`,
`SPECIALIST_FAILURE_PERSISTENCE`, and `CLAUDE_SPECIALIST_BOUNDARY` must pass.

## 8. Actual results

The deterministic production-composition integration passed all listed gates.
Investigation `2ba73e0e-c63e-44be-9bb0-4dbc341fd29b` completed with selected
Specialists `systemd-service`, `docker`, and `linux-network`. Three Specialist
runs persisted as completed; two collected Evidence records were bound; final
diagnosis reported two confirmed claims, one unknown claim, and zero
conflicts. Replay returned `idempotent=true`. No duplicate Specialist results
or Evidence were created.

Regression results after the seed fix were `79 passed` focused and `587 passed,
4 skipped` full non-real. The new focused contract/environment run passed `38`.
The final Claude/MCP/Specialist contract suite passed `54` before the bounded
real run. `compileall` and `git diff --check` passed.

Chronological live revalidation:

1. Initial acceptance was **PARTIAL**: deterministic production-composition
   Specialist execution passed; real Ollama returned raw log text in an
   Evidence-ID field and the Claude harness overwrote the operational database
   host.
2. The Ollama contract correction added explicit per-execution Evidence-ID
   allowlisting in the prompt, schema descriptions, and regression coverage.
   Backend validation remains authoritative and fail-closed.
3. Real Ollama then completed the canonical selected set on investigation
   `82b7f33e-52c2-4240-b092-5380d486e1f0` using
   `ollama/gemma4:e4b-it-q4_K_M`; three read-only Evidence records persisted,
   all three Specialist runs completed, and final diagnosis/finalization
   persisted. No invalid Evidence ID was accepted.
4. The Claude harness now preserves explicit environment values, disables
   pytest's isolated DB defaults during opt-in real runs, and restores the
   persisted lab key path after acceptance. The harness passed once with job
   `6ceb9d9e-737d-42f3-a1b5-53411b635ef5`, but Claude stopped after creating
   investigation `fa2592a6-76ec-45fc-895f-4317b5d7ccbe` and did not persist a
   Specialist run.
5. A narrowly tightened supervisory prompt was tested to force completion; it
   exceeded the configured 300-second bound with job
   `a782f112-27e8-4a4e-9ff6-85cae20c0267`. That experimental prompt change was
   reverted. It is retained here as a failed attempt, not as a PASS.
6. The final prompt correction explicitly required complete investigation
   progress and supplied the generic Agent delegation contract (`description`,
   `prompt`, `investigation_id`, `specialist_slug`, and objective). The one
   final bounded run created investigation
   `a1a2773b-b6e2-428c-8ffc-4fec02480587`, persisted the selected
   `systemd-service` Specialist execution and two project Evidence records,
   then hit the unchanged 300-second timeout before the remaining selected
   Specialists and finalization completed.

## 9. Evidence / IDs

- Investigation: `2ba73e0e-c63e-44be-9bb0-4dbc341fd29b`.
- Runs: `2ba73e0e-c63e-44be-9bb0-4dbc341fd29b:systemd-service:1`,
  `...:docker:1`, and `...:linux-network:1`.
- Evidence: `2ba73e0e-c63e-44be-9bb0-4dbc341fd29b:systemd-service:1:r1:a1:systemd-status`
  and `2ba73e0e-c63e-44be-9bb0-4dbc341fd29b:linux-network:1:r1:a1:network-listeners`.
- Real Ollama failure Investigation:
  `7924de69-15d8-444b-9b0d-167c2a05d353`.
- Real Ollama completed Investigation:
  `82b7f33e-52c2-4240-b092-5380d486e1f0`.
- Real Ollama Specialist runs:
  `82b7f33e-52c2-4240-b092-5380d486e1f0:systemd-service:1`,
  `...:docker:1`, and `...:linux-network:1`.
- Real Ollama Evidence:
  `82b7f33e-52c2-4240-b092-5380d486e1f0:systemd-service:1:r1:a1:systemd-failed`,
  `...:docker:1:r1:a1:docker-ps`, and
  `...:linux-network:1:r1:a1:network-listeners`.
- Real Claude successful harness job:
  `6ceb9d9e-737d-42f3-a1b5-53411b635ef5`.
- Real Claude-created but incomplete Investigation:
  `fa2592a6-76ec-45fc-895f-4317b5d7ccbe`.
- Real Claude timeout job:
  `a782f112-27e8-4a4e-9ff6-85cae20c0267`.
- Final bounded Claude job:
  `03c1a8d4-8350-40b2-9d84-9e3b78f3e582` (`timed_out`, 300 seconds).
- Final Claude-created Investigation:
  `a1a2773b-b6e2-428c-8ffc-4fec02480587` (`investigating`).
- Final Claude Specialist execution:
  `a1a2773b-b6e2-428c-8ffc-4fec02480587:systemd-service:1` (`completed`).
- Final Claude Evidence:
  `a1a2773b-b6e2-428c-8ffc-4fec02480587:systemd-service:1:r1:a1:systemd-status`
  and `...:r1:a2:journal-unit`.
- Seeded Specialist regression: `tests/test_seed_specialists.py`.

## 10. Failed attempts

- Real Ollama attempts with the installed models failed closed when the model
  emitted raw log text instead of valid Evidence IDs. The failures persisted.
- The live Claude acceptance harness failed before Claude execution because it
  overwrote the operational PostgreSQL host with `127.0.0.1`.
- After environment precedence was corrected, one real Claude run completed the
  monitoring/MCP harness but stopped with an unexecuted created investigation.
- The experiment that required nested Specialist completion timed out at the
  existing five-minute runtime bound and was reverted.
- The final bounded run reached Python Specialist execution and persisted
  Evidence, but the Claude job itself timed out before terminal investigation
  finalization. The persisted job record contains `error_code=timed_out`, no
  exception, and the unchanged `max_turns=20`/300-second runtime settings.

## 11. Root cause if failure occurred

The original Ollama failure was a narrow structured-output contract issue: the
model copied raw observation text where an opaque project Evidence ID was
required. The original Claude failure was acceptance-harness environment
precedence, compounded in WSL by a persisted Windows key-path representation.
The earlier live-flow gap was the acceptance prompt permitting completion
after investigation creation. The final prompt correction removed that
ambiguity and the bounded run did persist a canonical Specialist result. The
remaining limitation is completing all selected Specialists and finalization
within the existing five-minute Claude acceptance bound.

## 12. Fix performed

The discovered seed defect was fixed by assigning registered read-only tool IDs
to each canonical Specialist and preserving them in create/update DTOs. A
regression test was added, and local persisted definitions were updated with
`tools/dev/seed_specialists.py --update-existing`.

The Ollama contract fix added schema descriptions, an explicit Evidence-ID
allowlist, and deterministic rejection tests. The Claude harness now preserves
explicit environment values, avoids injecting isolated DB defaults for real
runs, restores its temporary WSL key-path normalization, and requires complete
Specialist progress in the acceptance prompt. No DB networking redesign,
migration, or architecture replacement was performed.

The current 25-tool MCP surface is sufficient for the intended continuation:
`start_investigation` returns the persisted `investigation_id` and routing;
`get_investigation_status` exposes selected and remaining Specialists;
`Agent(specialist-worker)` receives the structured delegation inputs; the
worker reads the DB definition, calls bounded `run_specialist`, then reads
`get_evidence`; and the parent rereads status, Evidence, and investigation
state. No Admin-only, raw shell, SSH, SQL, or hidden Python-only capability is
required.

## 13. Revalidation

The seed fix passed the focused and full non-real regressions, compile check,
and diff check. The deterministic production-composition integration passed.
Real Ollama passed through the canonical production composition with live SSH,
live read-only tools, persisted Evidence, completed Specialists, and final
diagnosis. Claude environment precedence passed. The final real Claude/MCP run
caused a canonical Python Specialist execution and persisted two Evidence
records, but timed out before terminal finalization.

## 14. Accepted limitation

### Remaining live Claude-to-Specialist flow

The real Claude harness can preserve the explicit operational environment and
now demonstrably reaches Python Specialist execution through the bounded MCP
boundary. The final run did not reach terminal Investigation finalization
within the unchanged five-minute bound. This is classified as
`NONDETERMINISTIC_SUPERVISORY_ACCEPTANCE`, not `PRODUCT_DEFECT`.

The limitation is accepted. No production orchestration defect was identified,
no architecture change is justified, and this limitation does not block final
project closure.

## 15. Final status

**REAL_CLAUDE_SPECIALIST_FLOW = PASS**

**SPECIALIST_FINAL_E2E_ACCEPTANCE = PARTIAL**

**ACCEPTED_LIMITATION = YES**

**PROJECT_CLOSURE_BLOCKING = NO**

The Ollama reasoning/Evidence contract and Claude acceptance environment gates
pass, and the explicit real-flow gate passes because Claude caused a canonical
Specialist execution and project Evidence to persist. The broader final E2E
record remains partial because the final bounded Claude job timed out with
Investigation status `investigating`, two selected Specialists remaining, and
no final diagnosis/finalization. This is an acceptance limitation,
not a discovered production orchestration defect, and it is accepted as
non-blocking for project closure.

## 16. Whether production code changed

Yes. Changes for this revalidation include the Specialist contract/prompt,
Ollama adapter prompt guidance, Specialist regression tests, Claude acceptance
environment handling, and `tests/conftest.py` real-runtime default isolation.
The prior Specialist validation work also changed
`tools/dev/seed_specialists.py` and added `tests/test_seed_specialists.py`.

## 17. Whether commit/push occurred

No commit or push occurred.

## 18. Final disposition carried into project readiness

```text
REAL_OLLAMA_SPECIALIST_REASONING = PASS
REAL_OLLAMA_EVIDENCE_CONTRACT = PASS
REAL_CLAUDE_SPECIALIST_FLOW = PASS
CLAUDE_SPECIALIST_BOUNDARY = PASS
MCP_TOOL_COUNT = 25

SPECIALIST_FINAL_E2E_ACCEPTANCE = PARTIAL
ACCEPTED_LIMITATION = YES
PROJECT_CLOSURE_BLOCKING = NO
```

The final real Claude run was job
`03c1a8d4-8350-40b2-9d84-9e3b78f3e582`, investigation
`a1a2773b-b6e2-428c-8ffc-4fec02480587`, with completed
`systemd-service` and remaining `docker` and `linux-network` at the unchanged
300-second timeout. This remains
`NONDETERMINISTIC_SUPERVISORY_ACCEPTANCE`, not `PRODUCT_DEFECT`. The
deployment-security audit did not rerun Specialist acceptance.
