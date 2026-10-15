"""Export LC25000CNN (LungDisease_Classifier.pth) to ONNX + verify parity.

Produces lung-dashboard/public/models/lung_classifier.onnx so the Vite dev server
serves it at /models/lung_classifier.onnx for in-browser inference.
"""
import os
import numpy as np
import torch
from torchvision import transforms
from PIL import Image

from pretrained_cnn import LC25000CNN, load_pretrained, CLASS_NAMES_3, LUNG_CLASS_INDICES

CKPT = "LungDisease_Classifier.pth"
OUT_DIR = os.path.join("lung-dashboard", "public", "models")
ONNX_PATH = os.path.join(OUT_DIR, "lung_classifier.onnx")

os.makedirs(OUT_DIR, exist_ok=True)
device = torch.device("cpu")

print("=" * 60)
print("ONNX export - LC25000CNN")
print("=" * 60)

model = load_pretrained(CKPT, device)
model.eval()
print(f"[1] loaded checkpoint  params={sum(p.numel() for p in model.parameters()):,}")

dummy = torch.randn(1, 3, 192, 192)

# dynamo=False keeps us on the TorchScript exporter, avoiding an onnxscript dependency
exported = False
try:
    torch.onnx.export(
        model, dummy, ONNX_PATH,
        input_names=["input"], output_names=["logits"],
        opset_version=17, dynamo=False,
    )
    exported = True
    print("[2] exported with legacy exporter (dynamo=False)")
except Exception as e:
    print(f"[2] legacy exporter failed: {type(e).__name__}: {str(e)[:200]}")

if not exported:
    raise SystemExit("export failed")

size_mb = os.path.getsize(ONNX_PATH) / 1e6
print(f"    -> {ONNX_PATH}  ({size_mb:.2f} MB)")

# ---- parity: torch vs onnxruntime on identical input ------------------------
import onnxruntime as ort
sess = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
print(f"[3] onnxruntime loaded  providers={sess.get_providers()}")

rng = np.random.default_rng(0)
x = rng.standard_normal((1, 3, 192, 192)).astype(np.float32)

with torch.no_grad():
    t_out = model(torch.from_numpy(x)).numpy()
o_out = sess.run(None, {"input": x})[0]

max_diff = float(np.abs(t_out - o_out).max())
print(f"[4] max abs diff (torch vs onnx) = {max_diff:.3e}")
print(f"    parity {'PASS' if max_diff < 1e-4 else 'FAIL'}")

# ---- identical prediction on real slides ------------------------------------
import glob
prep = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])

paths = sorted(glob.glob(os.path.join("data", "processed", "val", "images", "*.png")) +
               glob.glob(os.path.join("data", "processed", "val", "images", "*.jpg")))
if not paths:
    paths = [p for p in ("test_slide.jpg",) if os.path.exists(p)]

print("[5] real slides - torch vs onnx")
agree = 0
for p in paths:
    try:
        img = Image.open(p).convert("RGB")
    except Exception as e:
        print(f"      skip {p}: {e}")
        continue
    t_in = prep(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(t_in)[:, LUNG_CLASS_INDICES]
        probs_t = torch.softmax(logits, dim=1)[0].numpy()
    raw = sess.run(None, {"input": t_in.numpy()})[0][:, LUNG_CLASS_INDICES]
    raw = np.exp(raw - raw.max(1, keepdims=True))
    probs_o = (raw / raw.sum(1, keepdims=True))[0]

    a_t, a_o = int(probs_t.argmax()), int(probs_o.argmax())
    agree += (a_t == a_o)
    name = os.path.basename(p)
    print(f"      {name:<18} torch={CLASS_NAMES_3[a_t]:<26} "
          f"{probs_t[a_t]:.3f}   onnx={CLASS_NAMES_3[a_o]:<26} {probs_o[a_o]:.3f}   "
          f"{'MATCH' if a_t == a_o else 'MISMATCH'}")
print(f"    agreement: {agree}/{len(paths)}")

print("=" * 60)
print("DONE")