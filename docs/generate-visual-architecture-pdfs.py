from __future__ import annotations

from pathlib import Path

from pypdf import PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
W, H = landscape(A4)

BLUE = colors.HexColor("#082653")
LINE = colors.HexColor("#6b8db8")
GREEN = colors.HexColor("#0f7b4f")
RED = colors.HexColor("#c62828")
ORANGE = colors.HexColor("#f57c00")
PURPLE = colors.HexColor("#6a1b9a")
TEAL = colors.HexColor("#00796b")
BG = colors.HexColor("#f7fbff")


def header(c: canvas.Canvas, title: str, subtitle: str) -> None:
    c.setFillColor(BLUE)
    c.rect(0, H - 18 * mm, W, 18 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(W / 2, H - 8 * mm, title)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, H - 13 * mm, subtitle)
    c.setFillColor(colors.HexColor("#102033"))


def footer(c: canvas.Canvas) -> None:
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(10 * mm, 7 * mm, "DECEPTR v1 MVP - Chambre des Representants du Maroc - Mis a jour 2026-06-15")
    c.drawRightString(W - 10 * mm, 7 * mm, f"Page {c.getPageNumber()}")


def wrap(text: str, max_width: float, font: str = "Helvetica", size: float = 7) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        nxt = word if not cur else f"{cur} {word}"
        if stringWidth(nxt, font, size) <= max_width:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def box(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, body: str = "",
        fill=colors.white, stroke=LINE, title_color=BLUE) -> None:
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    c.setFillColor(title_color)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + w / 2, y + h - 5 * mm, title)
    if body:
        c.setFillColor(colors.HexColor("#1f2937"))
        c.setFont("Helvetica", 6.5)
        yy = y + h - 10 * mm
        for line in wrap(body, w - 6 * mm, size=6.5)[:6]:
            c.drawCentredString(x + w / 2, yy, line)
            yy -= 4 * mm


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, color=colors.HexColor("#1e56a0"),
          label: str | None = None) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.1)
    c.line(x1, y1, x2, y2)
    # Simple arrow head.
    dx = 1 if x2 >= x1 else -1
    dy = 1 if y2 >= y1 else -1
    if abs(x2 - x1) >= abs(y2 - y1):
        c.line(x2, y2, x2 - dx * 3 * mm, y2 + 1.5 * mm)
        c.line(x2, y2, x2 - dx * 3 * mm, y2 - 1.5 * mm)
    else:
        c.line(x2, y2, x2 + 1.5 * mm, y2 - dy * 3 * mm)
        c.line(x2, y2, x2 - 1.5 * mm, y2 - dy * 3 * mm)
    if label:
        c.setFont("Helvetica", 6)
        c.setFillColor(color)
        c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 2 * mm, label)


def zone(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, color) -> None:
    c.setStrokeColor(color)
    c.setDash(3, 2)
    c.roundRect(x, y, w, h, 5, fill=0, stroke=1)
    c.setDash()
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 3 * mm, y + h - 6 * mm, title)


