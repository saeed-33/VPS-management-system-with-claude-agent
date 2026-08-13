from io import BytesIO
from pathlib import Path
from typing import Iterable

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _rtl(value: object) -> str:
    text = str(value if value is not None else "-")
    return get_display(arabic_reshaper.reshape(text))


class ReportPdfService:
    def __init__(
        self,
        *,
        font_path: Path,
    ) -> None:
        if not font_path.exists():
            raise FileNotFoundError(
                f"PDF font was not found: {font_path}"
            )
        self._font_name = "ApplicationArabic"
        pdfmetrics.registerFont(
            TTFont(
                self._font_name,
                str(font_path),
            )
        )

    def build(
        self,
        *,
        report,
        analysis,
        sources: Iterable,
    ) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=f"Monitoring report {report.id}",
        )

        styles = getSampleStyleSheet()
        normal = ParagraphStyle(
            "ArabicNormal",
            parent=styles["BodyText"],
            fontName=self._font_name,
            fontSize=9,
            leading=14,
            alignment=TA_RIGHT,
        )
        heading = ParagraphStyle(
            "ArabicHeading",
            parent=styles["Heading2"],
            fontName=self._font_name,
            fontSize=14,
            leading=18,
            alignment=TA_RIGHT,
            spaceAfter=8,
        )

        story = [
            Paragraph(
                _rtl(f"تقرير المراقبة رقم {report.id}"),
                heading,
            ),
            Spacer(1, 5 * mm),
        ]

        info = [
            [_rtl("الخادم"), _rtl(report.server_name)],
            [_rtl("العنوان"), _rtl(report.server_host)],
            [_rtl("الحالة"), _rtl(report.status)],
            [_rtl("بداية التنفيذ"), _rtl(report.started_at)],
            [_rtl("نهاية التنفيذ"), _rtl(report.finished_at)],
            [_rtl("الأوامر الناجحة"), report.commands_succeeded],
            [_rtl("الأوامر الفاشلة"), report.commands_failed],
        ]
        info_table = Table(
            info,
            colWidths=[55 * mm, 105 * mm],
        )
        info_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), self._font_name),
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([info_table, Spacer(1, 7 * mm)])

        story.append(Paragraph(_rtl("تحليل الذكاء الاصطناعي"), heading))
        if analysis is None:
            story.append(Paragraph(_rtl("لا يوجد تحليل متاح."), normal))
        else:
            story.extend(
                [
                    Paragraph(
                        _rtl(
                            f"الحالة العامة: "
                            f"{analysis.health_status or '-'}"
                        ),
                        normal,
                    ),
                    Paragraph(
                        _rtl(
                            f"المصدر: {analysis.analysis_source}"
                        ),
                        normal,
                    ),
                    Paragraph(
                        _rtl(analysis.summary or "لا يوجد ملخص"),
                        normal,
                    ),
                ]
            )
            for issue in analysis.issues or []:
                story.append(
                    Paragraph(
                        _rtl(
                            f"- {issue.get('title', '-')}: "
                            f"{issue.get('description', '')}"
                        ),
                        normal,
                    )
                )

        story.extend(
            [
                Spacer(1, 7 * mm),
                Paragraph(_rtl("مصادر التحليل"), heading),
            ]
        )
        source_list = list(sources)
        if not source_list:
            story.append(
                Paragraph(
                    _rtl("لا توجد مصادر مسجلة."),
                    normal,
                )
            )
        else:
            for source in source_list:
                score = (
                    f"{source.similarity_score:.2%}"
                    if source.similarity_score is not None
                    else "-"
                )
                story.append(
                    Paragraph(
                        _rtl(
                            f"- {source.title} | "
                            f"النوع: {source.source_type} | "
                            f"الاستراتيجية: "
                            f"{source.retrieval_strategy or '-'} | "
                            f"التشابه: {score} | "
                            f"دخل في السياق: "
                            f"{'نعم' if source.used_in_prompt else 'لا'}"
                        ),
                        normal,
                    )
                )

        story.extend(
            [
                PageBreak(),
                Paragraph(_rtl("نتائج التعليمات"), heading),
            ]
        )
        for execution in report.executions:
            story.append(
                Paragraph(
                    _rtl(
                        f"{execution.execution_order}. "
                        f"{execution.command_name}"
                    ),
                    heading,
                )
            )
            output = execution.stdout or execution.stderr or (
                execution.error_message or "-"
            )
            story.append(Paragraph(_rtl(output[:8000]), normal))
            story.append(Spacer(1, 4 * mm))

        document.build(story)
        return buffer.getvalue()
