"""
Inference & Evaluation Utilities for Lung Histopathology Triage
================================================================
Load a trained model checkpoint and run predictions on single images
or whole directories.

Usage:
    python inference.py checkpoints/best_model.pth image.jpg
    python inference.py checkpoints/best_model.pth data/processed/val/adenocarcinoma/
"""
import argparse
import sys
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

from model import LungTriageModel

CLASS_NAMES = ["adenocarcinoma", "squamous_cell_carcinoma", "benign"]
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def load_model(ckpt_path: str, device: torch.device) -> LungTriageModel:
    model = LungTriageModel(num_classes=3, freeze_backbone=False)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()
    print(f"Loaded checkpoint from {ckpt_path} (epoch {ckpt['epoch']})")
    return model


def predict_image(model: LungTriageModel, image_path: str, device: torch.device) -> dict:
    """Run inference on a single image. Returns dict with class and confidence."""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    img = Image.open(image_path).convert("RGB")
    tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)
        conf, pred = probs.max(1)

    return {
        "path": image_path,
        "class": CLASS_NAMES[pred.item()],
        "confidence": conf.item(),
        "probabilities": {
            cls: probs[0, i].item() for i, cls in enumerate(CLASS_NAMES)
        },
    }


def predict_directory(model, dir_path: str, device, ext: tuple = (".jpg", ".jpeg", ".png")):
    """Run inference on all images in a directory."""
    results = []
    files = sorted(Path(dir_path).glob("*"))
    image_files = [f for f in files if f.suffix.lower() in ext]

    print(f"Found {len(image_files)} images in {dir_path}")
    for img_path in image_files:
        result = predict_image(model, str(img_path), device)
        results.append(result)
        print(f"  {img_path.name:40s} → {result['class']:30s} "
              f"(conf: {result['confidence']:.3f})")
    return results


def main():
    parser = argparse.ArgumentParser(description="Inference for lung histopathology triage.")
    parser.add_argument("checkpoint", help="Path to model checkpoint (.pth).")
    parser.add_argument("target", help="Image file or directory to run inference on.")
    parser.add_argument("--device", default=None, help="cuda / cpu (auto-detect if omitted).")
    args = parser.parse_args()

    device = torch.device(args.device if args.device else ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Device: {device}")

    model = load_model(args.checkpoint, device)

    target_path = Path(args.target)
    if target_path.is_file():
        result = predict_image(model, str(target_path), device)
        print(f"\nPrediction: {result['class']} (confidence: {result['confidence']:.3f})")
        print("Probabilities:")
        for cls, prob in result["probabilities"].items():
            print(f"  {cls}: {prob:.4f}")
    elif target_path.is_dir():
        predict_directory(model, str(target_path), device)
    else:
        print(f"Error: {args.target} is not a valid file or directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()