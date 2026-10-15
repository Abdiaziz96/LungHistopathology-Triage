"""Predict on repo sample images to sanity-check model accuracy."""
import sys
sys.path.insert(0, ".")
from pretrained_cnn import LC25000CNN, CLASS_NAMES_3, LUNG_CLASS_INDICES
from torchvision import transforms
from PIL import Image
import torch
from pathlib import Path

device = torch.device("cpu")
model = LC25000CNN(num_classes=5)
state = torch.load("LungDisease_Classifier.pth", map_location=device, weights_only=True)
model.load_state_dict(state)
model.eval()

preprocess = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])

samples = ["data/processed/val/images/image1.png", "test_slide.jpg", "template_preview.jpg"]
for p in samples:
    if not Path(p).exists():
        print(f"[skip] {p} (not found)")
        continue
    img = Image.open(p).convert("RGB")
    t = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(t)
        probs = torch.softmax(logits[:, LUNG_CLASS_INDICES], dim=1)
        conf, pred = probs.max(dim=1)
    top = [(CLASS_NAMES_3[i], round(probs[0, i].item() * 100, 1)) for i in range(3)]
    top.sort(key=lambda x: -x[1])
    print(f"{p}: {CLASS_NAMES_3[pred.item()]} ({conf.item()*100:.1f}%) -> {top}")