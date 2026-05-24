"""
Genera il PDF FINALE unico unendo tutte le sezioni:
    Sezione 1 + Sezione 2 + Sezione 3 + Sezione 4
in un singolo file pronto per la consegna.

Prerequisiti:
    pip install pypdf
    I quattro PDF di sezione devono esistere in report/.
"""
from pathlib import Path
from pypdf import PdfWriter, PdfReader

# ---- PERSONALIZZA QUI I TUOI DATI ----------------------------------------
STUDENTE_NOME      = "Raffaele Della Porta"
STUDENTE_MATRICOLA = "0322500029"
ANNO_ACCADEMICO    = "2025 / 2026"
DOCENTE            = "Sergio Spano'"
# --------------------------------------------------------------------------

ROOT = Path(__file__).parent
REPO = ROOT / "report"
OUT  = REPO / "Report_Hadamard_FINALE.pdf"

# Frontespizio (lo genero al volo con reportlab)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

FRONT = REPO / "_frontespizio.pdf"
styles = getSampleStyleSheet()
P = lambda t, sz=12, bold=False, color="#000000": Paragraph(
    f"<para align='center' fontSize={sz} textColor='{color}'>"
    f"{'<b>' if bold else ''}{t}{'</b>' if bold else ''}</para>",
    styles["BodyText"])

doc = SimpleDocTemplate(str(FRONT), pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2.5*cm, bottomMargin=2*cm)
story = [
    Spacer(1, 1.5*cm),
    P("Universita' degli Studi", 12),
    P("Corso di Laurea in Ingegneria Informatica", 12),
    Spacer(1, 0.4*cm),
    P("Introduzione al Trattamento Quantistico delle Informazioni", 13, True),
    Spacer(1, 3*cm),
    P("PROGETTO DI LABORATORIO", 14, True, "#555555"),
    Spacer(1, 0.5*cm),
    P("AREA HADAMARD GATE", 24, True, "#0B3D91"),
    Spacer(1, 0.3*cm),
    P("Implementazione VHDL di un gate di Hadamard 2x2", 13),
    P("su FPGA Boolean Board (Spartan-7)", 13),
    Spacer(1, 4*cm),
    P("Indice del documento:", 11, True),
    Spacer(1, 0.3*cm),
    P("Sezione 1 - Listato di codice e spiegazione dettagliata", 11),
    P("Sezione 2 - Risultato del Linter", 11),
    P("Sezione 3 - Risultati di implementazione (risorse, F_max, potenza)", 11),
    P("Sezione 4 - Risultati di test-bench behavioral (4 input)", 11),
    Spacer(1, 3*cm),
    P(f"Studente: <b>{STUDENTE_NOME}</b>", 11),
    P(f"Matricola: <b>{STUDENTE_MATRICOLA}</b>", 11),
    P(f"Docente: <b>{DOCENTE}</b>", 11),
    P(f"Anno Accademico: <b>{ANNO_ACCADEMICO}</b>", 11),
]
doc.build(story)
print(f"Frontespizio: {FRONT}")

# Unione dei PDF
parts = [
    FRONT,
    REPO / "Report_Hadamard_Sezione1.pdf",
    REPO / "Report_Hadamard_Sezione2.pdf",
    REPO / "Report_Hadamard_Sezione3.pdf",
    REPO / "Report_Hadamard_Sezione4.pdf",
]

writer = PdfWriter()
for p in parts:
    if not p.exists():
        print(f"  [WARN] non trovato: {p}")
        continue
    reader = PdfReader(str(p))
    for page in reader.pages:
        writer.add_page(page)
    print(f"  + {p.name}  ({len(reader.pages)} pagine)")

writer.add_metadata({
    "/Title":  "Report Hadamard Gate - Progetto Completo",
    "/Author": STUDENTE_NOME,
    "/Subject": "Introduzione al Trattamento Quantistico delle Informazioni",
})

with open(OUT, "wb") as f:
    writer.write(f)

print(f"\nPDF FINALE generato: {OUT}")
print(f"  Dimensione: {OUT.stat().st_size / 1024:.1f} KB")

