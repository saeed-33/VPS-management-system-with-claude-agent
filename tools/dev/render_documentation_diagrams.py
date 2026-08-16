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

CUSTOM_DIAGRAMS = {
    "16-use-case", "17-monitoring-sequence", "18-remediation-activity",
    "19-operator-use-case", "20-admin-use-case", "21-specialist-sequence",
    "22-supervised-sequence", "23-autonomous-sequence", "24-admin-sequence",
    "25-admin-dashboard", "26-investigation-interface", "27-remediation-interface",
}


def font(size: int):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى font؛ المدخلات المهمة: size.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render(name: str, labels: list[str]) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى render؛ المدخلات المهمة: name، labels.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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


def save_custom(name: str, image: Image.Image) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى save_custom؛ المدخلات المهمة: name، image.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    for directory in (ARCHIVE_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        image.save(directory / f"{name}.png", dpi=(220, 220))


def draw_box(draw: ImageDraw.ImageDraw, xy, label: str, *, fill="#E8EEF5", outline="#2E74B5", size=26):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى draw_box؛ المدخلات المهمة: draw، xy، label، fill، outline، size.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    draw.rounded_rectangle(xy, radius=18, fill=fill, outline=outline, width=4)
    x1, y1, x2, y2 = xy
    bbox = draw.textbbox((0, 0), label, font=font(size))
    draw.text(((x1 + x2 - bbox[2] + bbox[0]) / 2, (y1 + y2 - bbox[3] + bbox[1]) / 2), label, fill="#0B2545", font=font(size))


def draw_arrow(draw: ImageDraw.ImageDraw, start, end, label: str = ""):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى draw_arrow؛ المدخلات المهمة: draw، start، end، label.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    draw.line((*start, *end), fill="#7A5A00", width=4)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if abs(dx) >= abs(dy):
        tip = (end[0], end[1])
        wing = [(end[0] - 18 if dx > 0 else end[0] + 18, end[1] - 10), (end[0] - 18 if dx > 0 else end[0] + 18, end[1] + 10)]
    else:
        tip = (end[0], end[1])
        wing = [(end[0] - 10, end[1] - 18 if dy > 0 else end[1] + 18), (end[0] + 10, end[1] - 18 if dy > 0 else end[1] + 18)]
    draw.polygon([tip, *wing], fill="#7A5A00")
    if label:
        draw.text(((start[0] + end[0]) // 2 - 80, (start[1] + end[1]) // 2 - 30), label, fill="#0B2545", font=font(22))


def render_use_case() -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى render_use_case؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    image = Image.new("RGB", (W, H), "#F7F9FC")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), "Use Case Diagram", fill="#0B2545", font=font(42))
    draw.rounded_rectangle((500, 125, 1710, 930), radius=24, outline="#2E74B5", width=5, fill="#FFFFFF")
    draw.text((550, 145), "AI VPS Management System", fill="#0B2545", font=font(30))
    draw.ellipse((110, 240, 390, 340), fill="#E8EEF5", outline="#2E74B5", width=4)
    draw.text((170, 270), "Operator", fill="#0B2545", font=font(28))
    draw.ellipse((110, 650, 390, 750), fill="#E8EEF5", outline="#2E74B5", width=4)
    draw.text((185, 680), "Admin", fill="#0B2545", font=font(28))
    cases = [(610, 245, "Monitor VPS"), (1080, 245, "Review report"), (610, 390, "Request investigation"), (1080, 390, "View Evidence"), (610, 535, "Approve plan"), (1080, 535, "Run supervised fix"), (610, 680, "Enable policy"), (1080, 680, "Audit operation")]
    for x, y, label in cases:
        draw_box(draw, (x, y, x + 390, y + 90), label, fill="#F2F4F7", size=25)
    for target in [(610, 290), (610, 435), (610, 725)]:
        draw_arrow(draw, (390, 290 if target[1] < 500 else 700), target)
    for target in [(1080, 290), (1080, 435), (1080, 580), (1080, 725)]:
        draw_arrow(draw, (390, 700), target)
    save_custom("16-use-case", image)


def render_sequence() -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى render_sequence؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    image = Image.new("RGB", (W, H), "#F7F9FC")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), "Monitoring and Analysis Sequence", fill="#0B2545", font=font(42))
    columns = [(170, "Operator"), (500, "Admin UI"), (830, "Monitoring"), (1160, "Analysis"), (1490, "Database")]
    for x, label in columns:
        draw_box(draw, (x - 105, 130, x + 105, 205), label, size=23)
        draw.line((x, 205, x, 900), fill="#78909C", width=3)
    messages = [(280, 170, 830, "start monitoring"), (350, 830, 1490, "save report"), (430, 1490, 1160, "load previous analysis"), (520, 1160, 830, "request evidence"), (610, 830, 1490, "persist diagnosis"), (700, 1490, 500, "show result"), (790, 500, 170, "display status")]
    for y, x1, x2, label in messages:
        draw_arrow(draw, (x1, y), (x2, y), label)
    save_custom("17-monitoring-sequence", image)


