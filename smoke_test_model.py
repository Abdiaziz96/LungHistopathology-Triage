"""Quick model smoke test — verify LungDisease_Classifier.pth loads and infers."""
import torch
from pretrained_cnn import LC25000CNN, CLASS_NAMES_3, LUNG_CLASS_INDICES
from torchvision import transforms
from PIL import Image
import os

device = torch.device("cpu")
model = LC25000CNN(num_classes=5)
state = torch.load("LungDisease_Classifier.pth", map_location=device, weights_only=True)
model.load_state_dict(state)
model.eval()
print(f"Model loaded: {sum(p.numel() for p in model.parameters()):,} params")
print(f"Checkpoint keys: {len(state)} layers")

# Random input test
preprocess = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])
dummy = torch.rand(3, 192, 192)
batch = dummy.unsqueeze(0)
with torch.no_grad():
    logits = model(batch)
    lung_logits = logits[:, LUNG_CLASS_INDICES]
    probs = torch.softmax(lung_logits, dim=1)
    conf, pred = probs.max(dim=1)

print("Random input test:")
print(f"  All 5 logits: {[round(v, 3) for v in logits[0].tolist()]}")
print(f"  Predicted: {CLASS_NAMES_3[pred.item()]} ({conf.item()*100:.1f}%)")
for i, name in enumerate(CLASS_NAMES_3):
    print(f"    {name}: {probs[0,i].item()*100:.1f}%")

# Test with test_slide.jpg
if os.path.exists("test_slide.jpg"):
    img = Image.open("test_slide.jpg").convert("RGB")
    tensor = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor)
        lung_logits = logits[:, LUNG_CLASS_INDICES]
        probs = torch.softmax(lung_logits, dim=1)
        conf, pred = probs.max(dim=1)
    print(f"\nTest slide (test_slide.jpg):")
    print(f"  Predicted: {CLASS_NAMES_3[pred.item()]} ({conf.item()*100:.1f}%)")
    for i, name in enumerate(CLASS_NAMES_3):
        print(f"    {name}: {probs[0,i].item()*100:.1f}%")
else:
    print("\ntest_slide.jpg not found — skip")

# Test Grad-CAM
print("\nTesting Grad-CAM hook...")
from api import compute_gradcam
try:
    cam = compute_gradcam(model, batch, target_layer_name="conv_layers")
    print(f"  Grad-CAM shape: {cam.shape}, range: [{cam.min():.3f}, {cam.max():.3f}]")
    print("  Grad-CAM: OK")
except Exception as e:
    print(f"  Grad-CAM FAILED: {e}")

print("\n✓ Smoke test complete")