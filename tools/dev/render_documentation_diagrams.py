"""Render the documentation diagram set to reproducible high-resolution PNGs."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "docs" / "architecture" / "diagrams"
ARCHIVE_DIR = SOURCE_DIR / "rendered"
REPORT_DIR = ROOT / "docs" / "report" / "figures"
W, H = 1800, 1000

DIAGRAMS = {
    "01-system-block": ["Admin / Operator", "FastAPI Admin API/Web", "Python Capabilities + Policies", "PostgreSQL + pgvector", "Known-hosts SSH", "Ollama", "Native Sandbox + Evidence", "Claude Code -> bounded vps MCP"],
    "02-system-context": ["Admin UI", "AI VPS Management", "Claude Code", "Managed Linux VPS", "PostgreSQL", "Ollama", "WSL2 Native Sandbox", "Project MCP"],
    "03-component-layers": ["app/core", "app/capabilities", "app/runtime/claude", "app/interfaces/admin + mcp", "app/infrastructure", "app/composition"],
    "04-claude-ollama-mcp-python": ["Claude Code", "vps MCP: typed bounded request", "Python policy/capability", "Ollama", "DB / SSH / Evidence", "Safe structured response"],
    "05-monitor-analysis-investigation": ["Trigger", "MonitoringService", "Persisted report", "AnalysisOrchestrator", "InvestigationRouter", "Specialist loop", "Evidence", "Final diagnosis"],
    "06-specialist-orchestration": ["InvestigationRouter", "SpecialistInvestigationLoop", "DiagnosticPolicy", "Registered read-only tools", "EvidenceCollectionService", "Persisted result"],
    "07-supervised-remediation": ["Grounded diagnosis", "Immutable plan/fingerprint", "Native sandbox", "Human approval", "Named write", "Verification / rollback", "Audit"],
    "08-sandbox-validation": ["Plan fingerprint", "Persisted safe target", "Native attestation", "Before Evidence", "Registered validation", "After Evidence", "Verify + restore", "Persist + audit"],
    "09-autonomous-sequence": ["Evaluator gates", "AUTO_EXECUTE", "Single-use authorization", "Short reservation lease", "Named execution", "Verify / rollback", "Owner-token finalize"],
    "10-policy-reservation-idempotency": ["Issue + plan fingerprints", "Policy match", "Consume authorization", "Unique idempotency key", "Owner-token execution", "Conditional finalize", "Replay blocked"],
    "11-circuit-recovery": ["Enabled", "Failure threshold -> Suspended", "Future evaluation denied", "Explicit operator resume", "New epoch", "Lease recovery"],
    "12-admin-auth-rbac": ["Login", "scrypt", "Server session digest", "Middleware", "RBAC", "CSRF", "Operation", "Audit"],
    "13-deployment": ["Browser", "FastAPI/Uvicorn", "PostgreSQL + pgvector", "Ollama", "Claude Code", "Project MCP", "Known-hosts SSH", "VPS", "WSL2 Sandbox"],
    "14-database-erd": ["Monitoring: servers / profiles / reports", "Analysis + RAG", "Investigation + Specialists", "Remediation + Evidence", "Autonomous policy / decision / auth / reservation", "Admin users / sessions / audit"],
    "15-key-components": ["ClaudeSupervisor", "ProjectMcpToolBoundary", "MonitoringService", "InvestigationRouter", "SpecialistInvestigationLoop", "EvidenceCollectionService", "RemediationService", "AutonomousPolicyEvaluator", "AutonomousExecutionService", "AdminAuthService"],
}


def font(size: int):
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render(name: str, labels: list[str]) -> None:
    image = Image.new("RGB", (W, H), "#F7F9FC")
    draw = ImageDraw.Draw(image)
    title = name.replace("-", " ").title()
    draw.text((80, 45), title, fill="#0B2545", font=font(42))
    cols = 3 if len(labels) > 7 else 2
    rows = (len(labels) + cols - 1) // cols
    box_w = 450 if cols == 3 else 650
    box_h = 105
    gap_x = 90
    gap_y = 70
    total_w = cols * box_w + (cols - 1) * gap_x
    start_x = (W - total_w) // 2
    start_y = 170
    points = []
    boxes = []
    for i, label in enumerate(labels):
        col = i % cols
        row = i // cols
        x = start_x + col * (box_w + gap_x)
        y = start_y + row * (box_h + gap_y)
        boxes.append((x, y, x + box_w, y + box_h, label))
        points.append((x + box_w // 2, y + box_h // 2))
    for left, right in zip(points, points[1:]):
        draw.line((left[0], left[1], right[0], right[1]), fill="#7A5A00", width=5)
        draw.polygon([(right[0] - 16, right[1] - 8), (right[0], right[1]), (right[0] - 16, right[1] + 8)], fill="#7A5A00")
    for x, y, right, bottom, label in boxes:
        draw.rounded_rectangle((x, y, right, bottom), radius=18, fill="#E8EEF5", outline="#2E74B5", width=4)
        wrapped = label if len(label) <= 35 else label[:32] + "..."
        bbox = draw.textbbox((0, 0), wrapped, font=font(27))
        draw.text((x + (box_w - (bbox[2] - bbox[0])) / 2, y + 35), wrapped, fill="#0B2545", font=font(27))
    for directory in (ARCHIVE_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        image.save(directory / f"{name}.png", dpi=(220, 220))


def main() -> int:
    for name, labels in DIAGRAMS.items():
        render(name, labels)
    print(f"Rendered {len(DIAGRAMS)} documentation figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
