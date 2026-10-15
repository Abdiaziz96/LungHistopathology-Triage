"""Funder deck. Plain declarative prose, no editorial voice."""
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak)

OUT = "Lung_Triage_Funder_Deck.pdf"
PAGE = landscape((297 * mm, 167 * mm))

NAVY = colors.HexColor("#0B2545")
GREY = colors.HexColor("#5B6470")
LIGHT = colors.HexColor("#F1F4F8")
LINE = colors.HexColor("#D5DCE5")

TITLE = ParagraphStyle("TITLE", fontName="Helvetica-Bold", fontSize=31, leading=35,
                       textColor=NAVY, spaceAfter=8)
SUBT = ParagraphStyle("SUBT", fontName="Helvetica", fontSize=14.5, leading=19,
                      textColor=GREY, spaceAfter=5)
HEAD = ParagraphStyle("HEAD", fontName="Helvetica-Bold", fontSize=22, leading=26,
                      textColor=NAVY, spaceAfter=8)
BODY = ParagraphStyle("BODY", fontName="Helvetica", fontSize=12.5, leading=17.5,
                      textColor=colors.HexColor("#1F2933"), spaceAfter=7)
BUL = ParagraphStyle("BUL", parent=BODY, leftIndent=14, bulletIndent=3, spaceAfter=8)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=10, leading=13.5,
                       textColor=GREY)
KPI = ParagraphStyle("KPI", fontName="Helvetica-Bold", fontSize=24, leading=27,
                     textColor=NAVY, alignment=1)
KPIL = ParagraphStyle("KPIL", fontName="Helvetica", fontSize=9.5, leading=12,
                      textColor=GREY, alignment=1)
CELL = ParagraphStyle("CELL", fontName="Helvetica", fontSize=10.5, leading=14,
                      textColor=colors.HexColor("#1F2933"))

story = []


def slide(heading, sub, flow):
    story.append(Paragraph(heading, HEAD))
    if sub:
        story.append(Paragraph(sub, SUBT))
    story.append(Spacer(1, 4))
    story.extend(flow)
    story.append(PageBreak())


def bullets(items):
    return [Paragraph(t, BUL, bulletText="\u2022") for t in items]


def grid(rows, widths, header=True):
    t = Table(rows, colWidths=widths)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), LIGHT))
    t.setStyle(TableStyle(style))
    return t


# 1 cover
story.append(Spacer(1, 34))
story.append(Paragraph("Lung Histopathology Triage", TITLE))
story.append(Paragraph(
    "AI-assisted triage for lung cancer screening in capacity-constrained health systems.",
    SUBT))
story.append(Spacer(1, 16))
story.append(Paragraph(
    "A working prototype. The classifier is 19 MB and runs entirely in a web browser on "
    "commodity hardware, with no GPU and no inference server.", BODY))
story.append(Spacer(1, 20))
story.append(grid([[Paragraph("<b>Seed round</b><br/>$1M", KPIL),
                    Paragraph("<b>Scale round</b><br/>$5M", KPIL),
                    Paragraph("<b>Non-dilutive</b><br/>Cloud and HPC credits", KPIL),
                    Paragraph("<b>Model</b><br/>19 MB, in-browser", KPIL)]],
                  [60 * mm] * 4, header=False))
story.append(PageBreak())

# 2 problem
story.append(Paragraph("Pathology capacity is the constraint", HEAD))
story.extend(bullets([
    "Screening programmes and ageing populations increase slide volumes. Pathologist "
    "numbers are not increasing at the same rate.",
    "Triage is manual. Every case waits for specialist review, including the large "
    "majority that prove benign.",
    "Time to diagnosis is governed by queue position rather than by disease biology, and "
    "it is the variable that most affects patient outcome.",
    "Laboratories in lower-resource settings carry comparable caseloads with a fraction "
    "of the specialist capacity, and are least served by software priced for "
    "well-resourced hospitals.",
]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "The opportunity is faster and cheaper routing of cases, so that specialist time is "
    "spent where it changes an outcome.", BODY))
story.append(PageBreak())

