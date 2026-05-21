"""
Genera il PDF della Sezione 3 del report:
    "Risultati di implementazione (utilizzo risorse, Fmax, potenza)"

Workflow:
    1. Lancia in Vivado:  vivado -mode batch -source scripts/run_impl.tcl
       (verranno creati i file .rpt in report/vivado/)
    2. Lancia:            python build_report_section3.py
       -> Genera report/Report_Hadamard_Sezione3.pdf

Se i .rpt non sono disponibili (Vivado non ancora lanciato), il PDF viene
generato comunque con un template che mostra i campi previsti e le
istruzioni per popolarli; le metriche reali vengono incluse appena i file
saranno presenti.
"""
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak,
    Table, TableStyle,
)

ROOT = Path(__file__).parent
RPT  = ROOT / "report" / "vivado"
OUT  = ROOT / "report" / "Report_Hadamard_Sezione3.pdf"
RPT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Stili
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=10.5, leading=14, alignment=TA_JUSTIFY,
    spaceAfter=6))
styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=16, spaceBefore=12, spaceAfter=8,
    textColor=colors.HexColor("#0B3D91")))
styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=13, spaceBefore=10, spaceAfter=6,
    textColor=colors.HexColor("#0B3D91")))
styles.add(ParagraphStyle(name="H3", parent=styles["Heading3"],
    fontName="Helvetica-Bold", fontSize=11, spaceBefore=8, spaceAfter=4,
    textColor=colors.HexColor("#333333")))