def render_activity() -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى render_activity؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    image = Image.new("RGB", (W, H), "#F7F9FC")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), "Supervised Remediation Activity", fill="#0B2545", font=font(42))
    steps = [(120, "Start"), (250, "Read diagnosis and Evidence"), (390, "Build plan and fingerprint"), (530, "Validate policy and target"), (670, "Human approval"), (810, "Verify, execute, and audit")]
    for index, (y, label) in enumerate(steps):
        if label == "Start":
            draw.ellipse((760, y, 1040, y + 75), fill="#D8F3DC", outline="#2E7D32", width=4)
            draw.text((850, y + 22), label, fill="#0B2545", font=font(26))
        else:
            draw_box(draw, (610, y, 1190, y + 85), label, size=25)
        if index:
            draw_arrow(draw, (900, steps[index - 1][0] + 80), (900, y))
    draw_box(draw, (610, 930, 1190, 995), "Rollback and record failure", fill="#FDECEC", outline="#B71C1C", size=22)
    draw_arrow(draw, (1190, 852), (1190, 962), "if verification fails")
    save_custom("18-remediation-activity", image)


def render_actor_use_case(name: str, title: str, actor: str, cases: list[str]) -> None:
    """Render an actor-focused use-case diagram for the report's analysis chapter."""
    image = Image.new("RGB", (W, H), "#F7F9FC")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), title, fill="#0B2545", font=font(42))
    draw.ellipse((110, 420, 390, 520), fill="#E8EEF5", outline="#2E74B5", width=4)
    draw.text((175, 452), actor, fill="#0B2545", font=font(28))
    draw.rounded_rectangle((520, 125, 1710, 900), radius=24, outline="#2E74B5", width=5, fill="#FFFFFF")
    draw.text((575, 145), "AI VPS Management System", fill="#0B2545", font=font(30))
    positions = [(610, 250), (1110, 250), (610, 430), (1110, 430), (610, 610), (1110, 610)]
    for (x, y), label in zip(positions, cases):
        draw_box(draw, (x, y, x + 390, y + 90), label, fill="#F2F4F7", size=23)
        draw_arrow(draw, (390, 470), (x, y + 45))
    save_custom(name, image)


def render_lifeline_sequence(name: str, title: str, columns: list[str], messages: list[tuple[int, int, int, str]]) -> None:
    """Render a readable system-sequence diagram from actor-to-service messages."""
    image = Image.new("RGB", (W, H), "#F7F9FC")
    draw = ImageDraw.Draw(image)
    draw.text((80, 45), title, fill="#0B2545", font=font(42))
    left = 140
    step = (W - 280) // max(1, len(columns) - 1)
    x_positions = [left + i * step for i in range(len(columns))]
    for x, label in zip(x_positions, columns):
        draw_box(draw, (x - 125, 125, x + 125, 205), label, size=21)
        draw.line((x, 205, x, 920), fill="#78909C", width=3)
    for y, source, target, label in messages:
        draw_arrow(draw, (x_positions[source], y), (x_positions[target], y), label)
    save_custom(name, image)


