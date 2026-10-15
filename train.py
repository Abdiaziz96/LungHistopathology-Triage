"""
Training Script — Lung Histopathology Triage
=============================================
Fine-tunes a pretrained ResNet50 on the 3-class LC25000 lung dataset.

Usage:
    # Phase 1: freeze backbone, train only the classifier head
    python train.py --freeze-backbone --epochs 10 --lr 1e-3

    # Phase 2: unfreeze and fine-tune at a lower learning rate
    python train.py --epochs 20 --lr 1e-4

    # Resume a checkpoint
    python train.py --resume checkpoints/best_model.pth
"""
import argparse
import os
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
import yaml
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau

from dataset import create_dataloaders
from model import LungTriageModel


PROJECT_ROOT = Path(__file__).resolve().parent
CKPT_DIR = PROJECT_ROOT / "checkpoints"


def _load_config(path: str) -> dict:
    """Load YAML config and flatten top-level keys into a flat dict."""
    with open(path) as f:
        raw = yaml.safe_load(f)
    flat: dict = {}
    for section in ("model", "data", "training"):
        if section in raw:
            for k, v in raw[section].items():
                flat[k] = v
    return flat


def _apply_config_defaults(parser: argparse.ArgumentParser, config: dict):
    """Set argparse defaults from a config dict (only for matching flags)."""
    for action in parser._actions:
        key = action.dest
        if key in config and action.default == parser.get_default(key):
            action.default = config[key]


def train_one_epoch(
    model, loader, criterion, optimizer, device, epoch: int, total_epochs: int
) -> tuple[float, float]:
    """Single training epoch.  Returns (avg_loss, accuracy)."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        if batch_idx % 20 == 0:
            print(f"  Epoch {epoch}/{total_epochs} | Batch {batch_idx}/{len(loader)} | "
                  f"Loss: {loss.item():.4f}")

    avg_loss = running_loss / total
    accuracy = 100.0 * correct / total
    return avg_loss, accuracy


@torch.no_grad()
def validate(model, loader, criterion, device) -> tuple[float, float]:
    """Validation loop.  Returns (avg_loss, accuracy)."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    avg_loss = running_loss / total
    accuracy = 100.0 * correct / total
    return avg_loss, accuracy


def save_checkpoint(model, optimizer, epoch, metrics, path: Path, is_best: bool = False):
    """Save a training checkpoint."""
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "metrics": metrics,
    }, path)
    if is_best:
        print(f"  ✓ Best model saved → {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune ResNet50 for lung histopathology triage."
    )
    # Config file (loads defaults, CLI args override)
    parser.add_argument("--config", default="config.yaml",
                        help="Path to YAML config file for defaults (CLI args override).")
    # Data
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--num-workers", type=int, default=0)
    # Model
    parser.add_argument("--num-classes", type=int, default=3)
    parser.add_argument("--freeze-backbone", action="store_true",
                        help="Freeze ResNet50 backbone, train only the classifier head.")
    parser.add_argument("--dropout", type=float, default=0.3)
    # Training
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--scheduler", choices=["cosine", "plateau"], default="plateau")
    # Resume
    parser.add_argument("--resume", default=None, help="Path to checkpoint to resume from.")
    args = parser.parse_args()

    # Load config.yaml defaults (CLI args take precedence if user passes them)
    config_path = Path(args.config)
    if config_path.exists():
        _apply_config_defaults(parser, _load_config(str(config_path)))
        # Re-parse so config values become defaults and CLI args override
        args = parser.parse_args()
        print(f"Loaded config defaults from {config_path}")

    # ------------------------------------------------------------------
    # Device
    # ------------------------------------------------------------------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    train_loader, val_loader, class_names = create_dataloaders(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        img_size=args.img_size,
        num_workers=args.num_workers,
    )

    # ------------------------------------------------------------------
    # Model, loss, optimiser
    # ------------------------------------------------------------------
    model = LungTriageModel(
        num_classes=args.num_classes,
        freeze_backbone=args.freeze_backbone,
        dropout=args.dropout,
    )
    model.to(device)
    print(f"Trainable params: {model.get_trainable_params():,} / {model.get_total_params():,}")

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    if args.scheduler == "cosine":
        scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)
    else:
        scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=3, verbose=True)

    start_epoch = 0
    best_val_acc = 0.0

    # ------------------------------------------------------------------
    # Resume
    # ------------------------------------------------------------------
    if args.resume:
        ckpt = torch.load(args.resume, map_location=device, weights_only=True)
        model.load_state_dict(ckpt["model_state_dict"])
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        start_epoch = ckpt["epoch"] + 1
        best_val_acc = ckpt["metrics"].get("val_acc", 0.0)
        print(f"Resumed from {args.resume} at epoch {start_epoch}")

    # ------------------------------------------------------------------
    # Training loop
    # ------------------------------------------------------------------
    for epoch in range(start_epoch + 1, start_epoch + args.epochs + 1):
        print(f"\n{'='*50}\nEpoch {epoch}/{start_epoch + args.epochs}\n{'='*50}")

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch,
            start_epoch + args.epochs,
        )
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val   Loss: {val_loss:.4f} | Val   Acc: {val_acc:.2f}%")

        # Step scheduler
        if args.scheduler == "plateau":
            scheduler.step(val_loss)
        else:
            scheduler.step()

        # Save best checkpoint
        metrics = {"val_loss": val_loss, "val_acc": val_acc, "train_acc": train_acc}
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_checkpoint(
                model, optimizer, epoch, metrics,
                CKPT_DIR / "best_model.pth", is_best=True,
            )

        # Save latest checkpoint
        save_checkpoint(model, optimizer, epoch, metrics, CKPT_DIR / "last_checkpoint.pth")

        print(f"  Best val acc so far: {best_val_acc:.2f}%")

    print(f"\n{'='*50}")
    print(f"Training complete. Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Checkpoints saved in: {CKPT_DIR}")


if __name__ == "__main__":
    main()