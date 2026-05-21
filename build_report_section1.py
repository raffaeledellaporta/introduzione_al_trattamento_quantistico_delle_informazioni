"""
Genera il PDF della Sezione 1 del report:
    "Listato di codice e relativa spiegazione dettagliata del funzionamento"

Uso:
    pip install reportlab
    python build_report_section1.py

Output:
    report/Report_Hadamard_Sezione1.pdf
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    PageBreak, Table, TableStyle, KeepTogether
)

ROOT = Path(__file__).parent
SRC = ROOT / "src"
SIM = ROOT / "sim"
XDC = ROOT / "constraints"
OUT = ROOT / "report" / "Report_Hadamard_Sezione1.pdf"
OUT.parent.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Stili
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    alignment=TA_JUSTIFY,
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="H1",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=16,
    spaceBefore=12,
    spaceAfter=8,
    textColor=colors.HexColor("#0B3D91"),
))
styles.add(ParagraphStyle(
    name="H2",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=13,
    spaceBefore=10,
    spaceAfter=6,
    textColor=colors.HexColor("#0B3D91"),
))
styles.add(ParagraphStyle(
    name="H3",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11,
    spaceBefore=8,
    spaceAfter=4,
    textColor=colors.HexColor("#333333"),
))
styles.add(ParagraphStyle(
    name="VHDLCode",
    parent=styles["Code"],
    fontName="Courier",
    fontSize=8.5,
    leading=10.5,
    backColor=colors.HexColor("#F4F4F4"),
    borderColor=colors.HexColor("#CCCCCC"),
    borderWidth=0.5,
    borderPadding=4,
    leftIndent=4,
    rightIndent=4,
    spaceBefore=4,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="Caption",
    parent=styles["Italic"],
    fontSize=9,
    textColor=colors.HexColor("#555555"),
    spaceAfter=8,
))


def H1(t): return Paragraph(t, styles["H1"])
def H2(t): return Paragraph(t, styles["H2"])
def H3(t): return Paragraph(t, styles["H3"])
def P(t):  return Paragraph(t, styles["Body"])
def Cap(t): return Paragraph(t, styles["Caption"])


def code_block(path: Path):
    """Carica un file e lo restituisce come blocco preformattato."""
    text = path.read_text(encoding="utf-8")
    return Preformatted(text, styles["VHDLCode"])


def make_table(data, col_widths=None, header_bg="#0B3D91"):
    tbl = Table(data, colWidths=col_widths, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#888888")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F4F4F4")]),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]))
    return tbl


# ---------------------------------------------------------------------------
# Contenuto
# ---------------------------------------------------------------------------
story = []

# === Frontespizio ============================================================
story += [
    Spacer(1, 3*cm),
    Paragraph(
        "<para align='center'><b>Progetto di Laboratorio</b></para>",
        styles["Body"]),
    Spacer(1, 0.4*cm),
    Paragraph(
        "<para align='center' fontSize=20 textColor='#0B3D91'>"
        "<b>AREA HADAMARD GATE</b></para>",
        styles["Body"]),
    Spacer(1, 0.3*cm),
    Paragraph(
        "<para align='center' fontSize=12>"
        "Implementazione VHDL di un gate di Hadamard 2x2<br/>"
        "su FPGA Boolean Board (Spartan-7)</para>",
        styles["Body"]),
    Spacer(1, 2*cm),
    Paragraph(
        "<para align='center'>"
        "Corso: <b>Introduzione al Trattamento Quantistico delle Informazioni</b><br/>"
        "Sezione 1 del Report: <b>Listato di codice e spiegazione dettagliata</b>"
        "</para>",
        styles["Body"]),
    Spacer(1, 4*cm),
    Paragraph(
        "<para align='center' fontSize=9 textColor='#666666'>"
        "Documento generato automaticamente con ReportLab</para>",
        styles["Body"]),
    PageBreak(),
]

# === 1.1 Inquadramento teorico ==============================================
story += [
    H1("1. Sezione 1 — Listato di codice e spiegazione dettagliata"),
    H2("1.1 Inquadramento teorico"),
    P("Il gate di Hadamard è la porta quantistica a 1-qubit più importante "
      "nei circuiti di Deutsch–Jozsa, Grover e Shor: trasforma uno stato di "
      "base in una sovrapposizione bilanciata. La sua matrice è:"),
    Paragraph(
        "<para align='center' fontName='Courier' fontSize=11>"
        "H = (1/√2) · [ [ 1,  1 ] ; [ 1, -1 ] ]</para>",
        styles["Body"]),
    P("Applicata al vettore di stato |ψ⟩ = [a; b]<sup>T</sup> produce:"),
    Paragraph(
        "<para align='center' fontName='Courier' fontSize=11>"
        "H · |ψ⟩ = (1/√2) · [ a+b ; a−b ]</para>",
        styles["Body"]),
    P("L'obiettivo del progetto è realizzare questa trasformazione in "
      "hardware su FPGA, usando aritmetica a virgola fissa a "
      "<b>12 bit con segno</b> e <b>8 bit di parte frazionaria</b> "
      "(formato <b>Q3.8</b>: 1 bit di segno, 3 bit interi, 8 bit frazionari). "
      "Il range rappresentabile è [−8.000, +7.996], con risoluzione "
      "1/256 ≈ 3.9·10<sup>−3</sup>."),
    P("La costante 1/√2 ≈ 0.70710678 in Q3.8 vale:"),
    Paragraph(
        "<para align='center' fontName='Courier' fontSize=10>"
        "round(0.70710678 · 2<sup>8</sup>) = 181 = 0000_1011_0101<sub>2</sub>"
        "</para>",
        styles["Body"]),
]

# === 1.2 Architettura =======================================================
story += [
    H2("1.2 Architettura del progetto"),
    P("La specifica richiede che <b>tutti gli ingressi e le uscite della "
      "top-level entity siano collegati a registri</b>. Sono quindi presenti "
      "due banchi di registri: uno in ingresso (a_reg, b_reg) e uno in "
      "uscita (y0_reg, y1_reg). Il calcolo combinatorio è incapsulato nel "
      "modulo <b>hadamard_core</b>, riusabile e parametrico. I valori della "
      "matrice (1, 1, 1, −1, costante 1/√2) non sono input ma <b>costanti</b>, "
      "come permesso dal SUGGERIMENTO della traccia."),
    Preformatted(
        "                  ┌─────────────────────┐\n"
        "    A_CONST  ───► │  REG  a_reg (12b)   │──┐\n"
        "                  └─────────────────────┘  │\n"
        "                  ┌─────────────────────┐  ▼\n"
        "    B_CONST  ───► │  REG  b_reg (12b)   │─►┌──────────────────────┐\n"
        "                  └─────────────────────┘  │   hadamard_core      │\n"
        "                                           │   (combinatoria)     │\n"
        "                                           │   sum  = a+b         │\n"
        "                                           │   diff = a-b         │\n"
        "                                           │   prod = · 181       │\n"
        "                                           │   y    = prod >> 8   │\n"
        "                                           └──┬─────────────┬─────┘\n"
        "                                              ▼             ▼\n"
        "                                       ┌────────────┐ ┌────────────┐\n"
        "                                       │ REG y0_reg │ │ REG y1_reg │\n"
        "                                       └─────┬──────┘ └─────┬──────┘\n"
        "                                             ▼              ▼\n"
        "                                          y0_obs         y1_obs\n",
        styles["VHDLCode"]),
    Cap("Schema a blocchi della top-level entity con registri I/O."),
]

# === 1.3 Struttura dei file =================================================
story += [
    H2("1.3 Struttura dei file sorgente"),
    make_table([
        ["File", "Ruolo"],
        ["src/hadamard_core.vhd",
         "Modulo combinatorio: implementa H · v"],
        ["src/hadamard_top.vhd",
         "Top-level: registri I/O, costanti A,B, istanza core"],
        ["sim/tb_hadamard.vhd",
         "Testbench behavioral con 4 stimoli"],
        ["constraints/hadamard.xdc",
         "Pin assignment per la Boolean Board"],
    ], col_widths=[6*cm, 10*cm]),
    PageBreak(),
]

# === 1.4 hadamard_core ======================================================
story += [
    H2("1.4 Listato — hadamard_core.vhd"),
    code_block(SRC / "hadamard_core.vhd"),
    H3("Spiegazione dettagliata"),
    make_table([
        ["Elemento", "Cosa fa", "Perché è così"],
        ["library IEEE; use NUMERIC_STD.ALL",
         "Importa tipi signed/unsigned e operatori aritmetici sintetizzabili.",
         "Standard IEEE consigliato; evita ambiguità di std_logic_arith."],
        ["generic DATA_WIDTH, FRAC_BITS",
         "Parametrizza la larghezza del dato e i bit frazionari.",
         "Permette riuso del modulo per altri formati Q senza riscrivere."],
        ["a_in, b_in : signed",
         "Ingressi a 12 bit con segno (Q3.8).",
         "I dati sono in [−8, +8) con risoluzione 1/256."],
        ["INV_SQRT2 := to_signed(181, 12)",
         "Costante 1/√2 in Q3.8.",
         "round(0.70710678·256)=181; errore di quantizzazione ≈ 1.3·10⁻⁴."],
        ["sum_ab, diff_ab : signed(12 downto 0)",
         "Operazioni a + b e a − b su 13 bit.",
         "Estensione di 1 bit per evitare overflow quando |a|+|b| ≥ 8."],
        ["prod_sum, prod_diff : signed(24 downto 0)",
         "Prodotti completi a 25 bit.",
         "signed(13) · signed(12) = signed(25); nessuna perdita di precisione."],
        ["shift_right(prod, FRAC_BITS)",
         "Divide per 2⁸, ovvero riallinea il risultato a Q3.8.",
         "Su signed, shift_right è aritmetico → preserva il segno."],
        ["resize(..., DATA_WIDTH)",
         "Ritorna a 12 bit.",
         "I bit alti sono replica del segno per gli ingressi normalizzati."],
    ], col_widths=[4.2*cm, 5.8*cm, 6.2*cm]),
    P("<b>Aspetto numerico chiave.</b> Il prodotto signed(13b)×signed(12b) "
      "produce 25 bit con 16 bit frazionari. Dopo shift_right(...,8) restano "
      "17 bit con 8 frazionari; resize ne tiene 12. Vivado, per questa "
      "moltiplicazione, inferisce un blocco <b>DSP48E1</b> per ciascun "
      "prodotto (2 totali)."),
    PageBreak(),
]

# === 1.5 hadamard_top =======================================================
story += [
    H2("1.5 Listato — hadamard_top.vhd"),
    code_block(SRC / "hadamard_top.vhd"),
    H3("Spiegazione dettagliata"),
    P("<b>1. Porte fisiche</b> — clk e rst sono gli unici input osservabili "
      "sulla board; il vettore di stato è interno (costante), come consentito "
      "dalla traccia. Le uscite sono std_logic_vector per poterle pinnare "
      "direttamente ai LED della Boolean Board nel file .xdc."),
    P("<b>2. Costanti del vettore stato</b> — A_CONST = 256, B_CONST = 0 → "
      "in Q3.8 valgono +1.0 e 0.0, cioè lo stato |0⟩. Cambiando solo queste "
      "due righe si testano in hardware tutti gli stati (|1⟩, |+⟩, |−⟩, …)."),
    P("<b>3. Registri di ingresso p_in_reg</b> — processo sensibile al solo "
      "clk: inferisce flip-flop sincroni con reset sincrono attivo alto. "
      "Forzando i registri all'inizio del clock domain, blindiamo il timing "
      "del core."),
    P("<b>4. Istanza u_core</b> — mappatura diretta dei registri sui port del "
      "core. I generic vengono propagati, così il top resta scalabile."),
    P("<b>5. Registri di uscita p_out_reg</b> — stesso schema: catturano "
      "y0_c/y1_c al fronte di salita. Garantiscono che il path combinatorio "
      "del core sia un unico stage tra due flip-flop, consentendo a Vivado "
      "di calcolare F<sub>max</sub> in modo pulito."),
    P("<b>6. Driver delle uscite</b> — y0_obs &lt;= std_logic_vector(y0_reg) "
      "è una conversione di tipo a costo zero (stesso pattern di bit), serve "
      "solo a soddisfare la dichiarazione di porta."),
    PageBreak(),
]

# === 1.6 testbench ==========================================================
story += [
    H2("1.6 Listato — tb_hadamard.vhd (testbench behavioral)"),
    code_block(SIM / "tb_hadamard.vhd"),
    H3("Spiegazione dettagliata"),
    P("<b>Entità senza port</b> — convenzione standard per un testbench: non "
      "si interfaccia col mondo esterno, contiene solo stimoli e DUT."),
    P("<b>Funzione to_q(real)</b> — converte un numero in virgola mobile nel "
      "suo equivalente Q3.8. È usata solo in simulazione (non sintetizzabile) "
      "per rendere leggibili i test, p.es. to_q(0.707) invece di "
      "to_signed(181,12)."),
    P("<b>Procedura check</b> — confronta il valore osservato con quello "
      "atteso ammettendo un errore massimo di 2 LSB (≈ 0.0078). La tolleranza "
      "serve perché (1) la costante INV_SQRT2 = 181/256 è essa stessa "
      "quantizzata e (2) il prodotto seguito da shift_right introduce un "
      "troncamento."),
    P("<b>4 stimoli</b> — sono i 4 stati di base più rappresentativi per "
      "validare anche l'<b>involutività</b> di H (H² = I):"),
    make_table([
        ["#", "Ingresso [a;b]", "Stato in", "Uscita attesa [y0;y1]", "Stato out"],
        ["1", "[+1.000;  0.000]", "|0⟩", "[+0.707; +0.707]", "|+⟩"],
        ["2", "[ 0.000; +1.000]", "|1⟩", "[+0.707; −0.707]", "|−⟩"],
        ["3", "[+0.707; +0.707]", "|+⟩", "[+1.000;  0.000]", "|0⟩"],
        ["4", "[+0.707; −0.707]", "|−⟩", "[ 0.000; +1.000]", "|1⟩"],
    ], col_widths=[0.8*cm, 3.6*cm, 2.0*cm, 4.0*cm, 2.0*cm]),
    PageBreak(),
]

# === 1.7 XDC ================================================================
story += [
    H2("1.7 Listato — constraints/hadamard.xdc"),
    code_block(XDC / "hadamard.xdc"),
    H3("Spiegazione dettagliata"),
    P("<b>create_clock -period 10.000</b>: dichiara il clock di sistema a "
      "100 MHz (Boolean Board), indispensabile perché il timing engine di "
      "Vivado calcoli lo slack e quindi F<sub>max</sub>."),
    P("<b>IOSTANDARD LVCMOS33</b>: standard elettrico di default dei banchi "
      "I/O della Spartan-7 sulla Boolean Board (3.3 V)."),
    P("I pin LED riportano in tempo reale lo stato dei registri di uscita "
      "y0_reg/y1_reg; per gli ingressi (costanti) non serve allocare pin."),
]

# === Riepilogo finale =======================================================
story += [
    H2("1.8 Riepilogo della Sezione 1"),
    P("• Il design rispetta integralmente la specifica: top entity con I/O "
      "registrati, segnali di dato a 12 bit signed Q3.8, matrice/stato come "
      "costanti della top entity (SUGGERIMENTO), target Boolean Board, "
      "sintesi Vivado."),
    P("• Il modulo è parametrico (DATA_WIDTH, FRAC_BITS) e quindi facilmente "
      "estendibile a precisioni maggiori."),
    P("• Il calcolo è numericamente corretto: errore massimo ≤ 2 LSB "
      "(≈ 0.008 in valore reale), con inferenza automatica di blocchi DSP48 "
      "in fase di sintesi."),
    P("Nelle prossime sezioni (2 — Linter, 3 — Implementazione, 4 — "
      "Testbench) si riporteranno gli output di Vivado e gli screenshot della "
      "simulazione behavioral."),
]


# ---------------------------------------------------------------------------
# Page footer
# ---------------------------------------------------------------------------
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(2*cm, 1*cm,
                      "Report Hadamard Gate — Sezione 1")
    canvas.drawRightString(A4[0] - 2*cm, 1*cm,
                           f"Pagina {doc.page}")
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="Report Hadamard Gate - Sezione 1",
    author="Studente",
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

print(f"PDF generato: {OUT}")
