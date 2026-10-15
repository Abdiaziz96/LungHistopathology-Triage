"""Generate the funder slide deck (landscape 16:9 PDF)."""
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak)

OUT = "Lung_Triage_Funder_Deck.pdf"
PAGE = landscape((297 * mm, 167 * mm))
W, H = PAGE

NAVY = colors.HexColor("#0B2545")
ACCENT = colors.HexColor("#005EB8")
GREEN = colors.HexColor("#0F7B4F")
AMBER = colors.HexColor("#B45309")
RED = colors.HexColor("#B91C1C")
GREY = colors.HexColor("#5B6470")
LIGHT = colors.HexColor("#F1F4F8")

TITLE = ParagraphStyle("TITLE", fontName="Helvetica-Bold", fontSize=30, leading=34,
                       textColor=NAVY, spaceAfter=6)
SUB = ParagraphStyle("SUB", fontName="Helvetica", fontSize=14, leading=19,
                     textColor=GREY, spaceAfter=4)
H = ParagraphStyle("H", fontName="Helvetica-Bold", fontSize=23, leading=27,
                   textColor=NAVY, spaceAfter=9)
BODY = ParagraphStyle("BODY", fontName="Helvetica", fontSize=12.5, leading=17.5,
                      textColor=colors.HexColor("#1F2933"), spaceAfter=6)
BULL = ParagraphStyle("BULL", parent=BODY, leftIndent=13, bulletIndent=2, spaceAfter=7)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=10, leading=13.5,
                       textColor=GREY)
KPI = ParagraphStyle("KPI", fontName="Helvetica-Bold", fontSize=25, leading=28,
                     textColor=NAVY, alignment=1)
KPIL = ParagraphStyle("KPIL", fontName="Helvetica", fontSize=9.5, leading=12,
                      textColor=GREY, alignment=1)

story = []


def slide(title, sub, flow, footer=None):
    story.append(Paragraph(title, H))
    if sub:
        story.append(Paragraph(sub, SUB))
    story.append(Spacer(1, 5))
    story.extend(flow)
    if footer:
        story.append(Spacer(1, 8))
        story.append(Paragraph(footer, SMALL))
    story.append(PageBreak())


def bullets(items):
    return [Paragraph(t, BULL, bulletText="\u2013") for t in items]


# ── 1 title ───────────────────────────────────────────────────────────────
story.append(Spacer(1, 30))
story.append(Paragraph("Lung Histopathology Triage", TITLE))
story.append(Paragraph(
    "An AI-assisted triage platform for lung cancer screening in "
    "capacity-constrained health systems.", SUB))
story.append(Spacer(1, 16))
story.append(Paragraph(
    "<b>Working prototype today.</b> A 19 MB classifier that runs entirely in a browser "
    "on commodity hardware, with no GPU and no server. Built, measured, and honest about "
    "where it fails \u2014 this document states both.", BODY))
story.append(Spacer(1, 18))
t = Table([[Paragraph("<b>Seed round</b><br/>$1M", KPIL),
            Paragraph("<b>Scale round</b><br/>$5M", KPIL),
            Paragraph("<b>Non-dilutive</b><br/>Cloud + HPC credits", KPIL),
            Paragraph("<b>Model size</b><br/>19 MB, in-browser", KPIL)]],
          colWidths=[60*mm]*4)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), LIGHT),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#D5DCE5")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#D5DCE5")),
    ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9),
]))
story.append(t)
story.append(PageBreak())

# ── 2 problem ─────────────────────────────────────────────────────────────
slide("The problem is throughput, not capability", 
      "Pathology is the bottleneck in every cancer pathway, and it is a people problem.",
      bullets([
          "<b>Demand is rising faster than the workforce.</b> Screening programmes and "
          "ageing populations expand the caseload; pathologist numbers are not scaling with it.",
          "<b>Triage is manual and serial.</b> Every slide waits for scarce specialist "
          "attention, including the large majority that are ultimately benign.",
          "<b>The cost of delay is clinical.</b> Time-to-diagnosis is the variable that "
          "changes outcomes, and it is governed by queue position, not by disease biology.",
          "<b>Emerging systems are hit hardest.</b> Laboratories in lower-resource settings "
          "carry the same caseload with a fraction of the specialist capacity \u2014 and are "
          "the least served by software priced for well-resourced hospitals.",
      ]),
      "The opportunity is not a better diagnosis. It is a cheaper, faster way to route cases "
      "so that specialist time lands where it changes an outcome.")

