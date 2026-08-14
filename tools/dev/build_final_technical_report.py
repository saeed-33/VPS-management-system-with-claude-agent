"""Build the Arabic implementation-focused technical report from the retained template."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "1-Report-Template.docx"
OUT = ROOT / "docs" / "report" / "سعيد_بقدونس_هندسة_برمجيات_وذكاء_صنعي_Safe_Autonomous_AI_Agent_VPS.docx"
FIGURES = ROOT / "docs" / "report" / "figures"
BULLET_NUM_ID = None

BLUE = RGBColor(0x1F, 0x4D, 0x78)
LIGHT_BLUE = "E8EEF5"
GRAY = "F2F4F7"


def set_rtl(paragraph, align=WD_ALIGN_PARAGRAPH.RIGHT):
    paragraph.alignment = align
    ppr = paragraph._p.get_or_add_pPr()
    bidi = ppr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi")
        ppr.append(bidi)
    bidi.set(qn("w:val"), "1")


def set_font(run, name="Arial", size=12, bold=False, color=None):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:cs"), name)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = color


def shade(cell, fill: str):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = tcpr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcpr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tcpr = tc.get_or_add_tcPr()
    tc_mar = tcpr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tcpr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths):
    table.alignment = WD_TABLE_ALIGNMENT.RIGHT
    table.autofit = False
    tbl = table._tbl
    tblpr = tbl.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW")
        tblpr.append(tblw)
    tblw.set(qn("w:w"), str(sum(widths)))
    tblw.set(qn("w:type"), "dxa")
    ind = tblpr.find(qn("w:tblInd"))
    if ind is None:
        ind = OxmlElement("w:tblInd")
        tblpr.append(ind)
    ind.set(qn("w:w"), "120")
    ind.set(qn("w:type"), "dxa")
    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            tcpr = cell._tc.get_or_add_tcPr()
            tcw = tcpr.find(qn("w:tcW"))
            if tcw is None:
                tcw = OxmlElement("w:tcW")
                tcpr.append(tcw)
            tcw.set(qn("w:w"), str(widths[i]))
            tcw.set(qn("w:type"), "dxa")
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)


def mark_header_row(row):
    trpr = row._tr.get_or_add_trPr()
    header = trpr.find(qn("w:tblHeader"))
    if header is None:
        header = OxmlElement("w:tblHeader")
        trpr.append(header)
    header.set(qn("w:val"), "true")


def add_page_field(paragraph, field="PAGE"):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {field} "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    set_font(run, size=10, color=RGBColor(0x66, 0x66, 0x66))


def add_toc_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "افتح الحقل في Word لتحديث فهرس المحتويات"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    set_font(run, size=12)


def add_text(doc, text, *, bold=False, size=12, align=WD_ALIGN_PARAGRAPH.RIGHT, style=None):
    p = doc.add_paragraph(style=style)
    set_rtl(p, align)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    set_font(r, size=size, bold=bold)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Paragraph")
    set_rtl(p)
    p.paragraph_format.space_after = Pt(3)
    ppr = p._p.get_or_add_pPr()
    numpr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), "0")
    numid = OxmlElement("w:numId")
    numid.set(qn("w:val"), str(BULLET_NUM_ID))
    numpr.extend([ilvl, numid])
    ppr.append(numpr)
    r = p.add_run(text)
    set_font(r, size=11)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    set_rtl(p)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    set_font(r, size={1: 18, 2: 15, 3: 13}.get(level, 12), bold=True, color=BLUE)
    return p


def add_table(doc, headers: list[str], rows: Iterable[Iterable[str]], widths=None, caption=None):
    if caption:
        add_text(doc, caption, bold=True, size=10)
    rows = [list(map(str, row)) for row in rows]
    table = doc.add_table(rows=1, cols=len(headers))
    mark_header_row(table.rows[0])
    widths = widths or [9360 // len(headers)] * len(headers)
    set_table_geometry(table, widths)
    for i, value in enumerate(headers):
        cell = table.rows[0].cells[i]
        shade(cell, LIGHT_BLUE)
        cell.text = ""
        p = cell.paragraphs[0]
        set_rtl(p, WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(value)
        set_font(r, size=9, bold=True, color=BLUE)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            set_rtl(p, WD_ALIGN_PARAGRAPH.RIGHT)
            r = p.add_run(value)
            set_font(r, size=8.5)
    set_table_geometry(table, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_figure(doc, number, title, filename):
    p = doc.add_paragraph()
    set_rtl(p, WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    inline = run.add_picture(str(FIGURES / filename), width=Inches(6.0))
    inline._inline.docPr.set("descr", title)
    inline._inline.docPr.set("title", title)
    cap = doc.add_paragraph()
    set_rtl(cap, WD_ALIGN_PARAGRAPH.CENTER)
    r = cap.add_run(f"الشكل {number}: {title}")
    set_font(r, size=10, bold=True, color=BLUE)
    cap.paragraph_format.space_after = Pt(8)


def configure_document(doc):
    global BULLET_NUM_ID
    numbering = doc.part.numbering_part.element
    abstract_ids = [int(x.get(qn("w:abstractNumId"))) for x in numbering.findall(qn("w:abstractNum"))]
    num_ids = [int(x.get(qn("w:numId"))) for x in numbering.findall(qn("w:num"))]
    abstract_id = max(abstract_ids, default=0) + 1
    BULLET_NUM_ID = max(num_ids, default=0) + 1
    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), str(abstract_id))
    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "singleLevel")
    abstract.append(multi)
    level = OxmlElement("w:lvl")
    level.set(qn("w:ilvl"), "0")
    start = OxmlElement("w:start")
    start.set(qn("w:val"), "1")
    fmt = OxmlElement("w:numFmt")
    fmt.set(qn("w:val"), "bullet")
    text = OxmlElement("w:lvlText")
    text.set(qn("w:val"), "•")
    jc = OxmlElement("w:lvlJc")
    jc.set(qn("w:val"), "left")
    ppr = OxmlElement("w:pPr")
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "720")
    ind.set(qn("w:hanging"), "360")
    ppr.append(ind)
    level.extend([start, fmt, text, jc, ppr])
    abstract.append(level)
    numbering.append(abstract)
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(BULLET_NUM_ID))
    abstract_ref = OxmlElement("w:abstractNumId")
    abstract_ref.set(qn("w:val"), str(abstract_id))
    num.append(abstract_ref)
    numbering.append(num)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.25)
        section.header_distance = Inches(0.49)
        section.footer_distance = Inches(0.49)
        footer = section.footer.paragraphs[0]
        footer.text = ""
        set_rtl(footer, WD_ALIGN_PARAGRAPH.CENTER)
        r = footer.add_run("التقرير التقني - ")
        set_font(r, size=9, color=RGBColor(0x66, 0x66, 0x66))
        add_page_field(footer)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:cs"), "Arial")
    normal.font.size = Pt(12)
    for name, size in (("Heading 1", 18), ("Heading 2", 15), ("Heading 3", 13)):
        style = doc.styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style._element.rPr.rFonts.set(qn("w:cs"), "Arial")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = BLUE


def clear_body(doc):
    body = doc._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def cover(doc):
    for text, size, bold in (
        ("الجمهورية العربية السورية", 16, True),
        ("المعهد العالي للعلوم التطبيقية والتكنولوجيا", 15, True),
        ("هندسة برمجيات وذكاء صنعي", 14, False),
    ):
        add_text(doc, text, bold=bold, size=size, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3):
        doc.add_paragraph()
    add_text(doc, "تقرير تقني نهائي", bold=True, size=22, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_text(doc, "وكيل ذكاء صنعي آمن ومستقل لإدارة الخوادم الافتراضية الخاصة", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_text(doc, "Safe Autonomous AI Agent for VPS Management", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(4):
        doc.add_paragraph()
    add_text(doc, "إعداد: سعيد بقدونس", size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_text(doc, "إشراف: المهندس محمد بشار الدسوقي", size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_text(doc, "السنة الرابعة - هندسة برمجيات وذكاء صنعي", size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_text(doc, "2026", size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_page_break()


def abstract_and_front(doc):
    add_heading(doc, "الخلاصة", 1)
    add_text(doc, "يصف هذا التقرير التنفيذ العملي الحالي لمنصة تراقب خوادم Linux، وتحلل التقارير، وتنسق تحقيقات محدودة بمتخصصين ديناميكيين، ثم تمرر المعالجة المقترحة عبر طبقات الأدلة والعزل والموافقة والتنفيذ المسجل. يستخدم Claude Code كمنسق إشرافي، وOllama كمزود النموذج التشغيلي، بينما تظل Python وقاعدة PostgreSQL صاحبتَي القرار التنفيذي والأمني.")
    add_text(doc, "أثبتت اختبارات المستودع الحالية سلامة حدود MCP، وتجميع الأدلة، وسياسات المخاطر، والمصادقة والصلاحيات، وإعادة المحاولة المتزامنة، والحجز ذي المفتاح idempotency، وقاطع الدارة. في المقابل، لا يخلط التقرير بين الاختبار الحتمي والقبول الحي؛ إذ توجد مفارقة موثقة في سجلات Phase 6، ولا توجد نتيجة قبول حي مستقلة لـPhase 7 داخل المستودع.")
    add_heading(doc, "Abstract", 1)
    add_text(doc, "This technical report documents the implemented Safe Autonomous AI Agent for VPS Management. The system combines bounded Linux monitoring, persisted analysis, dynamic Specialist investigations, Evidence grounding, supervised remediation, native sandbox validation, and a fail-closed autonomous policy layer. Claude Code is supervisory, Ollama is the operational provider, MCP is a bounded capability boundary, and Python owns authorization, validation, persistence, SSH safety, and execution. The current safe regression run passed 586 tests; live Phase 6 and Phase 7 evidence is explicitly separated from deterministic implementation evidence.", align=WD_ALIGN_PARAGRAPH.LEFT)
    add_heading(doc, "فهرس المحتويات", 1)
    add_toc_field(doc.add_paragraph())
    add_heading(doc, "قائمة الأشكال", 1)
    for i, title in enumerate(["مخطط النظام العام", "سياق النظام", "طبقات المكونات", "تدفق Claude وOllama وMCP وPython", "المراقبة والتحليل والتحقيق", "تنسيق المتخصصين", "المعالجة الخاضعة للإشراف", "التحقق في Sandbox", "التنفيذ الذاتي", "السياسة والحجز وعدم التكرار", "قاطع الدارة والاستعادة", "مصادقة Admin والصلاحيات", "البنية الفيزيائية", "علاقات قاعدة البيانات", "المكونات الأساسية"], 1):
        add_text(doc, f"الشكل {i}: {title}", size=10)
    add_heading(doc, "قائمة الجداول", 1)
    for i, title in enumerate(["حالة المتطلبات", "المتطلبات غير الوظيفية", "تتبع المتطلبات", "مجموعات قاعدة البيانات", "التحقق الحالي", "الاختبارات الحالية"], 1):
        add_text(doc, f"الجدول {i}: {title}", size=10)
    add_heading(doc, "المصطلحات والاختصارات", 1)
    add_table(doc, ["المصطلح", "المعنى"], [["MCP", "Model Context Protocol؛ حد الأدوات الذي يراه Claude."], ["Evidence", "دليل تشغيلي مرتبط بملكية الحادثة والخادم."], ["RAG", "استرجاع السياق من تقارير ووثائق مفهرسة."], ["RBAC", "التحكم بالوصول المبني على الدور."], ["Idempotency", "منع تنفيذ العملية غير القابلة للتغيير أكثر من مرة."], ["Sandbox", "بيئة تحقق معزولة قبل الإجراء التشغيلي."]], [2200, 7160])
    doc.add_page_break()


def chapter1(doc):
    add_heading(doc, "الفصل الأول: مواصفات المتطلبات البرمجية (SRS)", 1)
    add_heading(doc, "1.1 نطاق المشروع وأهدافه", 2)
    add_text(doc, "الهدف العملي هو تقليل زمن اكتشاف أعطال VPS وتحسين جودة القرار دون منح النموذج اللغوي صلاحية تنفيذ غير مقيدة. يشمل النطاق مراقبة الموارد والخدمات والسجلات، تحليل التقارير، التحقيق المتخصص، حفظ الأدلة، التخطيط للمعالجة، العزل، الموافقة، التنفيذ المسجل، والتحقق والاستعادة. لا يشمل هذا الإصدار إرسالاً اجتماعياً أو تنبؤاً إنتاجياً أو تعديلاً ذاتياً لكود التطبيق.")
    add_heading(doc, "1.2 أصحاب المصلحة والقيود", 2)
    for x in ["المشغّل: يراقب الخوادم ويتعامل مع نتائج المعالجة الخاضعة للإشراف.", "المطور/الموافق: يقرر الإجراءات الخطرة أو الحساسة عبر Admin المحلي.", "المراجع: يحتاج إلى تتبع المتطلبات والأدلة والاختبارات.", "النظام: ينفذ القراءة والتحقق وفق حدود Python وPostgreSQL وSSH.", "القيود: PostgreSQL/Ollama/Claude/WSL2 وهدف آمن مطلوب للقبول الحي؛ لا توجد أسرار في الوثائق."]:
        add_bullet(doc, x)
    add_heading(doc, "1.3 المتطلبات الوظيفية", 2)
    add_text(doc, "المصفوفة الكاملة في docs/requirements/functional-requirements.md. فيما يلي ملخص حالات التنفيذ:")
    add_table(doc, ["الفئة", "الحالة الحالية", "الدليل"], [["المراقبة والتحليل والتحقيق", "IMPLEMENTED", "اختبارات الوحدات والتكامل وC.14.12"], ["Evidence والمتخصصون", "IMPLEMENTED", "اختبارات الملكية والتجميع والتخزين"], ["المعالجة الخاضعة للإشراف", "IMPLEMENTED", "اختبارات Phase 5 وسجل القبول"], ["Sandbox", "PARTIAL", "العقود والاختبارات موجودة؛ دليل القبول متناقض"], ["المعالجة الذاتية", "IMPLEMENTED / live proof deferred", "اختبارات السياسة والحجز وقاطع الدارة"], ["الإشعار الاجتماعي", "DEFERRED", "لا يوجد موصل Telegram/social"], ["تحديد موضع خطأ الكود", "PARTIAL", "تشخيص grounded بلا مسار مصدر مخصص"]], [2600, 2800, 3760], "الجدول 1: ملخص المتطلبات الوظيفية")
    add_heading(doc, "1.4 تدقيق الوظائف 1-9 في دفتر الشروط", 2)
    add_text(doc, "الوظائف 1-6 و9 لها مسارات تنفيذ أو بدائل محلية موثقة. الوظيفة 7 جزئية لأن النظام يحفظ تشخيصاً وأدلة لكنه لا يثبت مسار تحديد مصدر الكود. الوظيفة 8 مؤجلة حرفياً؛ Admin المحلي بديل للموافقة وليس وسيلة تواصل اجتماعي. الوظيفة 5 مرتبطة بمفارقة دليل Phase 6، والوظيفة 6 مرتبطة بعدم وجود سجل قبول حي مستقل لـPhase 7.")
    add_heading(doc, "1.5 المتطلبات غير الوظيفية والقبول", 2)
    add_text(doc, "المتطلبات القابلة للقياس موثقة في docs/requirements/non-functional-requirements.md. من أهمها: 100% حماية الجلسات والـCSRF، صفر قدرات MCP حرة، 33/33 جدولاً، 25 أداة، تنفيذ ذاتي مكرر لا يتجاوز مرة واحدة، و586 اختباراً غير حقيقي بلا فشل.")
    add_heading(doc, "1.6 مصفوفة التتبع", 2)
    add_text(doc, "تربط docs/requirements/traceability-matrix.md كل وظيفة بالمكوّن والاختبار والدليل والحالة. لا تُرفع حالة المتطلب إلى PASS بسبب نص قديم أو قياس غير منفذ.")
    add_heading(doc, "1.7 المتطلبات التفصيلية للمراقبة والتحليل", 2)
    add_text(doc, "يجب أن تكون المراقبة قابلة للضبط من خلال ملفات محفوظة، بحيث يستطيع المشغل اختيار مجموعة أوامر قراءة معروفة لكل خادم دون تعديل كود التطبيق. ويجب أن تحمل كل نتيجة هوية الخادم ووقت التنفيذ واسم الأمر وحالته ومخرجاته المقيدة. هذا الشرط يضمن أن التقرير ليس لقطة نصية مجهولة المصدر، بل سجل تشغيلي يمكن ربطه لاحقاً بالتحليل والتحقيق.")
    add_text(doc, "يجب أن يدعم التحليل إعادة استخدام نتيجة سابقة عندما تكون هوية التقرير ومدخلاته متوافقة، وأن يميز بين فشل المزود وفشل التحليل وفشل البيانات. وعند استخدام RAG، يجب أن تكون مصادر الاسترجاع معروفة وقابلة للتتبع، وأن يعرف المستهلك ما إذا كانت النتيجة مبنية على تقرير حديث أو على وثيقة معرفة عامة. هذه التفرقة ضرورية عند مراجعة قرار اتخذ في وقت كانت فيه حالة الخادم مختلفة.")
    add_heading(doc, "1.8 المتطلبات التفصيلية للتحقيق والأدلة", 2)
    add_text(doc, "يتطلب التحقيق أن تكون تعريفات المتخصصين ديناميكية ومخزنة في قاعدة البيانات، مع اسم واضح وهدف وميزانية أدوات وسياسة صلاحية. لا يكفي تسجيل إجابة نصية من النموذج؛ بل يجب حفظ الادعاءات والملاحظات وEvidence والعلاقات بينها، مع معرفة أي Specialist أنشأ كل جزء ومن أي خادم أُخذت المعلومة.")
    add_text(doc, "كما يجب أن يرفض النظام الدليل الذي لا يطابق الحادثة أو الخادم أو نوع الملاحظة المتوقع. وعند وجود تعارض بين متخصصين، يجب أن يظهر التعارض للمستخدم بدلاً من دمجه في نتيجة ثقة زائفة. لذلك صُمم مسار الارتباط كمرحلة مستقلة تراجع المصدر والملكية والاكتمال قبل إصدار التشخيص.")
    add_heading(doc, "1.9 المتطلبات التفصيلية للمعالجة الآمنة", 2)
    add_text(doc, "المعالجة ليست امتداداً تلقائياً للتحليل. كل خطة تحتوي على إجراء مسمى وهدف وخادم وبصمة غير قابلة للتغيير، وترتبط بنتيجة تحقق أو موافقة مناسبة. وتتحقق الطبقة التنفيذية من هذه الروابط مرة أخرى عند نقطة التنفيذ، لأن صحة الخطة عند إنشائها لا تضمن بقاء السياسة أو الخادم أو نتيجة العزل دون تغيير.")
    add_text(doc, "يجب أن تمنع المنصة التنفيذ المتكرر عند إعادة إرسال الطلب أو تشغيل عاملين متزامنين. ولذلك تشمل المتطلبات مفتاح idempotency فريداً، وحجزاً قصير الأجل، وملكية قابلة للتحقق، وتثبيتاً نهائياً مشروطاً بالمالك. ويجب أن يكون الفشل الافتراضي هو عدم التنفيذ مع سجل قابل للمراجعة، لا الاستمرار بناءً على تخمين.")
    add_heading(doc, "1.10 حدود الإصدار الحالي ومعايير الإغلاق", 2)
    add_text(doc, "يُعد الإصدار الحالي ناجحاً في نطاقه عندما تعمل المراقبة والتحليل والتحقيق والمعالجة المشرفة والحواجز الذاتية ضمن الاختبارات الحتمية، ويكون المخطط وقائمة الأدوات والواجهات قابلة للتحقق. أما الإغلاق التشغيلي النهائي فيحتاج إلى توحيد أدلة القبول الحي، وإثبات بيئة Ollama وSSH وSandbox، وتسجيل النتيجة المستقلة لكل مرحلة. هذه معايير إغلاق وليست افتراضات عن حالة لم تُثبت.")


def chapter2(doc):
    add_heading(doc, "الفصل الثاني: تحليل المتطلبات (SRA)", 1)
    add_heading(doc, "2.1 الممثلون وحالات الاستخدام", 2)
    add_text(doc, "الممثلون الأساسيون هم Admin بأدواره الثلاثة، Claude Code، Python capability services، Ollama، PostgreSQL، SSH/VPS، وSandbox. حالات الاستخدام UC-001 إلى UC-026 موصوفة تفصيلاً في docs/use-cases/use-cases.md.")
    add_heading(doc, "2.2 دورة الحادثة", 2)
    add_text(doc, "تبدأ الدورة بملاحظة تشغيلية، ثم تقرير وتحليل، ثم تحقيق متخصص عند الحاجة، ثم تشخيص قائم على Evidence. بعد ذلك ينشأ مسار معالجة خاضع للإشراف أو فرع ذاتي مستقل خلف بوابة الأمان. كل فرع يحتفظ بالفشل بدلاً من تحويله إلى تنفيذ غير مسموح.")
    add_heading(doc, "2.3 نموذج الخطورة", 2)
    add_table(doc, ["القرار", "المعنى", "الشرط التقريبي"], [["AUTO_EXECUTE", "تنفيذ ذاتي محدود", "كل بوابات السياسة، Sandbox، التاريخ، Evidence، rollback، والحدود ناجحة"], ["REQUIRE_HUMAN_APPROVAL", "لا تنفيذ ذاتي", "لا سياسة أو ثقة غير كافية مع بقاء أساس آمن للمعالجة المشرفة"], ["DENY", "رفض نهائي", "خطر مرتفع، mismatch، Sandbox مفقود/فاشل، ambiguity، replay، أو circuit suspended"]], [2200, 2600, 4360], "الجدول 2: قرارات سياسة المعالجة الذاتية")
    add_heading(doc, "2.4 التحكم البشري", 2)
    add_text(doc, "الموافقة ليست زرّاً شكلياً: تسجل في قاعدة البيانات وترتبط ببصمة الخطة، وتُراجع الصلاحية وCSRF والهوية قبل التنفيذ. يستطيع Admin إيقاف/استئناف السياسة، لكن لا تستطيع الواجهة إصدار authorization يدوياً أو تجاوز التحقق.")
    add_heading(doc, "2.5 وصف تدفقات النظام", 2)
    add_text(doc, "في تدفق المراقبة، يحدد الملف المحفوظ مجموعة القياسات المسموحة، ثم تجمع القدرة النتائج وتطبعها في نموذج تقريري موحد وتحفظها. بعد ذلك يقرر التحليل ما إذا كان يمكن إعادة استخدام نتيجة موثوقة أو يحتاج إلى مزود النموذج. هذه الخطوات تفصل جمع الوقائع عن تفسيرها وتسمح بتشخيص المشكلة حتى عند تعطل المزود.")
    add_text(doc, "في تدفق التحقيق، يبدأ النظام بادعاء أو إشارة تحتاج إلى توضيح، ثم يختار المتخصصين المؤهلين بناءً على تعريفاتهم وسياساتهم. تنفذ الحلقة أدوات القراءة ضمن ميزانية محددة، وتجمع Evidence وتربطه بالحادثة، ثم تمرر النتائج إلى الارتباط والتشخيص. لا يملك المتخصص صلاحية تغيير السياسة أو استدعاء أمر غير مسجل.")
    add_text(doc, "في تدفق المعالجة الذاتية، لا يكفي أن تبدو الخطة آمنة. يجري النظام مراجعة شاملة للسياسة والتاريخ ونتيجة Sandbox وبصمات الربط، ثم يستهلك تصريحاً أحادي الاستخدام ويحجز مفتاح العملية لفترة محددة. يجري التنفيذ خارج معاملة قاعدة البيانات، وبعده لا تُثبت النتيجة إلا إذا بقيت ملكية العامل صحيحة ونجح التحقق.")
    add_heading(doc, "2.6 السيناريو التشغيلي الطبيعي", 2)
    add_text(doc, "في السيناريو الطبيعي يفتح المشغل لوحة Admin، يختار الخادم وملف المراقبة، ثم يراجع التقرير المحفوظ. إذا ظهر مؤشر غير اعتيادي، يستطيع النظام طلب تحليل سياقي واستدعاء التحقيق المتخصص ضمن الأدوات المسجلة. يرى المشغل النتيجة على شكل تشخيص وأدلة ومصادر، لا على شكل نص غير قابل للمراجعة.")
    add_text(doc, "إذا احتاجت الحالة إلى معالجة، ينشئ النظام خطة تحمل كل تفاصيل الإجراء. في المسار المشرف، يراجعها صاحب الدور المناسب ويوافق عليها، ثم تنفذ طبقة التنفيذ الإجراء المعروف وتتحقق من أثره. في المسار الذاتي، لا يظهر التنفيذ إلا إذا نجحت كل البوابات المستقلة، وتبقى النتيجة قابلة للإيقاف والمراجعة من Admin.")
    add_heading(doc, "2.7 سيناريوهات الفشل والاستجابة", 2)
    add_table(doc, ["الحالة", "الاستجابة المتوقعة", "السبب"], [["تعطل PostgreSQL", "إيقاف الطلب وتسجيل فشل البنية", "لا يجوز اتخاذ قرار دون مخزن حقيقة"], ["تعطل Ollama", "إبقاء التقرير أو التحويل إلى نتيجة غير مكتملة", "النموذج ليس سلطة تنفيذ"], ["فقدان known_hosts", "رفض اتصال SSH", "منع اتصال غير موثق"], ["تعارض الأدلة", "إظهار ambiguity وطلب مراجعة", "منع التشخيص الزائف"], ["انتهاء lease", "استرداد الحجز وفحص السجل", "منع الكتابة المتأخرة"], ["إعادة استخدام authorization", "رفض وإضافة حدث تدقيق", "التصريح أحادي الاستخدام"], ["تجاوز معدل الفشل", "تفعيل Circuit Breaker", "تقليل الضرر والمحاولات المتكررة"]], [2600, 3900, 3300], "الجدول 3: تحليل سيناريوهات الفشل")
    add_heading(doc, "2.8 المتطلبات الأمنية في التحليل", 2)
    add_text(doc, "يُعامل النموذج اللغوي كمكوّن غير موثوق في حدود التنفيذ، حتى عندما تكون جودة تحليله مرتفعة. لذلك يُحلل كل طلب على مستويين: مستوى الفهم الذي قد يستخدم Ollama أو Claude، ومستوى التفويض الذي تنفذه Python ومخازن البيانات. لا يستطيع النص الناتج من النموذج تغيير الدور أو إصدار تصريح أو توسيع قائمة الأوامر.")
    add_text(doc, "تتضمن فرضيات التهديد محاولة إعادة إرسال طلب صالح، أو تمرير خطة قديمة، أو تبديل الخادم والهدف، أو استخدام عامل متأخر بعد استرداد الحجز، أو قراءة سر من واجهة Admin. يقابل النظام هذه التهديدات بالبصمات والربط والـowner token وCSRF وRBAC والإسقاطات الآمنة وسجل التدقيق. ويُعامل فشل أي فرضية على أنه سبب رفض قابل للتفسير.")
    add_heading(doc, "2.9 معايير قابلية الاستخدام والمراجعة", 2)
    add_text(doc, "ينبغي أن يستطيع المشغل فهم ما حدث دون قراءة الشيفرة. ولهذا تعرض واجهة Admin الحالة والمالك والقرار والبصمة والنتيجة والوقت، وتعرض سبب الرفض أو التأجيل بلغة واضحة. ولا تعرض الواجهة الرموز السرية أو مفاتيح الملكية أو بيانات المصادقة، وتظل صلاحية العرض منفصلة عن صلاحية التشغيل.")
    add_heading(doc, "2.10 قرارات التصميم التحليلية", 2)
    add_text(doc, "القرار الأهم هو الفصل بين الاقتراح والتنفيذ. القرار الثاني هو استخدام مخزن مستمر للأدلة والتشخيص بدلاً من الاعتماد على سياق محادثة مؤقت. القرار الثالث هو جعل الحجز والتفويض والتثبيت حدوداً منفصلة، حتى لا تتطلب عملية خارجية طويلة معاملة قاعدة بيانات مفتوحة. هذه القرارات تقلل مخاطر التزامن وتزيد قابلية التفسير والصيانة.")


def chapter3(doc):
    add_heading(doc, "الفصل الثالث: تصميم النظام (SD)", 1)
    add_heading(doc, "3.1 مخطط النظام وسياقه", 2)
    add_figure(doc, 1, "مخطط النظام العام", "01-system-block.png")
    add_figure(doc, 2, "سياق النظام", "02-system-context.png")
    add_heading(doc, "3.2 طبقات المكونات", 2)
    add_figure(doc, 3, "طبقات المكونات والاعتماديات", "03-component-layers.png")
    add_text(doc, "الاتجاه المعماري يبدأ من الواجهات إلى القدرات، ثم إلى البنية التحتية، مع مشاركة العقود والسياسات من app/core. composition يربط النسخ الفعلية ولا يضيف مسار orchestration ثانياً.")
    add_heading(doc, "3.3 Claude Code وOllama وMCP", 2)
    add_figure(doc, 4, "تدفق Claude Code -> Ollama -> MCP -> Python", "04-claude-ollama-mcp-python.png")
    add_text(doc, "Claude يحدد ما يريد والخطوة التالية. MCP يمرر طلباً typed إلى Python. Python تتحقق من السياسة والحدود ثم تستدعي Ollama للتحليل عند الحاجة أو البنية التحتية للتنفيذ، وتعيد نتيجة منظمة.")
    add_heading(doc, "3.4 المراقبة والتحليل والتحقيق", 2)
    add_figure(doc, 5, "المراقبة والتحليل والتحقيق", "05-monitor-analysis-investigation.png")
    add_heading(doc, "3.5 المتخصصون وEvidence", 2)
    add_figure(doc, 6, "تنسيق SpecialistInvestigationLoop", "06-specialist-orchestration.png")
    add_text(doc, "الحلقة نفسها تنفذ تقييم السياسة ثم EvidenceCollectionService.collect. مخزن التحقيق المستمر يحتفظ بالمخرجات والروابط والملكية، ولا يعيد بناء نظام Evidence مستقل.")
    add_heading(doc, "3.6 المعالجة الخاضعة للإشراف وSandbox", 2)
    add_figure(doc, 7, "سلسلة المعالجة الخاضعة للإشراف", "07-supervised-remediation.png")
    add_figure(doc, 8, "سلسلة Sandbox والتحقق والاستعادة", "08-sandbox-validation.png")
    add_heading(doc, "3.7 المعالجة الذاتية والحجز", 2)
    add_figure(doc, 9, "سلسلة المعالجة الذاتية", "09-autonomous-sequence.png")
    add_figure(doc, 10, "السياسة والتفويض والحجز وعدم التكرار", "10-policy-reservation-idempotency.png")
    add_text(doc, "الـreservation قصير ولا يبقى أثناء SSH/Ollama. owner_token يمنع worker قديماً من finalize حالة worker جديد، وunique idempotency_key يمنع ازدواج التنفيذ الفيزيائي.")
    add_heading(doc, "3.8 قاطع الدارة والاستعادة", 2)
    add_figure(doc, 11, "قاطع الدارة والاستعادة", "11-circuit-recovery.png")
    add_heading(doc, "3.9 Admin وRBAC والتدقيق", 2)
    add_figure(doc, 12, "مصادقة Admin وRBAC وCSRF", "12-admin-auth-rbac.png")
    add_text(doc, "AdminAuthService يستخدم scrypt، جلسة server-side، digest للكوكي، صلاحيات viewer/operator/admin، CSRF، وأحداث تدقيق. الشاشة تعرض السجلات الآمنة ولا تعرض authorization token أو owner token.")
    add_heading(doc, "3.10 النشر وقاعدة البيانات والمكونات", 2)
    add_figure(doc, 13, "البنية الفيزيائية", "13-deployment.png")
    add_figure(doc, 14, "مخطط علاقات قاعدة البيانات", "14-database-erd.png")
    add_figure(doc, 15, "المكونات والفئات الأساسية", "15-key-components.png")
    add_heading(doc, "3.11 تصميم العقود والحدود", 2)
    add_text(doc, "تحتوي app/core على العقود التي تصف الحالات والنتائج والسياسات، بينما تطبق طبقة capabilities السلوك التشغيلي. هذا الترتيب يمنع أن تتسرب تفاصيل SQL أو SSH أو عميل النموذج إلى الواجهات. كما يسمح للاختبارات باستخدام كائنات بديلة مع بقاء شكل القرار والنتيجة ثابتاً.")
    add_text(doc, "حد MCP ليس مجرد قناة نقل؛ إنه قائمة قدرات typed ذات أسماء ومدخلات ونتائج محددة. يستطيع Claude طلب عملية معروفة، لكن Python تتحقق من المدخلات والسياق وتعيد نتيجة منظمة. أي خدمة جديدة يجب أن تمر عبر هذا الحد وأن تلتزم بسياسة التسجيل، بدلاً من إضافة طرفية عامة أو حقل نصي يحمل أوامر.")
    add_heading(doc, "3.12 تصميم طبقة التخزين", 2)
    add_text(doc, "تتبع النماذج قاعدة ملكية واضحة: الخادم يملك سياق المراقبة، التقرير يملك التحليل، التحقيق يملك الأدلة والتشخيص، والخطة تملك المعالجة والتحقق. الروابط لا تستخدم للتجميل، بل تمنع خلط نتيجة من خادم أو حادثة مع طلب آخر. وتوفر المفاتيح والفهارس القيود التي يصعب ضمانها في الذاكرة وحدها.")
    add_text(doc, "تُستخدم PostgreSQL للبيانات التشغيلية وللبحث الدلالي عبر pgvector، مع فهارس مخصصة للنطاق والمصدر والاسترجاع. أما migrations فتبقى إضافية لتجنب فقد البيانات، ويظل bootstrap قادراً على التحقق من الجداول المتوقعة. توثيق المجموعات في التقرير لا يستبدل فحص المخطط؛ بل يشرح كيف ترتبط الجداول بالوظائف.")
    add_heading(doc, "3.13 تصميم الاتساق والتزامن", 2)
    add_text(doc, "تتعامل المنصة مع التزامن على أساس أن عاملين قد يقرآن الحالة نفسها في اللحظة نفسها. ولذلك لا تعتمد على قراءة snapshot ثم كتابة metadata كاملة دون شرط. الحجز والتحديث المشروط والمالك المؤقت تجعل كل عامل يثبت فقط النتيجة التي يملك حق تثبيتها، بينما تعيد العملية المتنافسة قراءة الحالة أو ترفضها.")
    add_text(doc, "هذه القاعدة مهمة خصوصاً عند تجميع Evidence أو تحديث حالة معالجة ذاتية. يجب أن يحافظ الدمج على النتائج السابقة، وألا يستبدل قاموساً كاملاً نتيجة قراءة قديمة. أما الحقول التي تتطلب تغييراً وحيداً، مثل الحالة النهائية أو استهلاك التصريح، فتُحدّث داخل عملية ذرية مناسبة وتُراجع نتيجتها.")
    add_heading(doc, "3.14 تصميم الأمن والخصوصية", 2)
    add_text(doc, "يعتمد Admin على جلسات server-side وdigest للكوكي وكلمات مرور مع scrypt وCSRF وRBAC. وتخضع نقاط API وWeb إلى middleware مشترك حتى لا تصبح إخفاءات الواجهة بديلاً عن الحماية. وتستخدم إسقاطات العرض قائمة حقول صريحة، ولذلك لا تصل رموز التفويض أو owner token أو المفاتيح الخاصة إلى المتصفح.")
    add_text(doc, "في طبقة SSH، known_hosts جزء من هوية الهدف وليس إعداداً اختيارياً في مسار التشغيل الآمن. وتُحصر الأوامر في سجل معروف وتُمرر المعاملات وفق عقد القدرة، مع منع shell الحر. كما تسجل الأحداث الأمنية ومحاولات الرفض بما يسمح بتحليل الحادثة من دون تخزين أسرار في التقرير.")
    add_heading(doc, "3.15 تصميم القابلية للتوسع", 2)
    add_text(doc, "يمكن توسيع عدد الخوادم أو المتخصصين أو السياسات دون إضافة فرع خاص لكل حالة، لأن التعريفات والميزانيات والروابط محفوظة في قاعدة البيانات. ويجب أن يحافظ التوسع على حدود المعدل والـlease وسجل التدقيق، لا أن يلتف عليها. كما يمكن إضافة مزود نموذج أو واجهة جديدة عبر composition مع إبقاء Python صاحبة قرار التحقق.")


def chapter4(doc):
    add_heading(doc, "الفصل الرابع: التنفيذ والاختبارات", 1)
    add_heading(doc, "4.1 البيئة والتقنيات وسبب الاختيار", 2)
    add_table(doc, ["التقنية", "الاستخدام والسبب"], [["Python 3.14 + FastAPI", "تنفيذ القدرات وواجهات typed سريعة الاختبار."], ["Jinja2 + vanilla JS/CSS", "Admin خفيف يحافظ على الفصل بين العرض وbackend authority."], ["PostgreSQL + pgvector", "تخزين معاملات وأدلة وفهارس RAG قابلة للتدقيق."], ["SQLAlchemy/SQLModel + psycopg", "نماذج ومستودعات typed مع اتصال PostgreSQL."], ["Ollama", "مزود محلي/تشغيلي للنموذج والتحليل والتضمين."], ["Claude Code + MCP", "إشراف وأدوات typed بدلاً من صلاحية تنفيذ حرة."], ["SSH known_hosts", "وصول VPS قابل للتحقق ومحصور بأوامر مسجلة."], ["pytest/TestClient", "تغطية حتمية قابلة للإعادة للسياسات والواجهات والأمان."]], [2600, 6760], "الجدول 3: التقنيات الرئيسية")
    add_heading(doc, "4.2 تنفيذ قاعدة البيانات", 2)
    add_text(doc, "يُنشئ bootstrap الجداول والنماذج، يضمن pgvector، ينشئ فهارس GIN/scope/HNSW، ثم يطابق EXPECTED_TABLES. عدد الجداول الحالي 33. مجموعات الجداول موثقة في docs/architecture/data-architecture.md، وSQL migrations تبقى additive.")
    add_heading(doc, "4.3 تنفيذ التكامل", 2)
    add_text(doc, "ينفذ composition wiring المستودعات ثم الخدمات ثم runtime. Admin وMCP يستدعيان القدرات نفسها؛ لا يوجد Python orchestration بديل يكرر Claude. Ollama لا يملك صلاحية التنفيذ؛ SSH لا يُستدعى من Claude مباشرة.")
    add_heading(doc, "4.4 Admin UI", 2)
    add_text(doc, "اكتملت الشاشات التشغيلية والسياسات والحجوزات والتفويضات والتدقيق. apiRequest موحد ويضيف CSRF ويحول non-2xx إلى خطأ منظم دون reload فاشل. صلاحيات الواجهة usability فقط، والـmiddleware هو authority.")
    add_heading(doc, "4.5 شرح تنفيذي لدورة المراقبة والتحقيق", 2)
    add_text(doc, "تبدأ الدورة من ملف مراقبة محفوظ في قاعدة البيانات، وليس من تعليمات حرة يكتبها النموذج. يحدد الملف الخادم المستهدف، والأوامر المسجلة، وترتيب التنفيذ، والمهلة، وحدود المخرجات. تنفذ طبقة القدرة هذه الأوامر ضمن سياق الخادم المصرح به، ثم تحفظ نتيجة كل أمر وحالة التقرير ووقت التنفيذ حتى يصبح التشخيص قابلاً للمراجعة وإعادة البناء.")
    add_text(doc, "بعد حفظ التقرير، تبحث طبقة التحليل عن نتيجة سابقة قابلة لإعادة الاستخدام قبل طلب تحليل جديد. وعند الحاجة إلى النموذج، يمرر السياق عبر استرجاع RAG ومصادر محددة، بينما تبقى هوية الخادم والتقرير والقيود التشغيلية مرتبطة بالطلب. لا تمنح إجابة Ollama صلاحية تنفيذ؛ فهي تفسر الملاحظات وتقترح مسار التحقيق فقط، وتظل السجلات المحفوظة والمحددات البرمجية هي مصدر الحقيقة.")
    add_text(doc, "عندما تشير النتيجة إلى أن التشخيص يحتاج إلى تحقيق متخصص، يمرر InvestigationRouter الادعاءات إلى SpecialistInvestigationLoop. الحلقة تقيم سياسة كل Specialist وتعتمد تعريفه المحفوظ في قاعدة البيانات، ثم تجمع الملاحظات من أدوات القراءة المسموح بها. وتجمع Evidence فعلياً داخل EvidenceCollectionService.collect، مع ربط كل دليل بالحادثة والخادم والمصدر والزمن، ثم تحفظ النتيجة قبل مرحلة الارتباط بين الأدلة.")
    add_text(doc, "تجري مرحلة الارتباط مقارنة بين نتائج المتخصصين وتكشف التعارضات أو نقص الأدلة، ثم تنتج غلاف تشخيص موحداً يوضح الادعاء ودرجة الثقة ومبرراته. هذا الفصل يمنع أن تتحول مخرجات Specialist إلى أمر مباشر، ويجعل أي قرار إصلاحي لاحقاً مبنياً على نتيجة قابلة للتدقيق بدلاً من نص محادثة عابر.")
    add_heading(doc, "4.6 شرح تنفيذي لدورة المعالجة الذاتية", 2)
    add_text(doc, "المعالجة الذاتية طبقة منفصلة عن المراقبة والتحقيق. تبدأ بقرار حتمي يراجع تفعيل السياسة، ونطاق الخادم، ونوع الإجراء، وبصمة الخطة، ونتيجة Sandbox، وسجل المحاولات، وحدود المعدل وفترة التهدئة وقاطع الدارة. أي نقص في هذه المدخلات أو أي تعارض في الربط يؤدي إلى قرار رفض مغلق، ولا يستطيع النموذج تجاوز هذه النتيجة.")
    add_text(doc, "قبل التنفيذ الخارجي، تصدر طبقة التفويض تصريحاً أحادي الاستخدام مرتبطاً بمعرف القرار وإصدار السياسة وبصمة الخطة والخادم والإجراء والهدف ونتيجة التحقق المعزول. استهلاك التصريح عملية مقفلة على مستوى قاعدة البيانات؛ لذلك لا يمكن للطلب نفسه إعادة استخدام تصريح مستهلك أو إنشاء تنفيذ ثانٍ لمجرد إعادة إرسال الرسالة.")
    add_text(doc, "تحجز مستودعات المعالجة مفتاح idempotency وفترة lease قصيرة في معاملة مستقلة. هذا الحجز يمنع عاملين متزامنين من امتلاك التنفيذ نفسه، ولا تبقى المعاملة مفتوحة أثناء اتصال SSH أو Ollama. بعد الحجز ينفذ العامل الإجراء المسمى الموجود في النظام، ثم يتحقق من النتيجة ويجمع سجل التنفيذ والتحقق وأي تراجع مطلوب.")
    add_text(doc, "يتم الإنهاء الذري مع owner token؛ فإذا انتهت ملكية الحجز أو استعادها عامل تعافٍ، يفشل العامل القديم في تثبيت نتيجته. وبهذا تعالج المنصة خطر الكتابة المتأخرة وLost Update، وتفصل بوضوح بين الحجز القصير والتنفيذ الخارجي والتثبيت النهائي. كما تسجل كل حدود القرار والتفويض والحجز والتنفيذ والتحقق والتراجع في سجل تدقيق مستقل.")
    add_text(doc, "يراقب Circuit Breaker الإخفاقات المتتابعة والتهدئة والحالة المعطلة، ويمنع استمرار المحاولات عند تجاوز الحدود. أما التعافي فيعيد فحص الحجز والتصريح وسجل التنفيذ قبل الاستئناف، ولا يعيد إصدار تفويض جديد أو يخمن أن عملية كتابة نجحت بعد انقطاع الاتصال. لذلك تبقى السلامة أهم من إكمال العملية عند وجود حالة غير محسومة.")
    add_heading(doc, "4.7 شرح تنفيذ الاختبارات والتكامل", 2)
    add_text(doc, "تغطي الاختبارات طبقات النظام من العقود الصغيرة إلى نقاط التكامل. تتحقق اختبارات الوحدات من قرارات السياسة، وبصمات الخطط، وحدود الأوامر، وتجميع Evidence، وسلوك قاطع الدارة. وتتحقق اختبارات المستودعات من التزامن، وملكية الحجز، واستهلاك التفويض، ومنع إعادة التشغيل، بينما تتحقق اختبارات الواجهات من المصادقة وCSRF وRBAC وإخفاء الأسرار.")
    add_text(doc, "تُشغّل اختبارات PostgreSQL والتحقق من المخطط في بيئة منفصلة عن الاختبارات الحتمية المحلية. ويشمل التحقق وجود pgvector والفهارس المخصصة وعدد الجداول المتوقع. أما اختبارات real acceptance فتظل opt-in لأنها تحتاج Ollama وSSH وبيانات تشغيل حقيقية؛ عدم توفر هذه البيئة لا يُحوّل الاختبار إلى نجاح اصطناعي ولا يغير نتيجة regression الآمن.")
    add_text(doc, "تشمل الخطة static/compile، وحدات السياسات والعقود، مستودعات SQLite، PostgreSQL schema، APIs وAdmin TestClient، MCP boundary، الأمن السلبي، concurrency/recovery، circuit breaker، وreal acceptance منفصل. لا تخلط الخطة بين 586 اختباراً حتمياً والقبول الحي، لأن لكل فئة دلالة مختلفة وبيئة تشغيل مختلفة.")
    add_heading(doc, "4.8 نتائج الاختبار الحالية", 2)
    add_table(doc, ["الفحص", "النتيجة"], [["Full non-real regression", "586 passed, 0 failed, 0 skipped, 1 warning / 24.48s"], ["Database", "33/33; pgvector OK; 3/3 custom RAG indexes"], ["MCP", "25 tools"], ["Routes", "99 total / 73 OpenAPI / 26 web-only"], ["Compileall", "PASS"], ["Git diff check", "PASS"]], [3400, 5960], "الجدول 4: النتائج الحالية")
    add_heading(doc, "4.9 تفسير نتائج القبول المرحلي", 2)
    add_text(doc, "سجل المشروع يصف Phase 5 بأنه مغلق بعد قبول المختبر غير الإنتاجي. Phase 6 له تنفيذ واختبارات، لكن `artifacts/evaluation/phase6_readiness.json` يعلن PASS بينما التقرير النهائي واختبار القبول الافتراضي يعلنان BLOCKED_BY_SANDBOX_RUNTIME. لا يوجد artifact مستقل لقبول Phase 7 الحي رغم اكتمال الحواجز الحتمية. لذلك يعرض التقرير هذا كقيد توثيقي صريح لا كنجاح مختلق.")
    add_heading(doc, "4.10 قابلية الصيانة والتشغيل", 2)
    add_text(doc, "تعتمد قابلية الصيانة على فصل واضح بين العقود الأساسية، والقدرات، والمستودعات، وواجهات MCP وAdmin، وطبقة composition. هذا الفصل يسمح بتغيير مزود النموذج أو قناة العرض دون نقل صلاحية التنفيذ إلى الطبقة الجديدة. كما أن وجود أدوات الجرد والتحقق، وملفات Mermaid القابلة للتحرير، ومصفوفة التتبع يقلل اعتماد المشروع على معرفة ضمنية غير موثقة.")
    add_text(doc, "تشغيلياً، يجب أن يبدأ أي نشر بفحص المتغيرات السرية، واتصال PostgreSQL، وتوافق المخطط، ووجود known_hosts، ثم التحقق من Ollama وMCP عند الحاجة. وتُقرأ سجلات التدقيق مع سجلات التنفيذ والتحقق والتراجع عند تحليل حادثة، مع عدم كشف كلمات المرور أو الرموز أو مفاتيح SSH في إسقاطات Admin. هذه الإجراءات لا تمنح صلاحية جديدة، بل تحافظ على الحدود الموجودة.")
    add_heading(doc, "4.11 القيود والعمل المؤجل", 2)
    add_text(doc, "الإشعار الاجتماعي، تنبؤ الأعطال، الصيانة الاستباقية، الاتجاهات طويلة الأمد، التعلم من قرارات المطور، مقارنة OpenClaw، benchmark إنتاجي، قبول clean-host، وتسوية أدلة Phase 6/7 مدرجة في docs/roadmap/deferred-requirements.md وfuture-work.md.")
    add_heading(doc, "4.12 تفاصيل تنفيذ المراقبة", 2)
    add_text(doc, "تنفذ خدمة المراقبة ملفاً معروفاً بدلاً من قبول نص أمر من المستخدم أو النموذج. يحتوي الملف على مجموعة الأوامر والمهل والحدود، وتُحفظ كل نتيجة منفردة قبل تكوين التقرير المجمع. هذا التصميم يجعل فشل أمر واحد قابلاً للتمييز عن فشل الاتصال أو فشل التقرير، ويمنع فقدان المعلومات عند توقف العملية في منتصفها.")
    add_text(doc, "تُمرر النتائج إلى طبقة التطبيع التي توحد الحالات والأزمنة والمخرجات، مع الحفاظ على النص الخام ضمن حدود الحجم المسموح. ثم ينشأ تقرير مستمر يمكن عرضه في Admin وربطه بالتحليل والتحقيق. ويستطيع المشغل مقارنة تقريرين لنفس الخادم دون الاعتماد على ذاكرة جلسة Claude.")
    add_heading(doc, "4.13 تفاصيل تنفيذ التحليل وRAG", 2)
    add_text(doc, "يستخدم التحليل التقرير المحفوظ كسياق أساسي، ثم يضيف مصادر RAG عند الحاجة. يميز النظام بين مصدر معرفة ثابت، وتقرير تشغيل حديث، ونتيجة تحقيق متخصصة، لأن وزن كل نوع يختلف عند تفسير الحادثة. وتسجل علاقة المصدر بالتحليل حتى يمكن للمراجع معرفة سبب ظهور معلومة معينة في النتيجة.")
    add_text(doc, "عند تعطل Ollama أو فشل parsing، لا تتحول النتيجة إلى قرار تنفيذي. تُحفظ حالة الفشل وسببها، ويمكن إبقاء التقرير متاحاً للمراجعة أو طلب إعادة تحليل لاحق. هذا السلوك ينسجم مع مبدأ أن النموذج يساعد في التفسير ولا يملك سلطة الوصول إلى SSH أو قاعدة البيانات التنفيذية.")
    add_heading(doc, "4.14 تفاصيل تنفيذ التحقيق المتخصص", 2)
    add_text(doc, "تبدأ حلقة التحقيق من قائمة claims، ثم تجلب تعريفات Specialists الفعالة من قاعدة البيانات. لكل متخصص هدف وميزانية وسياسة وأدوات مسموحة، وتُرفض التعريفات المتعارضة أو غير المعروفة قبل التنفيذ. هذا يمنع أن يضيف النموذج متخصصاً افتراضياً بصلاحيات لم يسجلها النظام.")
    add_text(doc, "تستدعي الحلقة EvidenceCollectionService.collect بعد تقييم السياسة، ولذلك لا يوجد نظام أدلة ثانٍ يجب إعادة بنائه. ما يلزم هو حفظ ناتج الحلقة داخل مخزن التحقيق المستمر مع المصدر والملكية والوقت، ثم استخدام نفس الدليل في الارتباط والعرض والتدقيق. هذه المحافظة على مصدر واحد تقلل اختلاف النتائج بين مسار التحليل ومسار التحقيق.")
    add_heading(doc, "4.15 تفاصيل تنفيذ المعالجة المشرفة", 2)
    add_text(doc, "المعالجة المشرفة تبدأ بخطة وبصمة وإجراء مسمى، ثم تمر عبر Sandbox أو موافقة وفق مستوى الخطر. موافقة المستخدم مرتبطة بالخطة الحالية ولا تكفي إذا تغير الخادم أو الهدف أو الإجراء. بعد التنفيذ تحفظ النتيجة والتحقق والتراجع، ويمكن عرض التسلسل الكامل في Admin.")
    add_text(doc, "التحقق بعد التنفيذ ليس رسالة نجاح من SSH فقط؛ بل نتيجة تحقق مستقلة مرتبطة بالخطة والهدف. عند فشل التحقق، ينتقل المسار إلى الاستعادة أو حالة غير ناجحة، ولا يعلن نجاحاً جزئياً على أنه حل. كما تسجل أحداث الموافقة والتنفيذ والتحقق والتراجع لتوفير خط زمني كامل للحادثة.")
    add_heading(doc, "4.16 تفاصيل تنفيذ المعالجة الذاتية والتعافي", 2)
    add_text(doc, "تُحفظ قرارات السياسة والإصدارات والتفويضات والحجوزات وحالة التشغيل في جداول منفصلة حتى يمكن التمييز بين قرار السماح، والتصريح الذي استُهلك، والتنفيذ الذي جرى، والنتيجة التي تحققت. هذا الفصل يمنع أن تُفسر حالة واحدة على أنها دليل كامل على نجاح المسار.")
    add_text(doc, "عند انقطاع عامل بعد الحجز أو أثناء التنفيذ، يفحص مسار التعافي lease والحالة والتصريح وسجل التنفيذ قبل اتخاذ أي خطوة. إذا كانت الملكية منتهية، يمكن لعامل جديد استرداد الحجز ضمن الشروط؛ وإذا كان التصريح مستهلكاً أو التنفيذ غير محسوم، يتوقف المسار ويطلب مراجعة. لا يعاد تنفيذ عملية خطرة بناءً على غياب سجل النجاح وحده.")
    add_heading(doc, "4.17 دليل التشغيل والصيانة", 2)
    add_text(doc, "يتطلب تشغيل البيئة ضبط متغيرات الاتصال وقاعدة البيانات ومسار known_hosts ومفاتيح SSH خارج المستودع. وبعد الإقلاع، يفحص المشغل المخطط وقائمة الأدوات وصحة الخدمات قبل استخدام أي وظيفة حقيقية. وتبقى ملفات real acceptance اختيارية حتى لا تتصل الاختبارات العادية بخادم أو نموذج حقيقي.")
    add_text(doc, "تُراجع سجلات التدقيق دورياً للبحث عن رفض متكرر أو انتهاء حجوزات أو تعارضات في الأدلة أو ارتفاع إخفاقات مزود النموذج. وتُستخدم أدوات الجرد لتحديث عدد المسارات والأدوات والجداول عند إضافة وظيفة. أما الوثائق التاريخية فلا تُعامل كحالة تشغيلية حالية إلا بعد توثيق قرار تحديثها.")


def appendices(doc):
    add_heading(doc, "الخاتمة التقنية", 1)
    add_text(doc, "النسخة الحالية تبني حدوداً تشغيلية واضحة: Claude للإشراف، Ollama للنموذج، MCP للأدوات المسموحة، وPython للتنفيذ والتحقق والتدقيق. يثبت الاختبار الحتمي حماية RBAC/CSRF، حدود MCP، Evidence، الحجز وعدم التكرار، الاستعادة، وقاطع الدارة، كما يثبت تحقق قاعدة البيانات 33/33 وعدد أدوات MCP 25. تبقى بعض وظائف دفتر الشروط جزئية أو مؤجلة، وتبقى حالة القبول الحي لـPhase 6 غير متسقة وPhase 7 غير موثقة في artifact مستقل.")
    add_heading(doc, "الملحق أ: قائمة الجداول الكاملة", 1)
    add_table(doc, ["المجموعة", "الجداول"], [["Monitoring", "servers; monitor_commands; monitoring_profiles; monitoring_profile_commands; monitoring_reports; command_executions"], ["Analysis/RAG", "report_analyses; report_analysis_sources; report_retrieval_documents; knowledge_sources; knowledge_documents; knowledge_chunks"], ["Investigation", "investigations; investigation_specialist_candidates; specialist_definitions; agent_jobs"], ["Supervised remediation", "remediation_plans; remediation_sandbox_results; remediation_approvals; remediation_executions; remediation_verifications; remediation_rollbacks; remediation_evidence; remediation_audit_events; sandbox_validations"], ["Autonomous", "autonomous_remediation_policies; autonomous_policy_decisions; autonomous_authorizations; autonomous_policy_execution_reservations; autonomous_policy_runtime_state; autonomous_policy_audit_events"], ["Admin", "admin_users; admin_sessions; admin_auth_audit_events"]], [2400, 6960], "الجدول 5: جرد الجداول وعددها 33")
    add_text(doc, "توضح هذه القائمة أن قاعدة البيانات ليست مخزناً عاماً لسياق النموذج. جداول المراقبة تحفظ الوقائع، وجداول التحليل تحفظ تفسيراً مرتبطاً بالمصدر، وجداول التحقيق تحفظ دورة الأدلة، بينما تفصل جداول المعالجة بين الخطة والموافقة والتنفيذ والتحقق والتراجع. أما جداول السياسة الذاتية فتحتفظ بسجل مستقل للقرار والتفويض والحجز والحالة والتدقيق.")
    add_heading(doc, "الملحق أ-1: معنى مجموعات البيانات", 2)
    add_table(doc, ["المجموعة", "الغرض", "ضابط السلامة"], [["Monitoring", "حفظ تقارير الخادم ونتائج الأوامر", "الأوامر مسجلة والمخرجات محدودة"], ["Analysis/RAG", "تفسير التقارير وربط المصادر", "المصدر والهوية محفوظان"], ["Investigation", "إدارة المتخصصين والأدلة", "الملكية وميزانية الأدوات"], ["Supervised", "المعالجة والموافقة والتحقق", "بصمة وخطر واستعادة"], ["Autonomous", "التنفيذ المقيد والتعافي", "تفويض أحادي وحجز وowner token"], ["Admin", "الهوية والجلسات والتدقيق", "scrypt وCSRF وRBAC"]], [2300, 4300, 2760], "الجدول 6: دلالة مجموعات قاعدة البيانات")
    add_heading(doc, "الملحق ب: مسارات الواجهات", 1)
    add_text(doc, "المخزون الفعلي generated by tools/dev/list_routes.py: 99 route إجمالاً، 73 ضمن OpenAPI، و26 Web-only. يشمل Admin routes الجديدة للسياسات والحالات والحجوزات والتفويضات والتدقيق، وAPI `/api/admin/auth-audit`.")
    add_text(doc, "تقسم المسارات إلى واجهات API قابلة للاكتشاف عبر OpenAPI ومسارات Web مرتبطة بالجلسة والقوالب. هذا الفرق مهم عند الاختبار؛ فاختبار API يراجع العقود والرموز والاستجابات، بينما يراجع اختبار Web الجلسة وCSRF والقالب وإخفاء العناصر بحسب الدور. لا تعني زيادة عدد المسارات زيادة في الصلاحية؛ فالمسارات كلها تستدعي خدمات backend التي تطبق الحدود.")
    add_heading(doc, "الملحق ب-1: عينة حالات الاستخدام", 2)
    add_table(doc, ["المعرف", "الحالة", "الممثل", "النتيجة"], [["UC-001", "تشغيل مراقبة خادم", "Admin/Claude", "تقرير محفوظ مع نتائج الأوامر"], ["UC-005", "تحليل تقرير سابق", "Python/Ollama", "تحليل مربوط بمصادره"], ["UC-009", "طلب تحقيق متخصص", "InvestigationRouter", "Evidence وتشخيص مستمران"], ["UC-013", "إنشاء خطة معالجة", "Remediation service", "خطة ذات بصمة ومخاطر"], ["UC-017", "موافقة بشرية", "Operator/Admin", "موافقة مرتبطة بالخطة"], ["UC-019", "تنفيذ ذاتي آمن", "Autonomous worker", "تنفيذ واحد أو رفض مغلق"], ["UC-022", "استعادة حجز", "Recovery worker", "استئناف مشروط أو توقف آمن"], ["UC-025", "إدارة Admin", "Admin", "إدارة دون كشف أسرار"]], [1400, 3100, 2500, 2360], "الجدول 7: عينة حالات الاستخدام الأساسية")
    add_heading(doc, "الملحق ج: مصادر التحقق", 1)
    for x in ["المصدر البرمجي: app/core، app/capabilities، app/runtime/claude، app/interfaces، app/infrastructure، app/composition.", "الاختبارات: tests/، مع استبعاد tests/real_runtime من regression العادي.", "التحقق: tools/bootstrap_database.py، tools/dev/list_routes.py، ProjectMcpToolBoundary.list_tools().", "الوثائق المرجعية: دفتر الشروط PDF، القالب 1-Report-Template.docx، والتقرير العربي القديم كمصدر مصطلحات فقط.", "الهوية الطلابية الموثقة في هذه النسخة: سعيد بقدونس."]:
        add_bullet(doc, x)
    add_heading(doc, "الملحق د: مصفوفة الاختبارات", 1)
    add_table(doc, ["المجال", "ما الذي يثبت", "النتيجة الحالية"], [["العقود والسياسات", "حالات القرار والحدود والربط", "مغطى في regression"], ["المستودعات", "الذرية والملكية وعدم التكرار", "مغطى في اختبارات التزامن"], ["الأمن", "RBAC وCSRF وعدم كشف الأسرار", "PASS"], ["MCP", "قائمة الأدوات والمدخلات المنظمة", "25 أداة"], ["قاعدة البيانات", "الجداول والفهارس وpgvector", "33/33 و3 فهارس"], ["Admin", "الجلسات والصفحات والإسقاطات", "مغطى في TestClient"], ["Real acceptance", "Ollama وSSH وSandbox الحقيقية", "opt-in؛ لا تُشغل ضمن regression"]], [2300, 4700, 2360], "الجدول 8: مصفوفة الاختبارات ونتائجها")
    add_text(doc, "تُقرأ نتيجة 586 اختباراً مع هذا التفصيل: هي دليل على سلامة السلوك الحتمي في البيئة الآمنة، وليست بديلاً عن قبول خارجي يتطلب خدمات حقيقية. ولذلك يحافظ التقرير على فصل واضح بين ما يمكن إعادته محلياً وما يحتاج بنية تشغيلية وأسراراً وهدفاً آمناً.")
    add_heading(doc, "الملحق هـ: قاموس المكونات", 1)
    for x in ["app/core: العقود والإعدادات والسياسات والحالات الأساسية.", "app/capabilities: قدرات المراقبة والتحليل والتحقيق والمعالجة، وهي موضع السلطة التنفيذية.", "app/infrastructure: PostgreSQL والنماذج والمستودعات وSSH وOllama.", "app/interfaces: واجهات MCP وAdmin وAPI، مع بقاء backend authority.", "app/runtime/claude: عقد التشغيل الإشرافي وتدفق الحوار المنظم.", "app/composition: تركيب المستودعات والخدمات والruntime في حاوية واحدة.", "tests: اختبارات حتمية واختبارات opt-in للبيئات الخارجية.", "tools/dev: أدوات جرد المسارات وتزامن الوثائق والتحقق وبناء التقرير."]:
        add_bullet(doc, x)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document(str(TEMPLATE))
    clear_body(doc)
    configure_document(doc)
    cover(doc)
    abstract_and_front(doc)
    add_text(doc, "ملاحظة منهجية: هذا التقرير تقني تنفيذي. لم تُنسخ الدراسة المرجعية أو الفصول النظرية من التقرير العربي القديم.", bold=True, size=11)
    chapter1(doc)
    chapter2(doc)
    chapter3(doc)
    chapter4(doc)
    appendices(doc)
    doc.core_properties.title = "التقرير التقني لوكيل ذكاء صنعي آمن ومستقل لإدارة الخوادم الافتراضية الخاصة"
    doc.core_properties.subject = "Implementation and testing report"
    doc.core_properties.author = "سعيد بقدونس"
    doc.core_properties.comments = "Generated from 1-Report-Template.docx; Arabic implementation-focused technical report."
    doc.save(str(OUT))
    print(str(OUT).encode("ascii", "backslashreplace").decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