def small_table(c: canvas.Canvas, x: float, y: float, rows: list[tuple[str, str]], title: str, w: float = 80 * mm) -> None:
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(BLUE)
    c.drawString(x, y, title)
    y -= 5 * mm
    for left, right in rows:
        c.setStrokeColor(colors.HexColor("#b7c8de"))
        c.setFillColor(colors.HexColor("#f8fbff"))
        c.rect(x, y - 5 * mm, w, 6 * mm, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#102033"))
        c.setFont("Helvetica-Bold", 6.2)
        c.drawString(x + 2 * mm, y - 3 * mm, left)
        c.setFont("Helvetica", 6.2)
        c.drawString(x + 33 * mm, y - 3 * mm, right)
        y -= 6 * mm


def functional_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    header(c, "ARCHITECTURE FONCTIONNELLE - DECEPTR v1 MVP", "Pipeline de deception, enrichissement, detection, stockage et visualisation")
    c.setFillColor(BG)
    c.rect(0, 0, W, H - 18 * mm, fill=1, stroke=0)

    x0, y0 = 12 * mm, 123 * mm
    bw, bh, gap = 39 * mm, 18 * mm, 5 * mm
    stages = [
        ("1. Detection", "Cowrie, Web honeypot, Dionaea, honeytokens", RED),
        ("2. Collecte", "Filebeat T-Pot et logs JSON", ORANGE),
        ("3. Ingestion", "Logstash TLS 1.3 TCP/5044", GREEN),
        ("4. Queue", "Redis deceptr:events", TEAL),
        ("5. Pipeline", "Collector, normalizer, enricher", PURPLE),
        ("6. Alertes", "MITRE, risk score, detection", RED),
    ]
    for i, (t, b, col) in enumerate(stages):
        x = x0 + i * (bw + gap)
        box(c, x, y0, bw, bh, t, b, fill=colors.white, stroke=col, title_color=col)
        if i:
            arrow(c, x - gap + 1 * mm, y0 + bh / 2, x - 1 * mm, y0 + bh / 2)

    # Storage and presentation layer.
    y2 = 80 * mm
    stores = [
        ("Elasticsearch", "cowrie-* / deceptr-events-* / deceptr-web-honeypot", 25 * mm, colors.HexColor("#fff8e1")),
        ("MySQL", "alerts / iocs / attackers / campaigns / honeytokens / users", 105 * mm, colors.HexColor("#e8f5e9")),
        ("MinIO", "reports / backups / malware-samples / attachments", 185 * mm, colors.HexColor("#ffebee")),
    ]
    for t, b, x, f in stores:
        box(c, x, y2, 67 * mm, 17 * mm, t, b, fill=f, stroke=LINE)
        arrow(c, x0 + 5 * (bw + gap) + bw / 2, y0, x + 33 * mm, y2 + 17 * mm, label="events")

    y3 = 45 * mm
    views = [
        ("Kibana", "Analyse ELK", 36 * mm),
        ("FastAPI", "JWT + API REST", 106 * mm),
        ("Dashboard DECEPTR", "SOC / Admin / Audit / Management", 176 * mm),
        ("ElastAlert 2", "Email / Webhook / Syslog", 226 * mm),
    ]
    for t, b, x in views:
        box(c, x, y3, 43 * mm, 16 * mm, t, b, fill=colors.white, stroke=BLUE)
    arrow(c, 58 * mm, y2, 58 * mm, y3 + 16 * mm, label="visualiser")
    arrow(c, 138 * mm, y2, 128 * mm, y3 + 16 * mm, label="API")
    arrow(c, 149 * mm, y3 + 8 * mm, 176 * mm, y3 + 8 * mm)
    arrow(c, 218 * mm, y2, 247 * mm, y3 + 16 * mm, label="alertes")

    small_table(c, 12 * mm, 42 * mm, [
        ("E2E", "OK"),
        ("TLS", "Filebeat -> Logstash TLS 1.3"),
        ("MITRE", "T1110 login / T1039 honeytoken"),
        ("API", "161 alertes, 80 sur 24h"),
    ], "Validation 2026-06-15", w=95 * mm)
    footer(c)
    c.save()


def network_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    header(c, "ARCHITECTURE RESEAU - DECEPTR v1 MVP", "Zones, flux unidirectionnels et ports valides")
    c.setFillColor(BG)
    c.rect(0, 0, W, H - 18 * mm, fill=1, stroke=0)

    zone(c, 10 * mm, 55 * mm, 55 * mm, 120 * mm, "ZONE EXTERNE", RED)
    zone(c, 75 * mm, 55 * mm, 65 * mm, 120 * mm, "DMZ - HONEYPOTS", ORANGE)
    zone(c, 150 * mm, 55 * mm, 88 * mm, 120 * mm, "LAN ANALYSE", GREEN)
    zone(c, 248 * mm, 55 * mm, 38 * mm, 120 * mm, "ADMIN / SOC", PURPLE)

    box(c, 18 * mm, 138 * mm, 38 * mm, 18 * mm, "Attaquants", "Internet, bots, scanners, insiders", fill=colors.white, stroke=RED, title_color=RED)
    box(c, 18 * mm, 92 * mm, 38 * mm, 18 * mm, "Firewall", "pfSense / FortiGate NAT, IDS/IPS, VPN", fill=colors.HexColor("#fff3e0"), stroke=RED, title_color=RED)
    arrow(c, 37 * mm, 138 * mm, 37 * mm, 110 * mm, RED)

    box(c, 82 * mm, 140 * mm, 50 * mm, 19 * mm, "T-Pot Cowrie", "SSH 22 / Telnet 23", fill=colors.white, stroke=ORANGE, title_color=ORANGE)
    box(c, 82 * mm, 113 * mm, 50 * mm, 19 * mm, "Web honeypot", "Faux portail intranet 8082", fill=colors.white, stroke=ORANGE, title_color=ORANGE)
    box(c, 82 * mm, 86 * mm, 50 * mm, 19 * mm, "Dionaea", "FTP 2121, HTTP 8081, SMB 1445, MySQL 13306", fill=colors.white, stroke=ORANGE, title_color=ORANGE)
    box(c, 88 * mm, 62 * mm, 38 * mm, 14 * mm, "Filebeat", "Forwarder TLS", fill=colors.HexColor("#fff8e1"), stroke=ORANGE, title_color=ORANGE)

    arrow(c, 56 * mm, 101 * mm, 82 * mm, 149 * mm, RED, "22/23")
    arrow(c, 56 * mm, 101 * mm, 82 * mm, 122 * mm, RED, "8082")
    arrow(c, 56 * mm, 101 * mm, 82 * mm, 95 * mm, RED, "decoys")
    arrow(c, 107 * mm, 140 * mm, 107 * mm, 76 * mm, ORANGE)
    arrow(c, 132 * mm, 69 * mm, 153 * mm, 69 * mm, GREEN, "TLS 1.3 5044")

    lan_boxes = [
        ("Logstash", "5044", 158, 145),
        ("Redis", "6379", 200, 145),
        ("Pipeline", "Python 7 etapes", 158, 116),
        ("Elasticsearch", "9200", 200, 116),
        ("MySQL", "interne", 158, 87),
        ("MinIO", "9000/9001", 200, 87),
        ("API", "8000", 158, 62),
        ("Kibana", "5601", 200, 62),
    ]
    for t, b, x, y in lan_boxes:
        box(c, x * mm, y * mm, 33 * mm, 15 * mm, t, b, fill=colors.white, stroke=GREEN, title_color=GREEN)
    arrow(c, 191 * mm, 152 * mm, 200 * mm, 152 * mm, GREEN)
    arrow(c, 216 * mm, 145 * mm, 174 * mm, 131 * mm, GREEN)
    arrow(c, 191 * mm, 123 * mm, 200 * mm, 123 * mm, GREEN)
    arrow(c, 174 * mm, 116 * mm, 174 * mm, 102 * mm, GREEN)
    arrow(c, 216 * mm, 116 * mm, 216 * mm, 102 * mm, GREEN)
    arrow(c, 174 * mm, 87 * mm, 174 * mm, 77 * mm, GREEN)

    box(c, 252 * mm, 137 * mm, 30 * mm, 16 * mm, "SOC", "Dashboard 8088", fill=colors.white, stroke=PURPLE, title_color=PURPLE)
    box(c, 252 * mm, 112 * mm, 30 * mm, 16 * mm, "Analyste", "Kibana 5601", fill=colors.white, stroke=PURPLE, title_color=PURPLE)
    box(c, 252 * mm, 87 * mm, 30 * mm, 16 * mm, "Admin", "API 8000 / MinIO 9001", fill=colors.white, stroke=PURPLE, title_color=PURPLE)
    arrow(c, 248 * mm, 145 * mm, 191 * mm, 69 * mm, PURPLE, "VPN/MFA")
    arrow(c, 248 * mm, 120 * mm, 233 * mm, 69 * mm, PURPLE)

    small_table(c, 12 * mm, 36 * mm, [
        ("Expose", "22, 23, 8082, 2121, 8081, 1445, 13306"),
        ("Ingestion", "5044 TLS depuis T-Pot seulement"),
        ("Admin", "8088, 5601, 8000, 9001 via VPN/MFA"),
    ], "Regles reseau", w=125 * mm)
    footer(c)
    c.save()


def technical_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    header(c, "ARCHITECTURE TECHNIQUE - DECEPTR v1 MVP", "Services Docker, stockage, API et validation technique")
    c.setFillColor(BG)
    c.rect(0, 0, W, H - 18 * mm, fill=1, stroke=0)

    # Main technical flow.
    nodes = [
        ("cowrie", "T-Pot runtime\n22/23", 15, 142, ORANGE),
        ("filebeat", "deceptr-tpot-forwarder\nTLS 1.3", 58, 142, ORANGE),
        ("logstash", "deceptr-logstash\n5044", 101, 142, GREEN),
        ("redis", "deceptr-redis\nqueue", 144, 142, TEAL),
        ("pipeline", "deceptr-pipeline\nPython 3.11", 187, 142, PURPLE),
        ("api", "deceptr-api\n8000", 230, 142, BLUE),
    ]
    for title, body, x, y, col in nodes:
        box(c, x * mm, y * mm, 36 * mm, 17 * mm, title, body.replace("\n", " "), stroke=col, title_color=col)
    for x in [51, 94, 137, 180, 223]:
        arrow(c, x * mm, 150 * mm, (x + 7) * mm, 150 * mm)

    stores = [
        ("Elasticsearch", "cowrie-* / deceptr-events-* / web", 86, 100, colors.HexColor("#fff8e1")),
        ("MySQL", "alerts / iocs / campaigns / honeytokens", 146, 100, colors.HexColor("#e8f5e9")),
        ("MinIO", "reports / backups / samples", 206, 100, colors.HexColor("#ffebee")),
    ]
    for title, body, x, y, fill in stores:
        box(c, x * mm, y * mm, 48 * mm, 18 * mm, title, body, fill=fill, stroke=LINE)
        arrow(c, 205 * mm, 142 * mm, (x + 24) * mm, (y + 18) * mm, label="write")

    views = [
        ("Kibana", "5601", 86, 68),
        ("Dashboard", "8088", 146, 68),
        ("ElastAlert", "notifications", 206, 68),
    ]
    for title, body, x, y in views:
        box(c, x * mm, y * mm, 48 * mm, 16 * mm, title, body, stroke=BLUE)
    arrow(c, 110 * mm, 100 * mm, 110 * mm, 84 * mm)
    arrow(c, 230 * mm, 142 * mm, 170 * mm, 84 * mm)
    arrow(c, 110 * mm, 100 * mm, 230 * mm, 84 * mm)

    box(c, 15 * mm, 100 * mm, 48 * mm, 18 * mm, "Web honeypot", "Flask faux portail 8082 -> ES", stroke=RED, title_color=RED)
    box(c, 15 * mm, 68 * mm, 48 * mm, 18 * mm, "Dionaea", "FTP/HTTP/SMB/MySQL decoys", stroke=RED, title_color=RED)
    arrow(c, 63 * mm, 109 * mm, 86 * mm, 109 * mm, RED)
    arrow(c, 63 * mm, 77 * mm, 86 * mm, 109 * mm, RED)

    small_table(c, 15 * mm, 45 * mm, [
        ("GeoLite2", "pipeline/data/GeoLite2-City.mmdb"),
        ("Canary", "API -> Redis -> CRITICAL T1039"),
        ("Smoke test", "status OK, MITRE T1110"),
        ("Docs", "PDF + Markdown mis a jour"),
    ], "Validation technique", w=105 * mm)
    small_table(c, 135 * mm, 45 * mm, [
        ("Dashboard", "http://127.0.0.1:8088/index.html?v=3"),
        ("Kibana", "http://127.0.0.1:5601"),
        ("API", "http://127.0.0.1:8000/docs"),
        ("MinIO", "http://127.0.0.1:9001"),
    ], "Acces", w=110 * mm)
    footer(c)
    c.save()


def combine(paths: list[Path], output: Path) -> None:
    writer = PdfWriter()
    for p in paths:
        writer.append(str(p))
    with output.open("wb") as fh:
        writer.write(fh)


def main() -> None:
    outputs = [
        ROOT / "architecture-fonctionnelle.pdf",
        ROOT / "architecture-reseau.pdf",
        ROOT / "architecture-technique.pdf",
    ]
    functional_pdf(outputs[0])
    network_pdf(outputs[1])
    technical_pdf(outputs[2])
    combine(outputs, ROOT / "architectures-deceptr.pdf")
    for p in [*outputs, ROOT / "architectures-deceptr.pdf"]:
        print(f"{p.name}: {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
