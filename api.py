"""
Lung Histopathology Triage — FastAPI Backend
=============================================
Serves predictions and Grad-CAM heatmaps for the NHS dashboard.

Endpoints:
    POST /predict     — classify a WSI/tile, return prediction + heatmap (base64)
    GET  /health      — model status check

Start:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations

import base64
import io
import traceback
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pretrained_cnn import LC25000CNN, CLASS_NAMES_3, CLASS_NAMES_5, LUNG_CLASS_INDICES

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CLASS_NAMES: list[str] = CLASS_NAMES_3  # ["adenocarcinoma", "benign", "squamous_cell_carcinoma"]
IMG_SIZE: int = 192  # matches the pre-trained CNN input size

# ---------------------------------------------------------------------------
# Globals (lazy‑loaded by lifespan)
# ---------------------------------------------------------------------------
device: torch.device
model: LC25000CNN

# Search for the trained checkpoint
_CHECKPOINT_CANDIDATES: list[Path] = [
    Path("LungDisease_Classifier.pth"),
    Path("model.pth"),
    Path("checkpoints/best_model.pth"),
    Path("checkpoints/best_model.pyt"),
]
CHECKPOINT_PATH: Path = next((p for p in _CHECKPOINT_CANDIDATES if p.exists()), Path("LungDisease_Classifier.pth"))

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Lung Histopathology Triage API",
    version="4.1.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # tighten in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------------------------
_preprocess = transforms.Compose(
    [
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
    ]
)

# Color‑map for Grad‑CAM → RGB overlay
_JET_COLORMAP = np.array(
    [
        [0, 0, 0],        # dark blue
        [0, 0, 255],
        [0, 255, 255],
        [0, 255, 0],
        [255, 255, 0],
        [255, 0, 0],       # red
    ],
    dtype=np.uint8,
)


def _apply_colormap(mask: np.ndarray, colormap: np.ndarray) -> np.ndarray:
    """
    Map floating‑point mask (0‑1) to a smooth RGB heatmap via linear
    interpolation over a small colour palette.
    """
    mask = np.clip(mask, 0, 1)
    idx = mask * (len(colormap) - 1)
    lo = np.floor(idx).astype(int)
    hi = np.ceil(idx).astype(int)
    hi = np.clip(hi, 0, len(colormap) - 1)
    frac = idx - lo

    rgb = np.zeros((*mask.shape, 3), dtype=np.float32)
    for c in range(3):
        rgb[..., c] = (1 - frac) * colormap[lo, c] + frac * colormap[hi, c]

    return rgb.astype(np.uint8)


# ---------------------------------------------------------------------------
# Grad‑CAM implementation (standalone – no external dependency needed)
# ---------------------------------------------------------------------------
class _GradCAMHook:
    """Capture forward activations and backward gradients from one layer."""

    def __init__(self, module: torch.nn.Module):
        self.activations: Optional[torch.Tensor] = None
        self.gradients: Optional[torch.Tensor] = None
        self._fwd_handle = module.register_forward_hook(self._forward_hook)
        self._bwd_handle = module.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, _mod, _inp, out: torch.Tensor):
        self.activations = out.detach()

    def _backward_hook(self, _mod, _g_inp, g_out):
        self.gradients = g_out[0].detach()

    def remove(self):
        self._fwd_handle.remove()
        self._bwd_handle.remove()


def compute_gradcam(
    model: torch.nn.Module,
    image_tensor: torch.Tensor,
    target_layer_name: str = "conv_layers",
) -> np.ndarray:
    """
    Generate a Grad‑CAM heatmap for the predicted class.

    Returns
    -------
    np.ndarray   shape (H, W)  float32 in [0, 1]
    """
    # Locate the target layer
    target_module: Optional[torch.nn.Module] = None
    for name, mod in model.named_modules():
        # ResNet stores the final block group under `backbone.layer4`
        if name.endswith(target_layer_name) or name == target_layer_name:
            target_module = mod
            break
    if target_module is None:
        raise ValueError(f"Target layer '{target_layer_name}' not found in model.")

    hook = _GradCAMHook(target_module)
    model.zero_grad()

    # Forward (+ requires_grad so autograd tracks through activations)
    image_tensor = image_tensor.detach().requires_grad_(True)
    logits = model(image_tensor)
    pred_class = logits.argmax(dim=1).item()

    # Backward on the predicted logit
    model.zero_grad()
    logits[0, pred_class].backward()

    # Compute weights via global-average-pooling of gradients
    gradients = hook.gradients                       # (1, C, H', W')
    activations = hook.activations                   # (1, C, H', W')
    weights = gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)

    # Weighted combination + ReLU
    cam = (weights * activations).sum(dim=1).squeeze(0)  # (H', W')
    cam = torch.relu(cam)

    # Normalise to [0, 1]
    cam -= cam.min()
    denom = cam.max()
    if denom > 0:
        cam /= denom

    # Resize to input spatial size
    cam = cam.unsqueeze(0).unsqueeze(0)              # (1, 1, H', W')
    cam = F.interpolate(
        cam,
        size=(IMG_SIZE, IMG_SIZE),
        mode="bilinear",
        align_corners=False,
    )
    cam = cam.squeeze().cpu().numpy()

    hook.remove()
    return cam.astype(np.float32)


def heatmap_to_base64(
    original_pil: Image.Image,
    cam: np.ndarray,
    alpha: float = 0.45,
) -> str:
    """
    Overlay Grad‑CAM heatmap onto the original image and return a
    base64‑encoded PNG string.
    """
    original_rgb = np.array(original_pil.convert("RGB"), dtype=np.uint8)

    # Resize CAM to match original image dimensions
    cam_pil = Image.fromarray((cam * 255).astype(np.uint8))
    cam_pil = cam_pil.resize(original_pil.size, Image.BILINEAR)
    cam_resized = np.array(cam_pil, dtype=np.float32) / 255.0

    # Colour mapping
    heatmap_rgb = _apply_colormap(cam_resized, _JET_COLORMAP)

    # Alpha blend
    blended = (heatmap_rgb * alpha + original_rgb * (1 - alpha)).astype(np.uint8)

    # Encode
    buf = io.BytesIO()
    Image.fromarray(blended).save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


# ---------------------------------------------------------------------------
# Lifespan — load model at startup
# ---------------------------------------------------------------------------
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global device, model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = LC25000CNN(num_classes=5)

    if CHECKPOINT_PATH.exists():
        state = torch.load(CHECKPOINT_PATH, map_location=device, weights_only=True)
        # Handle both raw state_dict and wrapped checkpoint formats
        if isinstance(state, dict) and "model_state_dict" in state:
            model.load_state_dict(state["model_state_dict"])
        else:
            model.load_state_dict(state)
        print(f"Loaded checkpoint: {CHECKPOINT_PATH}")
    else:
        print("⚠ No checkpoint found — using untrained weights for demo.")
        print(f"  Place a checkpoint at {CHECKPOINT_PATH.resolve()}")

    model.to(device)
    model.eval()
    yield


app.router.lifespan_context = lifespan


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    """Return model readiness status."""
    return {
        "status": "live" if CHECKPOINT_PATH.exists() else "ready",
        "device": str(device),
        "model_version": "4.1.0",
        "num_classes": len(CLASS_NAMES),
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accept a histopathology image (.png / .jpg / .tiff),
    run inference, and return the prediction together with a
    base64‑encoded Grad‑CAM heatmap overlay.
    """
    # Validate file extension
    allowed_ext = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".svs"}
    suffix = Path(file.filename or "unknown.jpg").suffix.lower()
    if suffix not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{suffix}'. Allowed: {', '.join(sorted(allowed_ext))}",
        )

    # Read bytes
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded file.")

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")

    # Open image
    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot decode image. Ensure it is a valid PNG/JPEG/TIFF.")

    # Preprocess for the model (192×192, no ImageNet normalization)
    image_tensor = _preprocess(pil_image).unsqueeze(0).to(device)  # (1, 3, 192, 192)

    # ── Inference ──
    with torch.no_grad():
        logits = model(image_tensor)         # (1, 5)
        # Extract only the 3 lung classes (ignore colon_aca, colon_n)
        lung_logits = logits[:, LUNG_CLASS_INDICES]  # (1, 3)
        probs = torch.softmax(lung_logits, dim=1)
        confidence, pred_idx = probs.max(dim=1)

    pred_class = CLASS_NAMES[pred_idx.item()]
    pred_confidence = confidence.item()

    all_probs: dict[str, float] = {
        cls: probs[0, i].item() for i, cls in enumerate(CLASS_NAMES)
    }

    # ── Grad‑CAM heatmap ──
    try:
        cam = compute_gradcam(model, image_tensor, target_layer_name="conv_layers")
        heatmap_b64 = heatmap_to_base64(pil_image, cam, alpha=0.45)
    except Exception:
        traceback.print_exc()
        heatmap_b64 = None

    # Determine prediction label
    if pred_class == "benign":
        label = "Benign"
    elif pred_class in ("adenocarcinoma", "squamous_cell_carcinoma"):
        label = "Malignant"
    else:
        label = pred_class

    # Estimate time saved (stub — replace with real calibration)
    time_saved_pct = round(100 - (pred_confidence * 60), 1) if pred_confidence > 0.5 else 35.0
    time_saved_pct = max(25.0, min(85.0, time_saved_pct))

    # Build secondary predictions (non‑max classes, sorted desc)
    sorted_probs = sorted(all_probs.items(), key=lambda kv: kv[1], reverse=True)
    secondary = [
        {"label": cls.replace("_", " ").title(), "score": round(p * 100, 1)}
        for cls, p in sorted_probs[1:]
    ]

    return {
        "prediction": pred_class.replace("_", " ").title(),
        "prediction_label": label,
        "confidence": round(pred_confidence * 100, 1),
        "time_saved_pct": time_saved_pct,
        "model_status": "live" if CHECKPOINT_PATH.exists() else "ready",
        "probabilities": {k: round(v * 100, 1) for k, v in all_probs.items()},
        "secondary_predictions": secondary,
        "heatmap_base64": heatmap_b64,
    }


# ---------------------------------------------------------------------------
# Direct run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)