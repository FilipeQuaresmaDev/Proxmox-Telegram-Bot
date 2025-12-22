from pathlib import Path
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

RAW_LOG = Path("/app/logs/audit.log")
PDF_LOG = Path("/app/logs/audit.pdf")

LOG_REGEX = re.compile(
    r"\[(?P<date>.*?)\]\s+"
    r"user_id=(?P<user_id>\S+)\s+"
    r"user=(?P<user>\S+)\s+"
    r"action=(?P<action>\S+)\s+"
    r"target=(?P<target>\S+)"
)


def generate_audit_pdf():
    if not RAW_LOG.exists():
        return None

    lines = []

    
    raw_lines = RAW_LOG.read_text().splitlines()[::-1]

    for raw_line in raw_lines:
        match = LOG_REGEX.search(raw_line)
        if not match:
            continue

        lines.extend([
            "-" * 40,
            f"Data/Hora : {match.group('date')}",
            f"Usuario   : {match.group('user')}",
            f"User ID   : {match.group('user_id')}",
            f"Acao      : {match.group('action')}",
            f"Alvo      : {match.group('target')}",
            "-" * 40,
            "",
        ])

    if not lines:
        return None

    c = canvas.Canvas(str(PDF_LOG), pagesize=A4)
    width, height = A4

    x = 2 * cm
    y = height - 2 * cm
    line_height = 14

    c.setFont("Helvetica", 10)

    for text in lines:
        if y < 3 * cm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 2 * cm

        c.drawString(x, y, text)
        y -= line_height

    c.save()
    return PDF_LOG
