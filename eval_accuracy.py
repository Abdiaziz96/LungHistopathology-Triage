"""Accuracy evaluation of LC25000CNN on labelled LC25000 samples.
Tries all 6 permutations of the 3 lung output indices to find the true label mapping.
"""
import glob
import os
from itertools import permutations

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from pretrained_cnn import load_pretrained, CLASS_NAMES_3, LUNG_CLASS_INDICES

ROOT = os.path.join("data", "lc25000_eval")
FOLDER_TO_CLASS = {
    "lung_aca": "adenocarcinoma",
    "lung_n": "benign",
    "lung_scc": "squamous_cell_carcinoma",
}
# logit positions 0,1,2 correspond to these indices in the 5-class output
POSITIONS = list(range(len(LUNG_CLASS_INDICES)))

model = load_pretrained("LungDisease_Classifier.pth", torch.device("cpu"))
model.eval()
prep = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])

records = []  # (true_class, argmax_position)
per_class_counts = {}

for folder, true_class in FOLDER_TO_CLASS.items():
    files = sorted(glob.glob(os.path.join(ROOT, folder, "*")))
    counts = [0, 0, 0]
    for p in files:
        try:
            img = Image.open(p).convert("RGB")
        except Exception:
            continue
        with torch.no_grad():
            logits = model(prep(img).unsqueeze(0))[:, LUNG_CLASS_INDICES]
        pos = int(logits.argmax(1).item())
        records.append((true_class, pos))
        counts[pos] += 1
    per_class_counts[folder] = (counts, len(files))

print("=" * 66)
print(f"LC25000CNN accuracy on {len(records)} labelled LC25000 images")
print("=" * 66)
print("\nRaw argmax position distribution (position 0 / 1 / 2 in the 3-lung output):")
for folder, (counts, n) in per_class_counts.items():
    print(f"  {folder:<10} true={FOLDER_TO_CLASS[folder]:<24} n={n:<4} "
          f"-> pos0={counts[0]:<3} pos1={counts[1]:<3} pos2={counts[2]:<3}")

print("\nAccuracy under each label permutation (position -> class name):")
best = None
for perm in permutations(CLASS_NAMES_3):
    mapping = dict(zip(POSITIONS, perm))
    hits = sum(1 for true_class, pos in records if mapping[pos] == true_class)
    acc = hits / len(records)
    label = " | ".join(f"pos{i}={perm[i]}" for i in POSITIONS)
    star = ""
    if best is None or acc > best[0]:
        best = (acc, perm)
    print(f"  {acc:6.1%}   {label}")

acc, perm = best
mapping = dict(zip(POSITIONS, perm))
print("\n" + "-" * 66)
print(f"BEST MAPPING: {perm}  ->  accuracy {acc:.1%}")

print("\nConfusion (best mapping): rows=true, cols=predicted")
labels = list(CLASS_NAMES_3)
w = max(len(x) for x in labels) + 2
print(" " * w + "".join(f"{c[:12]:>14}" for c in labels))
for t in labels:
    row = [0] * 3
    for true_class, pos in records:
        if true_class == t:
            row[labels.index(mapping[pos])] += 1
    print(f"{t:<{w}}" + "".join(f"{v:>14}" for v in row))

print("\nlibrary default mapping (currently used by api.py): "
      f"{ {i: CLASS_NAMES_3[i] for i in POSITIONS} }")
hits = sum(1 for true_class, pos in records if CLASS_NAMES_3[pos] == true_class)
print(f"library default accuracy: {hits / len(records):.1%}")
print("=" * 66)