# 3 product
slide("What the system does today", None, bullets([
    "End-to-end pipeline: slide upload, preprocessing, classification and an "
    "explainability overlay, presented in a single-page clinical interface.",
    "The model runs in the browser. It was exported to ONNX and verified client-side, so "
    "there is no GPU requirement, no inference server and no per-request inference cost.",
    "Numerical parity with the reference PyTorch implementation is verified at 3.8e-06 on "
    "identical input.",
    "The deployment artefact is a set of static files, so hosting and demonstration carry "
    "no meaningful marginal cost.",
]))

# 4 validation
story.append(Paragraph("Validation status", HEAD))
story.append(Paragraph("Measured on 120 labelled LC25000 images, 40 per class.", SUBT))
story.append(Spacer(1, 8))
story.append(grid([[Paragraph("66.7%", KPI), Paragraph("120 of 120", KPI),
                    Paragraph("0 of 80", KPI), Paragraph("19 MB", KPI)],
                   [Paragraph("3-class accuracy", KPIL),
                    Paragraph("benign vs malignant", KPIL),
                    Paragraph("adenocarcinoma vs squamous", KPIL),
                    Paragraph("model, in-browser", KPIL)]],
                  [62 * mm] * 4, header=False))
story.append(Spacer(1, 14))
story.append(Paragraph(
    "The model separates benign from malignant tissue reliably across all 120 samples. "
    "Adenocarcinoma and squamous cell carcinoma are not yet separated: all 80 malignant "
    "samples map to a single output, so the current model functions as a binary "
    "benign/malignant classifier.", BODY))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "These images come from the same public dataset used for training, so this is not a "
    "held-out result. Establishing a held-out split and publishing a validated accuracy "
    "figure is the first milestone of Phase 1.", BODY))
story.append(PageBreak())

# 5 development status
story.append(Paragraph("Development status", HEAD))
story.append(Paragraph(
    "Each item is scoped as work, with the Phase 1 deliverable named.", SUBT))
story.append(Spacer(1, 8))
rows = [[Paragraph("<b>Area</b>", CELL), Paragraph("<b>Current status</b>", CELL),
         Paragraph("<b>Phase 1 deliverable</b>", CELL)]]
for area, status, deliver in [
    ("Subtype discrimination",
     "Adenocarcinoma and squamous carcinoma are not separated by the current model "
     "(0 of 80 samples).",
     "Retrained model with three-class discrimination measured on held-out data."),
    ("Validation",
     "Figures are drawn from the training dataset. No held-out split exists yet.",
     "Held-out and external validation, with a published confusion matrix."),
    ("Data",
     "Public research dataset only.",
     "Clinical data partnerships and a validated dataset of record."),
    ("Governance",
     "Not yet initiated.",
     "Data protection impact assessment, ethics submission and data-sharing framework."),
    ("Explainability",
     "Occlusion sensitivity, used because browser inference has no gradient pass.",
     "Benchmark against the reference method, plus a clinician usability study."),
    ("Regulatory",
     "Not approved. The system is labelled not for clinical use.",
     "Quality management system and a submission-ready technical file."),
]:
    rows.append([Paragraph(area, CELL), Paragraph(status, CELL), Paragraph(deliver, CELL)])
story.append(grid(rows, [42 * mm, 98 * mm, 95 * mm]))
story.append(PageBreak())

# 6 funding to scope
story.append(Paragraph("Every item above maps to a funded workstream", HEAD))
story.append(Spacer(1, 8))
rows = [[Paragraph("<b>Area</b>", CELL), Paragraph("<b>Funded workstream</b>", CELL),
         Paragraph("<b>Verifiable outcome</b>", CELL)]]
for area, work, outcome in [
    ("Subtype discrimination",
     "Architecture and loss redesign, with compute-intensive retraining.",
     "Three-class accuracy on held-out data, published."),
    ("Validation",
     "Curated splits, an external validation set and an evaluation harness.",
     "Reproducible accuracy and confusion matrix, reviewable by third parties."),
    ("Data",
     "Clinical data partnerships, labelling and quality assurance.",
     "Signed agreements and a validated dataset of record."),
    ("Governance",
     "Data protection impact assessment, ethics submission, data-sharing framework.",
     "Approved governance pack, reusable across jurisdictions."),
    ("Explainability",
     "Method comparison study against the reference approach.",
     "Agreement metrics and a clinician usability study."),
    ("Regulatory",
     "Quality management system and regulatory strategy.",
     "Audited quality system and a submission-ready technical file."),
]:
    rows.append([Paragraph(area, CELL), Paragraph(work, CELL), Paragraph(outcome, CELL)])
