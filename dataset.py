"""
PyTorch Dataset & DataLoader for Lung Histopathology Triage
============================================================
3-class classification: adenocarcinoma, squamous_cell_carcinoma, benign.

Directory layout expected under data/processed/:
  train/
    adenocarcinoma/
    squamous_cell_carcinoma/
    benign/
  val/
    adenocarcinoma/
    squamous_cell_carcinoma/
    benign/

Usage:
    from dataset import create_dataloaders
    train_loader, val_loader, classes = create_dataloaders(
        data_dir="data/processed", batch_size=32, img_size=224
    )
"""
from pathlib import Path

import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms


CLASS_NAMES = ["adenocarcinoma", "squamous_cell_carcinoma", "benign"]

# ImageNet mean & std — standard for ResNet50 transfer learning
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def _make_transform(img_size: int, augment: bool) -> transforms.Compose:
    """
    Build a torchvision transform chain.

    Args:
        img_size: target square crop size (e.g. 224 for ResNet).
        augment:  if True, include random flips & colour jitter.
    """
    ops = [
        transforms.Resize((img_size, img_size)),
    ]
    if augment:
        ops.extend([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.05),
        ])
    ops.extend([
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    return transforms.Compose(ops)


def create_dataloaders(
    data_dir: str = "data/processed",
    batch_size: int = 32,
    img_size: int = 224,
    num_workers: int = 0,
    val_split: float = 0.0,
) -> tuple:
    """
    Create training and validation DataLoaders.

    Args:
        data_dir:    root processed data directory (contains train/ & val/).
        batch_size:  mini-batch size.
        img_size:    resize dimension (square).
        num_workers: DataLoader workers (0 for Windows safety).
        val_split:   float 0-1 — if > 0, split the *training* set into
                     train/val (ignoring data_dir/val).  Useful when the
                     download script already produced a val/ folder
                     (leave this at 0 to use that folder directly).

    Returns:
        (train_loader, val_loader, class_names)
    """
    data_path = Path(data_dir)

    train_dir = data_path / "train"
    val_dir = data_path / "val"

    train_transform = _make_transform(img_size, augment=True)
    val_transform = _make_transform(img_size, augment=False)

    if val_split > 0:
        # Use the whole 'train/' folder and split it
        full_dataset = datasets.ImageFolder(str(train_dir), transform=train_transform)
        n_total = len(full_dataset)
        n_val = int(n_total * val_split)
        n_train = n_total - n_val
        train_ds, val_ds = random_split(full_dataset, [n_train, n_val])
        # For validation we want the non-augmented transform
        val_ds.dataset.transform = val_transform  # type: ignore[union-attr]
    else:
        train_ds = datasets.ImageFolder(str(train_dir), transform=train_transform)
        if val_dir.exists():
            val_ds = datasets.ImageFolder(str(val_dir), transform=val_transform)
        else:
            raise FileNotFoundError(
                f"Validation directory not found at {val_dir}. "
                f"Either run data_download.py first or set val_split > 0."
            )

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    classes = CLASS_NAMES
    print(f"Train samples: {len(train_ds)} | Val samples: {len(val_ds)}")
    print(f"Classes: {classes}")
    return train_loader, val_loader, classes


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    data_root = sys.argv[1] if len(sys.argv) > 1 else "data/processed"
    try:
        tr, vl, cls_names = create_dataloaders(data_dir=data_root, batch_size=8)
        images, labels = next(iter(tr))
        print(f"Batch shape: {images.shape}, Labels: {labels}")
        print(f"Label names: {[cls_names[l] for l in labels.tolist()]}")
    except FileNotFoundError:
        print(f"No processed data yet at '{data_root}' — run data_download.py first.")