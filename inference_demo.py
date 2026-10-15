#!/usr/bin/env python3
"""MVP demo: LC25000CNN (18MB LungDisease_Classifier.pth) on a single image.
Usage: .venv\Scripts\python.exe inference_demo.py <image_path>
Outputs prediction + confidence + saves Grad-CAM PNG beside input."""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, numpy as np
from PIL import Image
from torchvision import transforms
from pretrained_cnn import LC25000CNN, load_pretrained, CLASS_NAMES_3, LUNG_CLASS_INDICES
from api import compute_gradcam, heatmap_to_base64

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to tissue slide image (.png/.jpg/.tif)")
    args = parser.parse_args()
    device = torch.device("cpu")
    model = load_pretrained("LungDisease_Classifier.pth", device)
    model.eval()
    img = Image.open(args.image).convert("RGB")
    prep = transforms.Compose([transforms.Resize((192, 192)), transforms.ToTensor()])
    t = prep(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits_5 = model(t)
        lung_logits = logits_5[:, LUNG_CLASS_INDICES]
        probs = torch.softmax(lung_logits, dim=1)
    conf, pred = probs.max(1)
    cls = CLASS_NAMES_3[pred.item()]
    print(f"PREDICTION: {cls} — confidence = {conf.item():.1%}")
    print(f"Probabilities: {dict(zip(CLASS_NAMES_3, [round(p,3) for p in probs[0].tolist()]))}")
    # Grad-CAM (uses api helper already verified working via smoke test)
    cam = compute_gradcam(model, t, target_layer_name="conv_layers")
    # Save overlay PNG next to source
    out_path = args.image.replace(".", "_gradcam.")
    # Simple overlay: blend CAM heatmap over original resized image
    cam_np = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    cam_rgb = (np.stack([cam_np]*3, axis=-1) * 255).astype(np.uint8)
    img_resized = img.resize((192, 192))
    blend = Image.blend(img_resized, Image.fromarray(cam_rgb), alpha=0.5)
    blend.save(out_path)
    print(f"Grad-CAM saved: {out_path}")

if __name__ == "__main__":
    main()
