"""Determine true class order using labeled ground-truth images."""
import torch
from pretrained_cnn import LC25000CNN
from torchvision import transforms
from PIL import Image
from pathlib import Path

device = torch.device("cpu")
model = LC25000CNN(num_classes=5)
state = torch.load("LungDisease_Classifier.pth", map_location=device, weights_only=True)
model.load_state_dict(state)
model.eval()

preprocess = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])

# Ground truth labels
samples = {
    "data/processed/val/images/image1.png": "adenocarcinoma",
    "data/processed/val/images/benign.png": "benign",
    "data/processed/val/images/squamous.png": "squamous_cell_carcinoma",
}

print("=== Determining TRUE 5-class order ===\n")
for path, true_label in samples.items():
    if not Path(path).exists():
        print(f"[SKIP] {path} not found")
        continue
    
    img = Image.open(path).convert("RGB")
    t = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(t)
        probs5 = torch.softmax(logits, dim=1)
    
    argmax_idx = probs5.argmax().item()
    argmax_prob = probs5[0, argmax_idx].item()
    
    print(f"{Path(path).name} (true: {true_label})")
    print(f"  argmax index = {argmax_idx} (conf: {argmax_prob*100:.1f}%)")
    print(f"  raw probs: {[(i, round(probs5[0,i].item()*100, 1)) for i in range(5)]}")
    print()

print("=== Mapping result ===")
print("Index 0 = ?")
print("Index 1 = adenocarcinoma (confirmed)")
print("Index 2 = ?")
print("Index 3 = ?")
print("Index 4 = ?")
