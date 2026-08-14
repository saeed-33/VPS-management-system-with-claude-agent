# Knowledge Sources Seed and Acceptance

**Phase:** 4.7.1  
**Status:** Implemented — pending runtime acceptance

4.7.1 provides an idempotent baseline seed of official documentation for
the nine current Specialist definitions.

The seed contains official sources for:

```text
Linux kernel administration
Linux proc filesystem
Linux networking
Linux filesystems
systemd
Docker Engine
NGINX
PostgreSQL
```

The seed is intentionally metadata-only. It registers source URLs and their
scope but does not crawl or index content.

Run:

```powershell
uv run python tools/dev/seed_knowledge_sources.py
```

The command is idempotent:

```text
missing slug  -> create
existing slug -> update
```

Then inspect:

```powershell
uv run python tools/dev/inspect_knowledge_sources.py
uv run python tools/dev/inspect_knowledge_sources.py --domain cpu
uv run python tools/dev/inspect_knowledge_sources.py --specialist linux-network
```

Acceptance:

```powershell
uv run python tools/acceptance/check_knowledge_source_acceptance.py
```

All nine baseline Specialists must resolve to at least one enabled knowledge
source.

After acceptance, Phase 4.7 is complete. Phase 4.8 begins ingestion,
parsing, chunking, indexing and retrieval.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.
<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
