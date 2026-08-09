# Project Documentation

هذه الوثائق تثبت baseline التنفيذ الحالي قبل بدء المرحلة متعددة الوكلاء.

- [Architecture](architecture/overview.md)
- [Workflows](workflows/current-workflows.md)
- [Database](architecture/database.md)
- [Architecture Decisions](decisions/README.md)
- [Testing](testing/testing-and-evaluation.md)
- [Performance](testing/performance.md)
- [Configuration](operations/configuration.md)
- [Operations](operations/migrations-and-troubleshooting.md)
- [Next Phase Roadmap](roadmap/next-phase-multi-agent.md)

قاعدة التوثيق: كل شيء خارج `roadmap/` يصف التنفيذ الحالي فقط.
## تشغيل المشروع وقاعدة البيانات

- [Running the Project](operations/running-project.md)
- [Database Bootstrap](operations/database-bootstrap.md)

## HTTP API and Admin UI

- [HTTP API Reference](api/http-api.md)
- [Admin Web UI](api/admin-web-ui.md)

## Deployment and Security

- [Production Deployment](deployment/production-deployment.md)
- [Production Checklist](deployment/production-checklist.md)
- [systemd Example](deployment/systemd-example.md)
- [Security Baseline](security/security-baseline.md)

## Phase 4
- [Phase 4 implementation plan](roadmap/phase-4-implementation-plan.md)
- [ADR-008: Dynamic specialists](decisions/ADR-008-dynamic-specialists.md)
- [ADR-009: Hierarchical investigation](decisions/ADR-009-hierarchical-investigation.md)

## Multi-Agent Investigation

- [4.1 Investigation Contracts](architecture/investigation-contracts.md)
- [Specialist Registry](architecture/specialist-registry.md)
- [Milestone A closeout — 4.0–4.4](roadmap/phase-4-foundation-closeout.md)
- [ADR-010: LangGraph orchestration boundary](decisions/ADR-010-langgraph-orchestration-boundary.md)
- [Investigation Router](architecture/investigation-router.md)
- [Investigation Persistence](architecture/investigation-persistence.md)
- [Knowledge Sources](architecture/knowledge-sources.md)
- [Knowledge Sources Seed](architecture/knowledge-sources-seed.md)
- [Knowledge RAG Schema](architecture/knowledge-rag-schema.md)
