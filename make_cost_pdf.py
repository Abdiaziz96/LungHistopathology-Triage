"""Cost statement + invoice. Measured figures are taken from the delivered repository.
Rate-card and consumption figures are a modelled schedule, marked as such on the document.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable, KeepTogether)

OUT = "Cost_Statement_and_Invoice.pdf"
PAGE = A4

# ---------------------------------------------------------------- identity
LAB_NAME = "ACINUS RESEARCH LTD"
LAB_TAG = "Computational pathology research and production"
LAB_ADDRESS = "[Registered office address]"
LAB_COMPANY = "[Company number]"
LAB_VAT = "[VAT registration number]"
CONTACT = "[name@domain]  |  [+44 ...]"

CLIENT = "[Client / commissioning entity]"
CLIENT_ADDRESS = "[Address]"
INVOICE_NO = "INV-2026-0001"
INVOICE_DATE = "15 October 2026"
REFERENCE = "Computational pathology triage platform: build, test and evaluation"

# ---------------------------------------------------------------- palette
NAVY = colors.HexColor("#0B2545")
ACCENT = colors.HexColor("#005EB8")
GREY = colors.HexColor("#5B6470")
LINE = colors.HexColor("#D5DCE5")
LIGHT = colors.HexColor("#F1F4F8")
TOTALBG = colors.HexColor("#E3EAF3")

H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=22, leading=25,
                    textColor=NAVY, spaceAfter=3)
H2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13, leading=16,
                    textColor=NAVY, spaceBefore=10, spaceAfter=5)
H3 = ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10.5, leading=13,
                    textColor=NAVY, spaceBefore=6, spaceAfter=3)
BODY = ParagraphStyle("BODY", fontName="Helvetica", fontSize=9.5, leading=13,
                      textColor=colors.HexColor("#1F2933"), spaceAfter=4)
NOTE = ParagraphStyle("NOTE", fontName="Helvetica-Oblique", fontSize=8.5, leading=11,
                      textColor=GREY, spaceAfter=4)
CELL = ParagraphStyle("CELL", fontName="Helvetica", fontSize=9, leading=12,
                      textColor=colors.HexColor("#1F2933"))
CELLB = ParagraphStyle("CELLB", fontName="Helvetica-Bold", fontSize=9, leading=12,
                       textColor=colors.HexColor("#1F2933"))
CELLR = ParagraphStyle("CELLR", fontName="Helvetica", fontSize=9, leading=12,
                       textColor=colors.HexColor("#1F2933"), alignment=2)
CELLRB = ParagraphStyle("CELLRB", fontName="Helvetica-Bold", fontSize=9, leading=12,
                        textColor=colors.HexColor("#1F2933"), alignment=2)
LABEL = ParagraphStyle("LABEL", fontName="Helvetica", fontSize=8, leading=10,
                       textColor=GREY)
BIG = ParagraphStyle("BIG", fontName="Helvetica-Bold", fontSize=15, leading=18,
                     textColor=NAVY, alignment=1)
BIGL = ParagraphStyle("BIGL", fontName="Helvetica", fontSize=7.5, leading=10,
                      textColor=GREY, alignment=1)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=8.5, leading=11.5,
                       textColor=GREY)


def money(v):
    return "\u00a3{:,.0f}".format(v)


def table(rows, widths, header=True, total_rows=()):
    t = Table(rows, colWidths=widths)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), LIGHT))
    for r in total_rows:
        style.append(("BACKGROUND", (0, r), (-1, r), TOTALBG))
    t.setStyle(TableStyle(style))
    return t


# ---------------------------------------------------------------- rate card
# MODELLED. Senior UK contract market rates. Edit rates and days to reflect actuals.
EFFORT = [
    ("Principal Machine Learning Engineer (technical co-founder)", 950, 24),
    ("Senior Software Engineer, front end", 750, 15),
    ("Research Scientist, evaluation and validation", 800, 9),
    ("DevOps and Release Engineer", 650, 6),
    ("Technical Author, documentation and regulatory preparation", 500, 5),
    ("Clinical and Regulatory Advisor (fractional)", 1200, 3),
    ("Commercial Lead (fractional)", 900, 4),
]
TOTAL_DAYS = sum(d for _, _, d in EFFORT)
TOTAL_EFFORT = sum(r * d for _, r, d in EFFORT)

WORKSTREAMS = [
    ("Discovery and architecture",
     "Problem definition, data strategy, architecture and deployment model selection.", 6),
    ("Model integration",
     "Checkpoint reconstruction, architecture matching, inference layer, ONNX export.", 10),
    ("Front end",
     "Clinical dashboard, upload pipeline, results panel and explainability viewer.", 12),
    ("Explainability",
     "Occlusion sensitivity implementation to replace unavailable Grad-CAM.", 5),
    ("Evaluation",
     "Labelled corpus assembly, label permutation study, accuracy measurement.", 9),
    ("Verification",
     "Numerical parity testing, smoke tests, defect resolution.", 7),
    ("Deployment",
     "Static build, hosting configuration, release pipeline, runtime vendoring.", 6),
    ("Documentation",
     "Cost statement, funder deck, hosting assessment, technical notes.", 6),
    ("Governance and commercial",
     "Funder strategy, governance requirements, IP and entity framing.", 5),
]

# ------------------------------------------------------- infrastructure
# MODELLED. Replace quantities with provider billing before external issue.
INFRA = [
    ("Agentic development and code generation API consumption", "28.5", "M tokens",
     "\u00a32.10 / M", 60),
    ("Model training and fine-tuning compute", "24", "GPU hours", "\u00a32.40 / hr", 58),
    ("Evaluation and validation compute", "60", "CPU hours", "\u00a30.12 / hr", 7),
    ("Dataset acquisition, licensing and transfer", "1", "lot", "\u00a3240", 240),
    ("Object storage and backup for artefacts", "12", "months", "\u00a314 / month", 168),
    ("Application hosting and content delivery", "12", "months", "\u00a320 / month", 240),
    ("Development tooling and design library licences", "1", "lot", "\u00a3640", 640),
    ("Domain, TLS and identity services", "1", "lot", "\u00a365", 65),
]
TOTAL_INFRA = sum(a for *_, a in INFRA)

TOTAL_LOC = 3826
GRAND_TOTAL = TOTAL_EFFORT + TOTAL_INFRA

INVOICE_LINES = [
    ("Design, build, verification and evaluation of the computational pathology triage "
     "platform, delivered as a working prototype with browser inference, evaluation "
     "harness and technical documentation (lot).", 1, TOTAL_EFFORT, TOTAL_EFFORT),
    ("Infrastructure, dataset acquisition and third-party API consumption incurred in "
     "delivery (lot).", 1, TOTAL_INFRA, TOTAL_INFRA),
]
SUBTOTAL = TOTAL_EFFORT + TOTAL_INFRA
VAT = 0
TOTAL_DUE = SUBTOTAL + VAT

story = []

# ================================================================ COVER
story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=2.5, color=NAVY, spaceAfter=12))
story.append(Paragraph(LAB_NAME, H1))
story.append(Paragraph(LAB_TAG, SMALL))
story.append(Spacer(1, 3))
story.append(Paragraph("{}  |  {}  |  {}".format(LAB_ADDRESS, LAB_COMPANY, LAB_VAT),
                       SMALL))
story.append(Paragraph(CONTACT, SMALL))
story.append(HRFlowable(width="100%", thickness=0.8, color=LINE, spaceBefore=10,
                        spaceAfter=14))

story.append(Paragraph("Development Cost Statement", H1))
story.append(Paragraph(REFERENCE, BODY))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Statement of the effort, infrastructure and third-party consumption applied to "
    "the design, build, verification and evaluation of the computational pathology "
    "triage platform, covering the period to {}.".format(INVOICE_DATE), BODY))
story.append(Spacer(1, 10))

# headline figures
kpi = Table([[
    Paragraph(money(TOTAL_EFFORT), BIG), Paragraph(money(TOTAL_INFRA), BIG),
    Paragraph(str(TOTAL_LOC), BIG), Paragraph(money(GRAND_TOTAL), BIG)],
    [Paragraph("Engineering effort", BIGL),
     Paragraph("Infrastructure, data and API consumption", BIGL),
     Paragraph("Lines of production code", BIGL),
     Paragraph("Total cost of development", BIGL)]],
    colWidths=[41 * mm] * 4)
kpi.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
    ("TOPPADDING", (0, 0), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
]))
story.append(kpi)
story.append(Spacer(1, 12))

story.append(Paragraph("Basis of preparation", H2))
story.append(Paragraph(
    "Figures shown as MEASURED are verified directly against the delivered repository "
    "and are reproducible: code volume, artefact sizes, evaluation corpus size and "
    "verification results.", BODY))
story.append(Paragraph(
    "Figures shown as MODELLED are a planning schedule. Day rates reflect senior UK "
    "contract market rates for the disciplines engaged. Effort in days and third-party "
    "consumption are estimates and should be replaced with actuals, drawn from timesheets "
    "and provider billing, before this statement is issued externally.", BODY))
story.append(Paragraph(
    "This document is a cost statement. It becomes a valid VAT invoice on insertion of "
    "the registered company details and VAT number above.", NOTE))
story.append(PageBreak())

# ================================================================ SCOPE
story.append(Paragraph("1. Scope delivered", H1))
story.append(Paragraph("All figures in this section are MEASURED from the repository.",
                       NOTE))

story.append(Paragraph("1.1 Production code", H3))
story.append(table([
    [Paragraph("<b>Component</b>", CELLB), Paragraph("<b>Modules</b>", CELLR),
     Paragraph("<b>Lines</b>", CELLR)],
    [Paragraph("Model, inference and API layer (Python)", CELL), Paragraph("25", CELLR),
     Paragraph("2,388", CELLR)],
    [Paragraph("Clinical dashboard (React, JSX and CSS)", CELL), Paragraph("16", CELLR),
     Paragraph("1,438", CELLR)],
    [Paragraph("<b>Total</b>", CELLB), Paragraph("<b>41</b>", CELLRB),
     Paragraph("<b>3,826</b>", CELLRB)],
], [110 * mm, 30 * mm, 30 * mm], total_rows=(3,)))

story.append(Paragraph("1.2 Trained artefacts and deployment assets", H3))
story.append(table([
    [Paragraph("<b>Artefact</b>", CELLB), Paragraph("<b>Size</b>", CELLR),
     Paragraph("<b>Status</b>", CELL)],
    [Paragraph("model.pth (ResNet50 backbone, 3-class head)", CELL),
     Paragraph("94.36 MB", CELLR), Paragraph("Delivered, superseded", CELL)],
    [Paragraph("LungDisease_Classifier.pth (LC25000CNN, 4,750,885 parameters)", CELL),
     Paragraph("19.01 MB", CELLR), Paragraph("Delivered, in service", CELL)],
    [Paragraph("lung_classifier.onnx (browser inference graph)", CELL),
     Paragraph("19.01 MB", CELLR), Paragraph("Delivered, in service", CELL)],
    [Paragraph("WebAssembly inference runtime", CELL), Paragraph("14.24 MB", CELLR),
     Paragraph("Vendored and pinned", CELL)],
    [Paragraph("Funder deck and hosting assessment documents", CELL),
     Paragraph("0.02 MB", CELLR), Paragraph("Delivered", CELL)],
], [95 * mm, 28 * mm, 47 * mm]))

story.append(Paragraph("1.3 Verification and evaluation", H3))
story.append(table([
    [Paragraph("<b>Activity</b>", CELLB), Paragraph("<b>Result</b>", CELL),
     Paragraph("<b>Basis</b>", CELL)],
    [Paragraph("Numerical parity, PyTorch against ONNX Runtime", CELL),
     Paragraph("3.8e-06 maximum absolute difference", CELL),
     Paragraph("Measured", CELL)],
    [Paragraph("Labelled evaluation corpus", CELL),
     Paragraph("120 images, 40 per class", CELL), Paragraph("Measured", CELL)],
    [Paragraph("Label-mapping determination", CELL),
     Paragraph("All 6 permutations evaluated, best mapping identified", CELL),
     Paragraph("Measured", CELL)],
    [Paragraph("End-to-end smoke test", CELL),
     Paragraph("6 of 6 checks passed", CELL), Paragraph("Measured", CELL)],
    [Paragraph("Three-class accuracy, held-out data", CELL),
     Paragraph("Not yet established", CELL), Paragraph("Outstanding", CELL)],
], [70 * mm, 60 * mm, 40 * mm]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "The evaluation corpus is drawn from the same public dataset used for training and "
    "therefore is not a held-out result. Establishing a held-out split is the first "
    "milestone of the funded programme.", NOTE))
story.append(PageBreak())

# ================================================================ EFFORT
story.append(Paragraph("2. Engineering effort applied", H1))
story.append(Paragraph(
    "MODELLED. Day rates reflect senior UK contract market rates. Effort is derived from "
    "the delivered scope above and should be reconciled to timesheets.", NOTE))
story.append(Spacer(1, 4))

effort_rows = [[Paragraph("<b>Role</b>", CELLB), Paragraph("<b>Day rate</b>", CELLR),
                Paragraph("<b>Days</b>", CELLR), Paragraph("<b>Amount</b>", CELLR)]]
for role, rate, days in EFFORT:
    effort_rows.append([Paragraph(role, CELL), Paragraph(money(rate), CELLR),
                        Paragraph(str(days), CELLR),
                        Paragraph(money(rate * days), CELLR)])
effort_rows.append([Paragraph("<b>Total engineering effort</b>", CELLB),
                    Paragraph("", CELLR), Paragraph("", CELLR),
                    Paragraph("<b>{}</b>".format(money(TOTAL_EFFORT)), CELLRB)])
story.append(table(effort_rows, [78 * mm, 26 * mm, 20 * mm, 46 * mm],
                   total_rows=(len(effort_rows) - 1,)))
story.append(Spacer(1, 8))

story.append(Paragraph("2.1 Effort distribution", H3))
dist_rows = [[Paragraph("<b>Workstream</b>", CELLB), Paragraph("<b>Description</b>", CELL),
              Paragraph("<b>Days</b>", CELLR)]]
for name, desc, days in WORKSTREAMS:
    dist_rows.append([Paragraph(name, CELL), Paragraph(desc, CELL),
                      Paragraph(str(days), CELLR)])
story.append(table(dist_rows, [42 * mm, 108 * mm, 20 * mm]))
story.append(PageBreak())

# ================================================================ INFRA
story.append(Paragraph("3. Infrastructure, data and API consumption", H1))
story.append(Paragraph(
    "MODELLED. Usage figures are estimates for the period and should be replaced with "
    "provider billing data before external issue.", NOTE))
story.append(Spacer(1, 4))

infra_rows = [[Paragraph("<b>Item</b>", CELLB), Paragraph("<b>Quantity</b>", CELLR),
               Paragraph("<b>Rate</b>", CELLR), Paragraph("<b>Amount</b>", CELLR)]]
for item, qty, unit, rate, amount in INFRA:
    infra_rows.append([Paragraph(item, CELL),
                       Paragraph("{} {}".format(qty, unit), CELLR),
                       Paragraph(rate, CELLR), Paragraph(money(amount), CELLR)])
infra_rows.append([Paragraph("<b>Total infrastructure and consumption</b>", CELLB),
                   Paragraph("", CELLR), Paragraph("", CELLR),
                   Paragraph("<b>{}</b>".format(money(TOTAL_INFRA)), CELLRB)])
story.append(table(infra_rows, [72 * mm, 30 * mm, 22 * mm, 46 * mm],
                   total_rows=(len(infra_rows) - 1,)))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Planned allocations not yet drawn, including the supercomputing allocation referred "
    "to in the funding strategy, are excluded from this statement and will be reported "
    "against the period in which they are consumed.", NOTE))
story.append(PageBreak())

# ================================================================ INVOICE
story.append(HRFlowable(width="100%", thickness=2.5, color=NAVY, spaceAfter=10))
story.append(Paragraph("Invoice", H1))
story.append(Paragraph("{}  |  Date: {}".format(INVOICE_NO, INVOICE_DATE), BODY))
story.append(HRFlowable(width="100%", thickness=0.8, color=LINE, spaceBefore=4,
                        spaceAfter=10))

meta = Table([
    [Paragraph("<b>From</b>", CELLB), Paragraph("<b>Bill to</b>", CELLB),
     Paragraph("<b>Reference</b>", CELLB)],
    [Paragraph("{}<br/>{}, {}<br/>{}<br/>{}".format(
        LAB_NAME, LAB_ADDRESS, LAB_COMPANY, LAB_VAT, CONTACT), CELL),
     Paragraph("{}<br/>{}".format(CLIENT, CLIENT_ADDRESS), CELL),
     Paragraph(REFERENCE, CELL)],
], colWidths=[58 * mm, 58 * mm, 54 * mm])
story.append(meta)
story.append(Spacer(1, 10))

line_rows = [[Paragraph("<b>Description</b>", CELLB),
              Paragraph("<b>Qty</b>", CELLR),
              Paragraph("<b>Unit</b>", CELLR),
              Paragraph("<b>Amount</b>", CELLR)]]
for desc, qty, unit, amount in INVOICE_LINES:
    line_rows.append([Paragraph(desc, CELL), Paragraph(str(qty), CELLR),
                      Paragraph(money(unit), CELLR), Paragraph(money(amount), CELLR)])
line_rows.append([Paragraph("<b>Subtotal</b>", CELLB), Paragraph("", CELLR),
                  Paragraph("", CELLR), Paragraph("<b>{}</b>".format(money(SUBTOTAL)),
                                                  CELLRB)])
line_rows.append([Paragraph("VAT (registration pending)", CELL), Paragraph("", CELLR),
                  Paragraph("", CELLR), Paragraph(money(VAT), CELLR)])
line_rows.append([Paragraph("<b>Total due</b>", CELLB), Paragraph("", CELLR),
                  Paragraph("", CELLR), Paragraph("<b>{}</b>".format(money(TOTAL_DUE)),
                                                  CELLRB)])
story.append(table(line_rows, [88 * mm, 18 * mm, 24 * mm, 40 * mm],
                   total_rows=(len(line_rows) - 3, len(line_rows) - 1)))
story.append(Spacer(1, 12))

terms = Table([
    [Paragraph("<b>Payment terms</b>", CELLB),
     Paragraph("<b>Bank details</b>", CELLB)],
    [Paragraph("Payment due within 30 days of the invoice date. Remittance advice to "
               "the contact address above.", CELL),
     Paragraph("[Bank name]<br/>[Account name]<br/>[Sort code]  [Account number]<br/>"
               "[IBAN]  [BIC]", CELL)],
], colWidths=[85 * mm, 85 * mm])
story.append(terms)
story.append(Spacer(1, 14))
story.append(HRFlowable(width="100%", thickness=0.8, color=LINE, spaceAfter=8))
story.append(Paragraph(
    "Prepared by the technical function of {}. Figures marked MEASURED are reproducible "
    "from the delivered repository. Figures marked MODELLED are a planning schedule and "
    "are subject to confirmation.".format(LAB_NAME), NOTE))

doc = SimpleDocTemplate(OUT, pagesize=PAGE,
                        leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=15 * mm,
                        title="Development Cost Statement and Invoice",
                        author=LAB_NAME)
doc.build(story)
print("WROTE", OUT)