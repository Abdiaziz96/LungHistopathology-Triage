"""
Train LC25000CNN (3-class) on LC25000 lung images.
==================================================
Classes: adenocarcinoma, benign, squamous_cell_carcinoma
Input: 192x192, no ImageNet normalization (matches api.py inference).

Usage:
    python train_lung.py --epochs 15 --per-class 1500
"""
import argparse
import random
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

from pretrained_cnn import LC25000CNN, CLASS_NAMES_3

# LC25000 folder -> our class name
FOLDER_TO_CLASS = {
    "lung_aca": "adenocarcinoma",
    "lung_n": "benign",
    "lung_scc": "squamous_cell_carcinoma",
}

IMG_SIZE = 192


class LungFolderDataset(Dataset):
    """Simple dataset from an explicit list of (path, label_idx) pairs."""

    def __init__(self, samples, transform):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        path, label = self.samples[i]
        img = Image.open(path).convert("RGB")
        return self.transform(img), label


def collect_samples(raw_root: Path, per_class: int, seed: int = 42):
    """Walk lung_image_sets, subsample per_class images per class."""
    random.seed(seed)
    class_to_idx = {name: i for i, name in enumerate(CLASS_NAMES_3)}
    lung_root = None
    for cand in raw_root.rglob("lung_image_sets"):
        if cand.is_dir():
            lung_root = cand
            break
    if lung_root is None:
        raise FileNotFoundError(f"lung_image_sets not found under {raw_root}")
    print(f"Found lung images at: {lung_root}")

    per_class_samples = {}
    for folder, class_name in FOLDER_TO_CLASS.items():
        cls_dir = lung_root / folder
        imgs = sorted([p for p in cls_dir.iterdir() if p.suffix.lower() in (".jpeg", ".jpg", ".png")])
        random.shuffle(imgs)
        chosen = imgs[:per_class]
        per_class_samples[class_name] = [(p, class_to_idx[class_name]) for p in chosen]
        print(f"  {class_name}: {len(chosen)} images (of {len(imgs)} available)")

    return per_class_samples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--per-class", type=int, default=1500, help="train+val images per class")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--val-frac", type=float, default=0.2)
    ap.add_argument("--out", default="LungDisease_Classifier.pth")
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    per_class = collect_samples(Path(args.raw_dir), args.per_class)

    # Split per class
    train_samples, val_samples = [], []
    for class_name, samples in per_class.items():
        n_val = max(1, int(len(samples) * args.val_frac))
        val_samples.extend(samples[:n_val])
        train_samples.extend(samples[n_val:])
    random.shuffle(train_samples)
    random.shuffle(val_samples)
    print(f"Train: {len(train_samples)} | Val: {len(val_samples)}")

    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
    ])

    train_loader = DataLoader(LungFolderDataset(train_samples, train_tf),
                              batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(LungFolderDataset(val_samples, val_tf),
                            batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = LC25000CNN(num_classes=3).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)

    best_val_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        # ---- train ----
        model.train()
        tr_loss, tr_correct, tr_total = 0.0, 0, 0
        for i, (x, y) in enumerate(train_loader):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            tr_loss += loss.item() * x.size(0)
            tr_correct += out.argmax(1).eq(y).sum().item()
            tr_total += y.size(0)
            if i % 25 == 0:
                print(f"  E{epoch} batch {i}/{len(train_loader)} loss={loss.item():.4f}", flush=True)
        # ---- validate ----
        model.eval()
        vl_loss, vl_correct, vl_total = 0.0, 0, 0
        per_class_correct = [0] * 3
        per_class_total = [0] * 3
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                vl_loss += criterion(out, y).item() * x.size(0)
                preds = out.argmax(1)
                vl_correct += preds.eq(y).sum().item()
                vl_total += y.size(0)
                for j in range(y.size(0)):
                    per_class_total[y[j].item()] += 1
                    if preds[j].item() == y[j].item():
                        per_class_correct[y[j].item()] += 1

        tr_acc = 100.0 * tr_correct / tr_total
        vl_acc = 100.0 * vl_correct / vl_total
        print(f"Epoch {epoch}/{args.epochs} ({time.time()-t0:.0f}s) | "
              f"train {tr_acc:.1f}% | val {vl_acc:.1f}%", flush=True)
        for i, name in enumerate(CLASS_NAMES_3):
            if per_class_total[i]:
                print(f"    {name}: {100.0*per_class_correct[i]/per_class_total[i]:.1f}% "
                      f"({per_class_correct[i]}/{per_class_total[i]})", flush=True)

        scheduler.step(vl_loss / vl_total)
        if vl_acc > best_val_acc:
            best_val_acc = vl_acc
            torch.save(model.state_dict(), args.out)
            print(f"  saved best -> {args.out} (val {vl_acc:.1f}%)", flush=True)

    print(f"\nDone. Best val accuracy: {best_val_acc:.1f}% -> {args.out}")


if __name__ == "__main__":
    main()