# ── 3 what exists ─────────────────────────────────────────────────────────
slide("What already works", 
      "Not a concept. A running system, measured, with the failures documented in the next slide.",
      bullets([
          "<b>End-to-end pipeline.</b> Slide upload, preprocessing, classification, and "
          "explainability overlay, in a single-page clinical interface.",
          "<b>Runs in the browser.</b> The model was exported to ONNX and verified to run "
          "client-side \u2014 no GPU, no inference server, no per-request cost.",
          "<b>Numerical parity proven.</b> Browser inference matches the reference PyTorch "
          "implementation to <b>3.8e-06</b> on identical input. Not an approximation.",
          "<b>Deployment surface is trivial.</b> Static assets. It can be hosted for "
          "effectively zero marginal cost and demonstrated from a single URL.",
          "<b>Triage layer scaffolded.</b> The interface and pipeline that route a case "
          "after classification are in place.",
      ]))

# ── 4 results ─────────────────────────────────────────────────────────────
story.append(Paragraph("Where we are, measured", H))
story.append(Paragraph(
    "Evaluated on 120 labelled LC25000 images (40 per class). The number below is the real "
    "one, including the part that is zero.", SUB))
story.append(Spacer(1, 8))

kpi = Table([[
    Paragraph("66.7%", KPI), Paragraph("120/120", KPI),
    Paragraph("0/80", KPI), Paragraph("19 MB", KPI)],
    [Paragraph("3-class accuracy", KPIL),
     Paragraph("benign vs malignant", KPIL),
     Paragraph("adeno vs squamous", KPIL),
     Paragraph("model, in-browser", KPIL)]],
    colWidths=[62*mm]*4)
kpi.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), LIGHT),
    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#D5DCE5")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#D5DCE5")),
    ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
]))
story.append(kpi)
story.append(Spacer(1, 10))
story.append(Paragraph(
    "<b>Reading it plainly.</b> The model reliably separates <b>benign from malignant</b> "
    "\u2014 every one of 120 images. It does <b>not</b> separate adenocarcinoma from squamous "
    "cell carcinoma: all 80 malignant cases collapse onto a single output. It is, today, a "
    "binary benign/malignant classifier wearing a three-class head.", BODY))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>And the caveat that matters more than the number.</b> These 120 images come from the "
    "same public dataset the model was trained on. This is <b>not</b> a held-out test set, so "
    "100% benign/malignant recall is consistent with memorisation rather than generalisation. "
    "We report it as such rather than presenting it as clinical accuracy.", BODY))
story.append(PageBreak())

# ── 5 shortcomings ────────────────────────────────────────────────────────
slide("The shortcomings, stated first",
      "Each one is a workstream, and each workstream is what the funding buys.",
      bullets([
          "<b>1. Cancer subtyping does not work.</b> Adenocarcinoma and squamous carcinoma "
          "are indistinguishable to the current model (0/80). Subtype determines treatment, "
          "so this is the single largest functional gap.",
          "<b>2. No held-out validation.</b> No train/test split exists against unseen data. "
          "Without it there is no defensible accuracy claim \u2014 and no regulatory path.",
          "<b>3. Trained on public research data, not clinical data.</b> Real-world slides "
          "differ in staining, scanner, and preparation. The model is out-of-distribution on "
          "them, which we have observed directly.",
          "<b>4. No clinical data access yet.</b> Live data requires a data-sharing "
          "agreement, a data protection impact assessment, and research ethics approval. "
          "Legal review alone is not sufficient.",
          "<b>5. Explainability is approximated.</b> Browser inference has no gradient pass, "
          "so we use occlusion sensitivity instead of Grad-CAM. Defensible, but it needs "
          "validation against the reference method.",
          "<b>6. No regulatory approval.</b> The system is explicitly labelled "
          "\u201cnot for clinical use\u201d. That is a deliberate and honest control, and "
          "lifting it is a funded programme, not a code change.",
      ]))

