"""Determine TRUE 5-class order by inspecting raw softmax on known samples."""
import torch
from pretrained_cnn import LC25000CNN, CLASS_NAMES_5
from torchvision import transforms
from PIL import Image
from pathlib import Path

device = torch.device("cpu")
model = LC25000CNN(num_classes=5)
state = torch.load("LungDisease_Classifier.pth", map_location=device, weights_only=True)
model.load_state_dict(state)
model.eval()

# Inspect the raw 5-class output WITHOUT the [0,1,2] masking
preprocess = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])

# CLASS_NAMES_5 currently hardcodes a GUESSED order. We'll print raw indices.
print("Model head: 5 output classes. Final fc bias (per-class bias):")
fc_bias = model.fc_layers[6].bias
for i in range(5):
    print(f"  index {i}: bias = {fc_bias[i].item():+.3f}")

samples = ["data/processed/val/images/image1.png", "test_slide.jpg", "template_preview.jpg"]
for p in samples:
    if not Path(p).exists():
        print(f"[skip] {p}")
        continue
    img = Image.open(p).convert("RGB")
    t = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(t)
        probs5 = torch.softmax(logits, dim=1)  # softmax over ALL 5
    vals = [(i, round(probs5[0, i].item() * 100, 1)) for i in range(5)]
    vals.sort(key=lambda x: -x[1])
    print(f"\n{p}")
    print(f"  Raw 5-class softmax (sorted): {vals}")
    print(f"  ARGMAX INDEX = {vals[0][0]}")
    print(f"  (index 0..4 correspond to whatever order the trainer used)")