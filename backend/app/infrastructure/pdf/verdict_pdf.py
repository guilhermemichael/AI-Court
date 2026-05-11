from pathlib import Path
from textwrap import wrap

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.infrastructure.db.models import CaseModel, VerdictModel


class VerdictPdfRenderer:
    def __init__(self, output_dir: Path, public_base_url: str) -> None:
        self.output_dir = output_dir
        self.public_base_url = public_base_url.rstrip("/")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render(self, case: CaseModel, verdict: VerdictModel) -> Path:
        path = self.output_dir / f"verdict-{case.id}.pdf"
        pdf = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        pdf.setTitle(f"Sentenca AI Court - {case.title}")

        pdf.setFillColor(colors.HexColor("#ece2cc"))
        pdf.rect(12 * mm, 12 * mm, width - 24 * mm, height - 24 * mm, stroke=0, fill=1)

        pdf.setFillColor(colors.HexColor("#b8924a"))
        pdf.rect(18 * mm, height - 38 * mm, width - 36 * mm, 12 * mm, stroke=0, fill=1)

        pdf.setFillColor(colors.black)
        pdf.setFont("Times-Bold", 16)
        pdf.drawCentredString(width / 2, height - 30 * mm, "REPUBLICA FEDERATIVA DO APARTAMENTO")
        pdf.setFont("Times-Bold", 18)
        pdf.drawCentredString(
            width / 2, height - 41 * mm, "SUPREMO TRIBUNAL DAS INTELIGENCIAS ARTIFICIAIS"
        )

        pdf.setFillColor(colors.HexColor("#ceb88a"))
        pdf.setFont("Times-Bold", 52)
        pdf.drawCentredString(width / 2, height / 2, "TRANSITADO")
        pdf.drawCentredString(width / 2, height / 2 - 20, "EM JULGADO")

        pdf.setFillColor(colors.black)
        pdf.setFont("Times-Roman", 11)
        pdf.drawString(22 * mm, height - 58 * mm, f"Processo no: {case.id}")
        pdf.drawString(22 * mm, height - 66 * mm, f"Caso: {case.title}")
        pdf.drawString(22 * mm, height - 74 * mm, f"Autor: {case.plaintiff_name}")
        pdf.drawString(22 * mm, height - 82 * mm, f"Reu: {case.defendant_name}")
        pdf.drawString(
            22 * mm, height - 90 * mm, f"Indice de culpa: {float(verdict.guilt_index):.2f}"
        )
        pdf.drawString(22 * mm, height - 98 * mm, f"Vencedor tecnico: {verdict.winner}")

        qr_code = qr.QrCodeWidget(f"{self.public_base_url}/api/v1/cases/{case.id}")
        bounds = qr_code.getBounds()
        size = 28 * mm
        width_scale = size / (bounds[2] - bounds[0])
        height_scale = size / (bounds[3] - bounds[1])
        drawing = Drawing(size, size, transform=[width_scale, 0, 0, height_scale, 0, 0])
        drawing.add(qr_code)
        renderPDF.draw(drawing, pdf, width - 48 * mm, height - 106 * mm)

        cursor_y = height - 115 * mm
        cursor_y = self._draw_section(
            pdf, "DOS FATOS", [case.plaintiff_argument, case.defendant_argument], cursor_y
        )
        cursor_y = self._draw_section(pdf, "DO MERITO", [verdict.reasoning], cursor_y)
        cursor_y = self._draw_section(
            pdf,
            "DA PENA",
            [
                verdict.sentence,
                verdict.compensation_order or "Sem ordem compensatoria adicional.",
            ],
            cursor_y,
        )
        self._draw_section(
            pdf,
            "DISPOSITIVO FINAL",
            [
                "Este documento e uma simulacao humoristica gerada por IA.",
                "Nao possui validade juridica real.",
                "Assinatura digital ficticia: Ministro Relator da Cozinha.",
            ],
            cursor_y,
        )

        pdf.setFillColor(colors.HexColor("#8d1d1d"))
        pdf.setFont("Times-Bold", 22)
        pdf.drawRightString(width - 22 * mm, 24 * mm, "SENTENCA TRANSITADA EM JULGADO")
        pdf.save()
        return path

    def _draw_section(
        self, pdf: canvas.Canvas, title: str, paragraphs: list[str], start_y: float
    ) -> float:
        pdf.setFillColor(colors.HexColor("#4a111a"))
        pdf.setFont("Times-Bold", 13)
        pdf.drawString(22 * mm, start_y, title)
        pdf.setFillColor(colors.black)
        pdf.setFont("Times-Roman", 11)
        text = pdf.beginText(22 * mm, start_y - 7 * mm)
        text.setLeading(14)
        for paragraph in paragraphs:
            for line in wrap(paragraph, width=92):
                text.textLine(line)
            text.textLine("")
        pdf.drawText(text)
        return text.getY() - 4 * mm
