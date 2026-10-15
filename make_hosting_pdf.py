from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether)

OUT = "Hosting_Plan.pdf"
styles = getSampleStyleSheet()

H1 = ParagraphStyle("H1", parent=styles["Title"], fontName="Helvetica-Bold",
                    fontSize=20, leading=24, spaceAfter=2, alignment=0,
                    textColor=colors.HexColor("#111111"))
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontName="Helvetica",
                     fontSize=9, leading=12, textColor=colors.HexColor("#666666"),
                     spaceAfter=10)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                    fontSize=12.5, leading=15, spaceBefore=13, spaceAfter=5,
                    textColor=colors.HexColor("#111111"))
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=9.5, leading=13.5, spaceAfter=5,
                      textColor=colors.HexColor("#1a1a1a"))
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=11, bulletIndent=2,
                        spaceAfter=3.5)
MONO = ParagraphStyle("MONO", parent=BODY, fontName="Courier", fontSize=8.5,
                      leading=12, leftIndent=10, textColor=colors.HexColor("#333333"),
                      spaceAfter=5)
NOTE = ParagraphStyle("NOTE", parent=BODY, fontSize=8.5, leading=11.5,
                      textColor=colors.HexColor("#555555"))

def bullets(items):
    return [Paragraph(t, BULLET, bulletText="-") for t in items]

story = []
story.append(Paragraph("Hosting the Lung Histopathology Triage MVP", H1))
story.append(Paragraph(
    "Deployment assessment - verified against the repository at "
    "C:\\Users\\Abdurrahman\\Documents\\DeepSeekHarness-Projects\\LungHistopathology-Triage",
    SUB))
story.append(HRFlowable(width="100%", thickness=1,
                        color=colors.HexColor("#d8d5cd"), spaceAfter=10))

# 1
story.append(Paragraph("1. What is actually blocking you", H2))
story.append(Paragraph(
    "There are two backends in the repo, and the one wired up for deployment is broken.", BODY))