# ── 6 funding maps to gaps ────────────────────────────────────────────────
story.append(Paragraph("Every gap maps to a funded workstream", H))
story.append(Paragraph(
    "This is a specificity test. Each row states what is broken, what fixes it, and what a "
    "funder can verify at the end.", SUB))
story.append(Spacer(1, 8))

rows = [
    [Paragraph("<b>Gap</b>", BODY), Paragraph("<b>Funded workstream</b>", BODY),
     Paragraph("<b>Verifiable outcome</b>", BODY)],
    [Paragraph("Subtype collapse", BODY),
     Paragraph("Architecture and loss redesign; compute-intensive retraining", BODY),
     Paragraph("Three-class accuracy on held-out data, published", BODY)],
    [Paragraph("No held-out validation", BODY),
     Paragraph("Curated splits, external validation set, evaluation harness", BODY),
     Paragraph("Reproducible accuracy + confusion matrix, third-party reviewable", BODY)],
    [Paragraph("Public data only", BODY),
     Paragraph("Clinical data partnerships; labelling and QA pipeline", BODY),
     Paragraph("Signed agreements; a validated dataset of record", BODY)],
    [Paragraph("Governance unaddressed", BODY),
     Paragraph("DPIA, ethics submission, data-sharing framework", BODY),
     Paragraph("Approved governance pack, reusable per jurisdiction", BODY)],
    [Paragraph("Explainability unvalidated", BODY),
     Paragraph("Method comparison study against Grad-CAM reference", BODY),
     Paragraph("Agreement metrics; clinician usability study", BODY)],
    [Paragraph("No regulatory path", BODY),
     Paragraph("Quality management system; regulatory strategy", BODY),
     Paragraph("Audited QMS; submission-ready technical file", BODY)],
]
t = Table(rows, colWidths=[45*mm, 95*mm, 95*mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), LIGHT),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D5DCE5")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(PageBreak())

# ── 7 why now ─────────────────────────────────────────────────────────────
slide("Why now, and why this is cheap to fund",
      "The expensive work is already done with no capital. What remains is compute and validation.",
      bullets([
          "<b>The hard engineering risk is retired.</b> The pipeline exists, runs on "
          "commodity hardware, and its numerical correctness is verified. There is no "
          "technical unknown standing between this and a validation programme.",
          "<b>Capital intensity is unusually low.</b> A 19 MB model that runs in a browser "
          "needs no GPU fleet and no inference infrastructure. Marginal cost per user "
          "approaches zero \u2014 which is precisely what makes deployment viable in "
          "lower-resource health systems.",
          "<b>The remaining cost is compute and rigour, not invention.</b> Training to "
          "separate subtypes, validating on held-out and clinical data, and building the "
          "governance and quality systems. All are well-understood, budgetable work.",
          "<b>Compute access is the lever.</b> Donated cloud credits and HPC allocation "
          "convert directly into validation throughput for this project \u2014 the "
          "highest-return form of non-dilutive support available.",
          "<b>Timing.</b> Every health system is under the same throughput pressure "
          "simultaneously. The window for a low-cost triage layer is now, not in five years.",
      ]))

# ── 8 use of funds ────────────────────────────────────────────────────────
story.append(Paragraph("Use of funds", H))
story.append(Paragraph(
    "Staged so that a funder can stop after Phase 1 and still see a complete, verified "
    "result. Figures are planning targets, not quotations.", SUB))
story.append(Spacer(1, 8))