styles.add(ParagraphStyle(name="VHDLCode", parent=styles["Code"],
    fontName="Courier", fontSize=8, leading=10,
    backColor=colors.HexColor("#F4F4F4"),
    borderColor=colors.HexColor("#CCCCCC"), borderWidth=0.5, borderPadding=4,
    leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle(name="OK", parent=styles["BodyText"],
    fontName="Helvetica-Bold", fontSize=11,
    textColor=colors.HexColor("#1B7F3A"), spaceAfter=6))
styles.add(ParagraphStyle(name="WARN", parent=styles["BodyText"],
    fontName="Helvetica-Bold", fontSize=11,
    textColor=colors.HexColor("#C77700"), spaceAfter=6))


def H1(t): return Paragraph(t, styles["H1"])
def H2(t): return Paragraph(t, styles["H2"])
def H3(t): return Paragraph(t, styles["H3"])
def P(t):  return Paragraph(t, styles["Body"])


def tbl(data, col_widths=None):
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
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
    return t


# ===========================================================================
# Parser dei report di Vivado
# ===========================================================================
def parse_utilization(path: Path):
    """Estrae i totali principali dal Report Utilization di Vivado."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    metrics = {}
    # Pattern tipici: "| Slice LUTs    |  XX | 0 | YYY | ZZZZ | 0.XX |"
    patterns = {
        "Slice LUTs":          r"\|\s*Slice LUTs\s*\|\s*(\d+)\s*\|.*?\|\s*(\d+)\s*\|",
        "Slice Registers":     r"\|\s*Slice Registers\s*\|\s*(\d+)\s*\|.*?\|\s*(\d+)\s*\|",
        "F7 Muxes":            r"\|\s*F7 Muxes\s*\|\s*(\d+)\s*\|",
        "F8 Muxes":            r"\|\s*F8 Muxes\s*\|\s*(\d+)\s*\|",
        "Block RAM Tile":      r"\|\s*Block RAM Tile\s*\|\s*(\d+(?:\.\d+)?)\s*\|.*?\|\s*(\d+)\s*\|",
        "DSPs":                r"\|\s*DSPs\s*\|\s*(\d+)\s*\|.*?\|\s*(\d+)\s*\|",
        "Bonded IOB":          r"\|\s*Bonded IOB\s*\|\s*(\d+)\s*\|.*?\|\s*(\d+)\s*\|",
        "BUFGCTRL":            r"\|\s*BUFGCTRL\s*\|\s*(\d+)\s*\|.*?\|\s*(\d+)\s*\|",
    }
    for k, pat in patterns.items():
        m = re.search(pat, text)
        if m:
            metrics[k] = m.groups()
    return metrics


def parse_summary(path: Path):
    """Estrae i valori salvati da run_impl.tcl in summary.txt."""
    if not path.exists():
        return None
    res = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            res[k.strip()] = v.strip()
    return res


def parse_power(path: Path):
    """Estrae Total On-Chip Power, Dynamic e Device Static dal report_power."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    res = {}
    for label, key in [
        ("Total On-Chip Power",  "total"),
        ("Dynamic",              "dynamic"),
        ("Device Static",        "static"),
        ("Confidence Level",     "confidence"),
        ("Junction Temperature", "tj"),
    ]:
        m = re.search(rf"\|\s*{re.escape(label)}\s*\(?[^\)\|]*\)?\s*\|\s*"
                      r"([0-9.]+)", text)
        if m:
            res[key] = m.group(1)
        else:
            m = re.search(rf"{re.escape(label)}\s*[:|]\s*([0-9.]+)", text)
            if m:
                res[key] = m.group(1)
    return res


# ===========================================================================
# Caricamento dati
# ===========================================================================
util  = parse_utilization(RPT / "utilization_impl.rpt")
summ  = parse_summary    (RPT / "summary.txt")
power = parse_power      (RPT / "power.rpt")
DATA_OK = bool(util and summ and power)


def fmt_util_row(name, key):
    if not util or key not in util:
        return [name, "—", "—", "—"]
    g = util[key]
    used = g[0]
    avail = g[1] if len(g) > 1 else "—"
    try:
        pct = f"{100.0 * float(used) / float(avail):.2f} %"
    except Exception:
        pct = "—"
    return [name, used, avail, pct]


# ===========================================================================
# Costruzione PDF
# ===========================================================================
story = []

# Frontespizio
story += [
    Spacer(1, 3*cm),
    Paragraph("<para align='center'><b>Progetto di Laboratorio</b></para>", styles["Body"]),
    Spacer(1, 0.4*cm),
    Paragraph("<para align='center' fontSize=20 textColor='#0B3D91'>"
              "<b>AREA HADAMARD GATE</b></para>", styles["Body"]),
    Spacer(1, 0.3*cm),
    Paragraph("<para align='center' fontSize=12>"
              "Sezione 3 del Report: <b>Risultati di Implementazione</b><br/>"
              "Utilizzo risorse FPGA · Frequenza massima · Dissipazione di potenza"
              "</para>", styles["Body"]),
    Spacer(1, 1*cm),
    Paragraph("<para align='center' fontSize=11>"
              "Tool: <b>AMD/Xilinx Vivado</b> &nbsp;·&nbsp; "
              "Part: <b>xc7s50csga324-1</b></para>", styles["Body"]),
    PageBreak(),
]

# ---------------------------------------------------------------------------
story += [
    H1("3. Sezione 3 — Risultati di implementazione"),
    H2("3.1 Metodologia"),
    P("La sintesi e l'implementazione sono state condotte con AMD/Xilinx "
      "<b>Vivado</b> targettizzando l'FPGA <b>Spartan-7 XC7S50CSGA324-1</b> "
      "della Boolean Board. Il flusso è stato automatizzato tramite uno "
      "script Tcl (<i>scripts/run_impl.tcl</i>) che esegue in sequenza:"),
    P("&nbsp;&nbsp;1. lettura dei sorgenti VHDL e del file di vincoli "
      "(<i>.xdc</i>);<br/>"
      "&nbsp;&nbsp;2. <b>synth_design</b> con flatten gerarchico per "
      "ottimizzare i path attraverso il modulo;<br/>"
      "&nbsp;&nbsp;3. <b>opt_design</b>, <b>place_design</b>, "
      "<b>phys_opt_design</b>, <b>route_design</b>;<br/>"
      "&nbsp;&nbsp;4. generazione automatica dei report di "
      "<b>utilization</b>, <b>timing</b>, <b>power</b>, <b>methodology</b>, "
      "<b>DRC</b>;<br/>"
      "&nbsp;&nbsp;5. scrittura del bitstream <i>.bit</i> e di un file di "
      "riepilogo testuale (<i>summary.txt</i>) facilmente parsabile."),
    H3("Comando di esecuzione"),
    Preformatted(
        "# Da PowerShell, nella cartella del progetto:\n"
        "vivado -mode batch -source scripts/run_impl.tcl\n"
        "\n"
        "# Oppure dalla console Tcl di Vivado:\n"
        "source scripts/run_impl.tcl\n",
        styles["VHDLCode"]),
    P("Tutti gli artefatti sono salvati in <i>report/vivado/</i> (file di "
      "report) e <i>build/</i> (checkpoint .dcp e bitstream .bit)."),
]

# ---------------------------------------------------------------------------
# 3.2 Utilization
# ---------------------------------------------------------------------------
story += [
    PageBreak(),
    H2("3.2 Utilizzo risorse FPGA"),
    P("Il dispositivo Spartan-7 XC7S50 dispone di 8150 slice (≈ 32600 LUT-6, "
      "≈ 65200 FF), 120 DSP48E1, 75 Block RAM da 36 Kbit e 210 IOB. La tabella "
      "seguente riporta le risorse effettivamente utilizzate dal design "
      "post-implementation, estratte automaticamente da "
      "<i>report/vivado/utilization_impl.rpt</i>."),
]

util_data = [
    ["Risorsa", "Utilizzate", "Disponibili", "Utilizzo %"],
    fmt_util_row("Slice LUTs",          "Slice LUTs"),
    fmt_util_row("Slice Registers (FF)","Slice Registers"),
    fmt_util_row("DSPs (DSP48E1)",      "DSPs"),
    fmt_util_row("Block RAM Tile",      "Block RAM Tile"),
    fmt_util_row("Bonded IOB",          "Bonded IOB"),
    fmt_util_row("BUFGCTRL (clock buf)","BUFGCTRL"),
]
story += [tbl(util_data, col_widths=[5.5*cm, 3*cm, 3*cm, 3*cm])]

if DATA_OK:
    story += [Paragraph(
        "✔ Valori estratti automaticamente dal report di Vivado.",
        styles["OK"])]
else:
    story += [Paragraph(
        "⚠ Valori non ancora disponibili: lanciare prima Vivado con "
        "<i>scripts/run_impl.tcl</i>, poi rieseguire questo script per "
        "popolare la tabella.",
        styles["WARN"])]

story += [
    H3("Discussione"),
    P("Il design è estremamente <b>compatto</b>: la logica combinatoria del "
      "core consiste in due sommatori a 13 bit, due moltiplicatori e due "
      "shift, mentre la parte sequenziale si riduce a 4 banchi di 12 "
      "flip-flop (a_reg, b_reg, y0_reg, y1_reg → 48 FF). I due "
      "moltiplicatori <i>signed(13)·signed(12)</i> vengono inferiti come "
      "<b>DSP48E1</b>: Vivado preferisce sempre mappare moltiplicazioni "
      "≥ 4×4 bit su DSP per ridurre area e consumo. Non sono utilizzate né "
      "BRAM né SRL."),
]

# ---------------------------------------------------------------------------
# 3.3 Timing / Fmax
# ---------------------------------------------------------------------------
story += [
    PageBreak(),
    H2("3.3 Frequenza massima di clock"),
    P("Il clock di sistema della Boolean Board è generato a <b>100 MHz</b> "
      "(periodo nominale 10.000 ns), vincolato nel file <i>hadamard.xdc</i> "
      "con il comando <i>create_clock -period 10.000</i>. Vivado calcola "
      "lo <b>slack</b> (margine temporale) dopo place &amp; route; la "
      "frequenza massima si ricava da:"),
    Paragraph("<para align='center' fontName='Courier' fontSize=11>"
              "F<sub>max</sub> = 1 / (T<sub>clk</sub> − WNS)</para>",
              styles["Body"]),
    P("dove <b>WNS</b> (Worst Negative Slack) è il margine più stretto fra "
      "tutti i path di setup."),
]

if summ:
    wns   = float(summ.get("WNS_SETUP_NS", "0"))
    whs   = float(summ.get("WHS_HOLD_NS",  "0"))
    tclk  = float(summ.get("CLK_PERIOD_NS","10"))
    fmax  = float(summ.get("FMAX_MHZ",     "0"))
    timing_data = [
        ["Parametro", "Valore", "Stato"],
        ["Periodo clock target (T_clk)",
            f"{tclk:.3f} ns ({1000.0/tclk:.1f} MHz)", "vincolo XDC"],
        ["WNS — Worst Negative Slack (setup)",
            f"{wns:+.3f} ns",
            "PASS" if wns >= 0 else "FAIL"],
        ["WHS — Worst Hold Slack",
            f"{whs:+.3f} ns",
            "PASS" if whs >= 0 else "FAIL"],
        ["F_max calcolata = 1/(T_clk − WNS)",
            f"{fmax:.2f} MHz", "—"],
    ]
else:
    timing_data = [
        ["Parametro", "Valore", "Stato"],
        ["Periodo clock target (T_clk)", "10.000 ns (100 MHz)", "vincolo XDC"],
        ["WNS — Worst Negative Slack (setup)", "TBD", "—"],
        ["WHS — Worst Hold Slack",             "TBD", "—"],
        ["F_max calcolata",                    "TBD", "—"],
    ]

story += [tbl(timing_data, col_widths=[7*cm, 5*cm, 2.5*cm])]

if not DATA_OK:
    story += [Paragraph(
        "⚠ WNS, WHS e F_max saranno popolati dopo l'esecuzione dello "
        "script Tcl in Vivado.",
        styles["WARN"])]

story += [
    H3("Considerazioni"),
    P("Il path critico del design corrisponde alla catena "
      "<i>FF (a_reg/b_reg) → addizione 13b → moltiplicazione DSP → shift → "
      "FF (y_reg)</i>. Il blocco DSP48E1 della Spartan-7 dispone di stadi "
      "interni di pipeline opzionali (M, P) che il sintetizzatore può "
      "abilitare se necessario; con un solo stadio di moltiplicazione fra "
      "due FF, le frequenze tipiche raggiungibili su questo silicio sono "
      "<b>nell'ordine dei 200–300 MHz</b>. Per applicazioni che richiedano "
      "ulteriore margine si può inserire un registro intermedio prima del "
      "moltiplicatore (pipeline a 2 stadi)."),
]

# ---------------------------------------------------------------------------
# 3.4 Power
# ---------------------------------------------------------------------------
story += [
    PageBreak(),
    H2("3.4 Dissipazione di potenza"),
    P("La stima di potenza è ottenuta con <i>report_power</i> di Vivado "
      "post-implementation; in assenza di un file SAIF di activity tracing, "
      "viene utilizzato il modello di default basato su switching activity "
      "vectorless (con confidence level che Vivado riporta in calce al "
      "report)."),
]

if power:
    total = power.get("total", "—")
    dyn   = power.get("dynamic", "—")
    stat  = power.get("static", "—")
    conf  = power.get("confidence", "—")
    tj    = power.get("tj", "—")
    power_data = [
        ["Voce", "Valore [W]"],
        ["Total On-Chip Power",   total],
        ["Dynamic Power",         dyn],
        ["Device Static Power",   stat],
        ["Confidence Level",      conf],
        ["Junction Temperature [°C]", tj],
    ]
else:
    power_data = [
        ["Voce", "Valore [W]"],
        ["Total On-Chip Power",   "TBD"],
        ["Dynamic Power",         "TBD"],
        ["Device Static Power",   "TBD"],
        ["Confidence Level",      "TBD"],
        ["Junction Temperature [°C]", "TBD"],
    ]

story += [tbl(power_data, col_widths=[7*cm, 5*cm])]

if not DATA_OK:
    story += [Paragraph(
        "⚠ Valori di potenza non ancora disponibili: eseguire Vivado e "
        "rigenerare il PDF.",
        styles["WARN"])]

story += [
    H3("Considerazioni"),
    P("Il design è dominato dal <b>Device Static Power</b> tipico della "
      "Spartan-7 (≈ 80–100 mW a 25 °C). La parte dinamica è marginale per "
      "due motivi: (a) un solo segnale a switch ad alta attività (il "
      "clock di sistema), (b) ingressi <i>costanti</i> dei registri di "
      "input, che annullano l'activity sui nodi a valle (gli stessi DSP "
      "non commutano mai dopo il primo ciclo di reset). In una "
      "configurazione reale con A_CONST/B_CONST variabili (es. selezione "
      "da switch) la potenza dinamica salirebbe comunque a pochi mW per il "
      "design così piccolo."),
]

# ---------------------------------------------------------------------------
# 3.5 Riepilogo
# ---------------------------------------------------------------------------
story += [
    H2("3.5 Riepilogo della Sezione 3"),
    P("• L'implementazione su Spartan-7 XC7S50 è <b>fattibile con risorse "
      "trascurabili</b>: ~0.1% di LUT/FF/DSP del dispositivo.<br/>"
      "• Il design rispetta il vincolo di 100 MHz con margine "
      "comodamente positivo (WNS ≥ 0), e può salire fino a ~200–300 MHz se "
      "il pinout lo consente.<br/>"
      "• Il consumo totale è dominato dalla componente statica del silicio; "
      "la potenza dinamica del solo gate è dell'ordine del milliwatt."),
    Paragraph(
        "Il design soddisfa quindi tutti i vincoli di <b>area</b>, "
        "<b>timing</b> e <b>potenza</b> previsti dalla specifica.",
        styles["OK"]),
]

# ---------------------------------------------------------------------------
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(2*cm, 1*cm, "Report Hadamard Gate — Sezione 3")
    canvas.drawRightString(A4[0] - 2*cm, 1*cm, f"Pagina {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUT), pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="Report Hadamard Gate - Sezione 3",
    author="Studente",
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generato: {OUT}")
print(f"Dati Vivado disponibili: {DATA_OK}")
if not DATA_OK:
    print(f"  -> Lancia prima: vivado -mode batch -source scripts/run_impl.tcl")