data = [
    [Paragraph("<b></b>", BODY),
     Paragraph("<b>api.py (root)</b>", BODY),
     Paragraph("<b>backend/main.py</b>", BODY)],
    [Paragraph("Model class", BODY),
     Paragraph("LC25000CNN (Ghost-141, from pretrained_cnn.py)", BODY),
     Paragraph("SimpleCNN (3 conv layers, defined inline)", BODY)],
    [Paragraph("Label order", BODY),
     Paragraph("adenocarcinoma, benign, squamous_cell_carcinoma", BODY),
     Paragraph("0: Benign, 1: Adenocarcinoma, 2: Squamous", BODY)],
    [Paragraph("Verified", BODY),
     Paragraph("PASS - smoke test, live on :8000", BODY),
     Paragraph("FAIL - cannot load either checkpoint", BODY)],
]
t = Table(data, colWidths=[24*mm, 73*mm, 73*mm])
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#d8d5cd")),
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f2f0eb")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 5),
    ("RIGHTPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(t)
story.append(Spacer(1, 7))
story.append(Paragraph(
    "Proven failure: loading model.pth into SimpleCNN raises "
    "\"Unexpected key(s) in state_dict: backbone.conv1.weight, backbone.layer1.0...\" "
    "- that checkpoint is a ResNet50 (model.py), not SimpleCNN. So railway.toml "
    "(cd backend && python main.py), backend/Dockerfile and DEPLOYMENT.md all point "
    "at an app that can never work with your weights.", BODY))
story.extend(bullets([
    "<b>Silent failure mode:</b> on Windows it crashes printing an emoji (cp1252); on a "
    "Linux container it boots successfully with no model loaded, so it serves nonsense "
    "instead of erroring.",
    "<b>No weights in the repo:</b> both .pth files were untracked in git, so any deploy "
    "from git arrives with zero model files.",
    "<b>Minor:</b> root requirements.txt is missing fastapi and uvicorn (present only in "
    "backend/requirements.txt); lung-dashboard/.env points at http://localhost:8000 and "
    "must become the live API URL.",
]))

# 2
story.append(Paragraph("2. Why hosting is a real decision here", H2))
story.append(Paragraph(
    "torch occupies <b>490 MB on disk</b> in the virtual environment. That single fact "
    "eliminates the obvious free options.", BODY))
story.append(Paragraph("<b>Render (free)</b> - 0.1 CPU / 512 MB RAM. There is a documented "
    "case of exactly this stack (FastAPI + a local model + React) exceeding 512 MB on "
    "import. Free services also sleep, so a first visitor waits roughly a minute.", BODY))
story.append(Paragraph("<b>Hugging Face Spaces (CPU Basic)</b> - 2 vCPU / 16 GB RAM / 50 GB "
    "disk. The only free option that comfortably fits torch. <b>Unresolved uncertainty:</b> "
    "HF documentation states Docker and Gradio Spaces now require a paid plan while only "
    "Static Spaces are free, yet other HF pages still list CPU Basic as free. Verify "
    "directly before committing to this path.", BODY))

# 3
story.append(Paragraph("3. Recommended split", H2))
story.append(Paragraph("<b>Frontend to Vercel (free).</b> lung-dashboard/ is a plain Vite app; "
    "npm run build produces a static dist/. Nothing about it needs a server. Set "
    "VITE_API_BASE to the backend URL as a build-time environment variable.", BODY))
story.append(Paragraph("<b>Backend to Hugging Face Spaces (Docker) if still free, otherwise "
    "Railway hobby tier (about $5/month).</b> Keep torch. The Grad-CAM heatmap is the "
    "demo's real impact, and it needs gradients - the one thing lost by optimising torch "
    "away.", BODY))
story.append(Paragraph("<b>Alternative worth knowing:</b> export LC25000CNN to ONNX and swap "
    "torch for onnxruntime (about 50 MB instead of 490 MB). That fits Render's free 512 MB "
    "at zero cost, but it removes Grad-CAM, because ONNX Runtime gives no backward pass. "
    "Take this path only if the heatmap is not essential to the pitch.", BODY))

# 4
story.append(Paragraph("4. Two things to do first, on any host", H2))
story.extend(bullets([
    "<b>Fix the deploy path to target api.py</b> - either rewrite backend/main.py to import "
    "LC25000CNN from pretrained_cnn.py, or repoint the Dockerfile entrypoint at "
    "<font face='Courier' size='8.5'>uvicorn api:app</font>. Until this is done, nothing "
    "deployed will serve correct predictions.",
    "<b>Decide how the model travels.</b> LungDisease_Classifier.pth is only 19 MB - small "
    "enough to commit to git directly (GitHub warns above 50 MB, blocks above 100 MB). The "
    "94 MB model.pth should stay out. This means reversing half of the earlier "
    "<font face='Courier' size='8.5'>git rm --cached</font>: re-track the 19 MB checkpoint, "
    "leave the 94 MB one untracked.",
]))

# 5
story.append(Paragraph("5. Open questions that change the answer", H2))
story.extend(bullets([
    "What is the real monthly ceiling - does about $5/month work, or must it be $0?",
    "Does the hosted demo need the Grad-CAM heatmap, or is predicted class plus confidence enough?",
    "Who is the audience - investors, clinicians, or a course submission? That decides whether "
    "60-second cold starts are acceptable.",
]))

story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=0.5,
                        color=colors.HexColor("#d8d5cd"), spaceAfter=6))
story.append(Paragraph(
    "Note: this report also corrects two earlier errors. backend/ does exist and DEPLOYMENT.md "
    "is structurally accurate; it was WORKSPACE_SUMMARY.md (line 24) that was wrong - the same "
    "file that wrongly claimed vault/spec.md was missing.", NOTE))

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=20*mm, rightMargin=20*mm,
                        topMargin=18*mm, bottomMargin=18*mm,
                        title="Hosting the Lung Histopathology Triage MVP",
                        author="Deployment assessment")
doc.build(story)
print("WROTE", OUT)