story.append(grid(rows, [42 * mm, 98 * mm, 95 * mm]))
story.append(PageBreak())

# 7 capital efficiency
slide("Why the remaining work is capital-efficient", None, bullets([
    "The engineering risk is retired. The pipeline exists, it runs on commodity hardware, "
    "and its numerical correctness is verified.",
    "The model is 19 MB and inference is client-side, so there is no GPU fleet and no "
    "inference infrastructure to fund.",
    "Marginal cost per user approaches zero, which is what makes deployment viable in "
    "lower-resource health systems.",
    "The remaining cost is compute and validation rather than invention.",
    "Compute access is the highest-leverage form of support available, because donated "
    "credits and supercomputing allocation convert directly into validation throughput.",
]))

# 8 use of funds
story.append(Paragraph("Use of funds", HEAD))
story.append(Paragraph(
    "Staged so that a funder can stop after Phase 1 and still see a complete, verified "
    "result. Figures are planning targets, not quotations.", SUBT))
story.append(Spacer(1, 8))
rows = [[Paragraph("<b>Phase</b>", CELL), Paragraph("<b>Ask</b>", CELL),
         Paragraph("<b>Focus</b>", CELL), Paragraph("<b>Milestone at exit</b>", CELL)],
        [Paragraph("<b>Phase 1</b>", CELL), Paragraph("<b>$1M</b>", CELL),
         Paragraph("Subtyping model, held-out validation, governance pack, cloud and HPC "
                   "compute.", CELL),
         Paragraph("Published three-class accuracy on held-out and clinical data.", CELL)],
        [Paragraph("<b>Phase 2</b>", CELL), Paragraph("<b>$5M</b>", CELL),
         Paragraph("Clinical pilots in capacity-constrained systems, regulatory submission, "
                   "team and support.", CELL),
         Paragraph("Regulatory filing and validated deployment in a live pathway.", CELL)],
        [Paragraph("<b>In kind</b>", CELL), Paragraph("Credits and HPC", CELL),
         Paragraph("Training compute, validation sweeps, evaluation infrastructure.", CELL),
         Paragraph("A documented compute-to-result trail.", CELL)]]
story.append(grid(rows, [26 * mm, 30 * mm, 95 * mm, 84 * mm]))
story.append(PageBreak())

# 9 the ask
slide("The ask", None, bullets([
    "Sovereign and development funds: $1M seed, followed by $5M at scale. The deliverable "
    "is a validated, deployable triage layer with measured impact on time to diagnosis in "
    "a screening pathway.",
    "Cloud and compute credit programmes: the fastest route to accelerating this work. "
    "Credits convert directly into validation throughput, are non-dilutive, and carry no "
    "execution risk for the provider.",
    "Supercomputing allocation: retraining for subtype discrimination is compute-bound. An "
    "allocation compresses a twelve-month model roadmap into a quarter.",
    "Impact measurement: quantifying patients reached and health system cost avoided in "
    "target deployment regions is a funded Phase 1 deliverable, and is reported against "
    "published methodology.",
]))

# 10 milestones
story.append(Paragraph("Phase 1 milestones", HEAD))
story.extend(bullets([
    "Published three-class accuracy on held-out data, with the confusion matrix and "
    "evaluation script released alongside it.",
    "Subtype discrimination demonstrated at a clinically useful level.",
    "Validation on clinical data from partner centres, with governance approved and "
    "documented.",
    "Explainability benchmarked against the reference method and reviewed by pathologists.",
    "Quality management system in place and a regulatory submission strategy agreed.",
]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "The system remains labelled retrospective validation only, not for clinical use, "
    "until these milestones are met.", BODY))

doc = SimpleDocTemplate(OUT, pagesize=PAGE,
                        leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=15 * mm, bottomMargin=13 * mm,
                        title="Lung Histopathology Triage - Funder Deck",
                        author="Technical Co-founder")
doc.build(story)
print("WROTE", OUT)