rows = [
    [Paragraph("<b>Phase</b>", BODY), Paragraph("<b>Ask</b>", BODY),
     Paragraph("<b>Focus</b>", BODY), Paragraph("<b>Milestone at exit</b>", BODY)],
    [Paragraph("<b>Phase 1</b>", BODY), Paragraph("<b>$1M</b>", BODY),
     Paragraph("Subtyping model; held-out validation; governance pack; cloud/HPC compute",
               BODY),
     Paragraph("Published three-class accuracy on held-out and clinical data", BODY)],
    [Paragraph("<b>Phase 2</b>", BODY), Paragraph("<b>$5M</b>", BODY),
     Paragraph("Clinical pilots in capacity-constrained systems; regulatory submission; "
               "team and support", BODY),
     Paragraph("Regulatory filing; validated deployment in a live pathway", BODY)],
    [Paragraph("<b>In kind</b>", BODY), Paragraph("Credits + HPC", BODY),
     Paragraph("Training compute, validation sweeps, evaluation infrastructure", BODY),
     Paragraph("Documented compute-to-result trail", BODY)],
]
t = Table(rows, colWidths=[26*mm, 30*mm, 95*mm, 84*mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), LIGHT),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D5DCE5")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(PageBreak())

# ── 9 the ask ─────────────────────────────────────────────────────────────
slide("The ask",
      "Three routes in, because the support we need is not only money.",
      bullets([
          "<b>Sovereign and development funds \u2014 $1M seed, then $5M scale.</b> Health "
          "system capacity with a measurable output: time-to-diagnosis in a screening "
          "pathway. The deliverable is a validated, deployable triage layer, not a paper.",
          "<b>Cloud and compute credit programmes.</b> The single fastest way to accelerate "
          "this project. Credits convert straight into validation throughput, they are "
          "non-dilutive, and they carry no execution risk for the provider.",
          "<b>Supercomputing allocation.</b> Retraining for subtype discrimination is "
          "compute-bound. An allocation turns a twelve-month model roadmap into a "
          "quarterly one.",
          "<b>What we are not asking for.</b> We are not asking anyone to fund a hypothesis "
          "about a technology that might work. The prototype runs, its correctness is "
          "verified, and its weaknesses are quantified in this document. This is execution "
          "capital against a stated gap list.",
      ]),
      "<b>The case in one line:</b> a low-cost triage layer that runs on hardware already "
      "present in the clinic, with a funded plan to close the four gaps that currently stop "
      "it being clinical.")

# ── 10 closing ────────────────────────────────────────────────────────────
story.append(Paragraph("What we will be judged on", H))
story.append(Paragraph(
    "Stated now so that progress is falsifiable. These are the milestones we hold ourselves "
    "to, in order.", SUB))
story.append(Spacer(1, 8))
story.extend(bullets([
    "<b>Held-out accuracy, published.</b> A reproducible three-class number on data the "
    "model has never seen, with the confusion matrix released alongside it.",
    "<b>Subtype discrimination demonstrated.</b> Adenocarcinoma separated from squamous "
    "carcinoma at a level that is clinically useful, not merely above chance.",
    "<b>Validation on clinical data.</b> Performance on real slides from partner centres, "
    "with governance approved and documented.",
    "<b>Explainability validated.</b> The occlusion method benchmarked against the "
    "reference, and reviewed by pathologists for whether the highlighted regions are "
    "the ones a human would use.",
    "<b>A regulatory pathway opened.</b> Quality management system in place and a "
    "submission strategy agreed, so that lifting the \u201cnot for clinical use\u201d "
    "label becomes a schedule rather than an aspiration.",
]))
story.append(Spacer(1, 10))
story.append(Paragraph(
    "Until every one of those is met, the system stays labelled as it is today: "
    "<b>retrospective validation only \u2014 not for clinical use.</b> We would rather be "
    "funded for closing a stated gap list than for a claim we cannot reproduce.", BODY))

doc = SimpleDocTemplate(OUT, pagesize=PAGE,
                        leftMargin=18*mm, rightMargin=18*mm,
                        topMargin=15*mm, bottomMargin=13*mm,
                        title="Lung Histopathology Triage - Funder Deck",
                        author="Technical Co-founder")
doc.build(story)
print("WROTE", OUT)