def render_ui_wireframe(name: str, title: str, nav: list[str], cards: list[str]) -> None:
    """Render a schematic of an existing Admin template, not a fabricated screenshot."""
    image = Image.new("RGB", (W, H), "#EEF2F7")
    draw = ImageDraw.Draw(image)
    draw.text((70, 35), title, fill="#0B2545", font=font(40))
    draw.rounded_rectangle((100, 120, 1700, 930), radius=18, fill="#FFFFFF", outline="#2E74B5", width=4)
    draw.rectangle((100, 120, 430, 930), fill="#0B2545")
    draw.text((145, 160), "Admin", fill="#FFFFFF", font=font(30))
    for i, label in enumerate(nav):
        draw.rounded_rectangle((135, 235 + i * 70, 395, 285 + i * 70), radius=8, fill="#173B63")
        draw.text((160, 248 + i * 70), label, fill="#FFFFFF", font=font(21))
    for i, label in enumerate(cards):
        x = 500 + (i % 2) * 530
        y = 180 + (i // 2) * 230
        draw_box(draw, (x, y, x + 460, y + 150), label, fill="#F2F4F7", size=24)
    save_custom(name, image)


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    for name, labels in DIAGRAMS.items():
        render(name, labels)
    render_use_case()
    render_sequence()
    render_activity()
    render_actor_use_case("19-operator-use-case", "Operator Use Cases", "Operator", ["Monitor VPS", "Review reports", "Request investigation", "Review Evidence", "Approve plan", "Run supervised fix"])
    render_actor_use_case("20-admin-use-case", "Admin Use Cases", "Admin", ["Manage servers", "Manage specialists", "Manage policies", "Review authorizations", "Recover lease", "Audit operations"])
    render_lifeline_sequence("21-specialist-sequence", "Specialist Investigation Sequence", ["Operator", "API", "Router", "Specialist loop", "Evidence", "Database"], [(280, 0, 1, "request investigation"), (370, 1, 2, "select specialists"), (460, 2, 3, "run bounded tools"), (550, 3, 4, "collect evidence"), (640, 4, 5, "persist result"), (730, 5, 1, "return diagnosis")])
    render_lifeline_sequence("22-supervised-sequence", "Supervised Remediation Sequence", ["Operator", "Admin UI", "Policy", "Sandbox", "SSH", "Audit DB"], [(280, 0, 1, "review plan"), (370, 1, 2, "validate policy"), (460, 2, 3, "validate target"), (550, 3, 4, "execute named action"), (640, 4, 5, "persist result"), (730, 5, 1, "show verification")])
    render_lifeline_sequence("23-autonomous-sequence", "Autonomous Execution Sequence", ["Evaluator", "Authorization", "Reservation", "Worker", "VPS", "Finalize"], [(280, 0, 1, "issue once"), (370, 1, 2, "reserve briefly"), (460, 2, 3, "grant owner"), (550, 3, 4, "named operation"), (640, 4, 5, "verify and merge"), (730, 5, 2, "conditional finalize")])
    render_lifeline_sequence("24-admin-sequence", "Admin Approval and Audit Sequence", ["Admin", "Browser", "Session", "Policy API", "Database"], [(280, 0, 1, "submit decision"), (370, 1, 2, "check session"), (460, 2, 3, "check role + CSRF"), (550, 3, 4, "save decision"), (640, 4, 3, "audit result"), (730, 3, 1, "structured response")])
    render_ui_wireframe("25-admin-dashboard", "Admin Dashboard Template", ["Dashboard", "Servers", "Reports", "Investigations", "Audit"], ["System status", "Recent monitoring reports", "Open investigations", "Recent audit events", "Service health", "Pending actions"])
    render_ui_wireframe("26-investigation-interface", "Investigation and Evidence Template", ["Investigations", "Specialists", "Knowledge", "Reports"], ["Incident summary", "Specialist results", "Evidence sources", "Conflicting findings", "Final diagnosis", "Next action"])
    render_ui_wireframe("27-remediation-interface", "Remediation and Policy Templates", ["Remediation", "Policies", "Authorizations", "Reservations", "History"], ["Plan and fingerprint", "Risk and target", "Approval state", "Reservation state", "Verification", "Audit trail"])
    print(f"Rendered {len(DIAGRAMS) + len(CUSTOM_DIAGRAMS)} documentation figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
