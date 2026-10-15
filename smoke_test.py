import torch, numpy as np
from PIL import Image
from pretrained_cnn import LC25000CNN, load_pretrained, CLASS_NAMES_3, CLASS_NAMES_5, LUNG_CLASS_INDICES

print("=" * 48)
print("Smoke test — Pre-trained LC25000 CNN")
print("=" * 48)

# 1. Load
model = load_pretrained('LungDisease_Classifier.pth', torch.device('cpu'))
print(f"[PASS] Model loaded ({sum(p.numel() for p in model.parameters()):,} params)")

# 2. Inference
x = torch.randn(1, 3, 192, 192)
with torch.no_grad():
    logits_5 = model(x)
    lung_logits = logits_5[:, LUNG_CLASS_INDICES]
    probs = torch.softmax(lung_logits, dim=1)
    conf, pred = probs.max(1)
print(f"[PASS] Inference: pred={CLASS_NAMES_3[pred.item()]}, conf={conf.item():.3f}")
print(f"       All probs: {dict(zip(CLASS_NAMES_3, [round(p,3) for p in probs[0].tolist()]))}")

# 3. Grad-CAM
from api import compute_gradcam, heatmap_to_base64
cam = compute_gradcam(model, x, target_layer_name="conv_layers")
print(f"[PASS] Grad-CAM: shape={cam.shape}, range=[{cam.min():.3f}, {cam.max():.3f}]")

# 4. Heatmap encoding
img = Image.fromarray(np.random.randint(0, 255, (192, 192, 3), dtype=np.uint8))
b64 = heatmap_to_base64(img, cam)
print(f"[PASS] Heatmap PNG: {len(b64)} chars, {img.size}")

# 5. API routes
from api import app
routes = [r.path for r in app.routes]
assert '/health' in routes
assert '/predict' in routes
print(f"[PASS] API routes: {routes}")

# 6. Test with a real-ish image (colored gradient)
test_img = Image.fromarray(np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8))
from torchvision import transforms
prep = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])
t = prep(test_img).unsqueeze(0)
with torch.no_grad():
    logits_5 = model(t)
    lung_logits = logits_5[:, LUNG_CLASS_INDICES]
    probs = torch.softmax(lung_logits, dim=1)
print(f"[PASS] Real image test: {CLASS_NAMES_3[probs.argmax().item()]} at {probs.max().item():.1%}")

print("\n" + "=" * 48)
print("All smoke tests passed. Model is ready to serve.")
print("Start API: .venv\\Scripts\\uvicorn api:app --host 0.0.0.0 --port 8000")