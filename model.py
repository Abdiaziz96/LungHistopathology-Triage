"""
ResNet50-based Model for Lung Histopathology Triage
====================================================
3-class classifier: adenocarcinoma, squamous_cell_carcinoma, benign.

Uses a pretrained ResNet50 backbone (ImageNet) with a replaced final
fully-connected layer for 3-way classification.

Usage:
    from model import LungTriageModel
    model = LungTriageModel(num_classes=3, freeze_backbone=False)
"""
import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights


class LungTriageModel(nn.Module):
    """
    ResNet50 backbone → 3-class lung histopathology classifier.

    Args:
        num_classes:    number of output classes (default 3).
        freeze_backbone: if True, freeze all layers except the final fc.
        dropout:        dropout probability before the classifier head.
    """

    def __init__(
        self,
        num_classes: int = 3,
        freeze_backbone: bool = False,
        dropout: float = 0.3,
    ):
        super().__init__()
        # Load pretrained weights (IMAGENET1K_V2 is the current best default)
        self.backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)

        in_features = self.backbone.fc.in_features

        # Replace the classification head
        self.backbone.fc = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes),
        )

        if freeze_backbone:
            self._freeze_backbone()

        self.num_classes = num_classes

    def _freeze_backbone(self):
        """Freeze all parameters except the final fc layer."""
        for name, param in self.backbone.named_parameters():
            if not name.startswith("fc."):
                param.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def get_trainable_params(self) -> int:
        """Return the count of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def get_total_params(self) -> int:
        """Return the total parameter count."""
        return sum(p.numel() for p in self.parameters())


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Test with frozen backbone (quick first-pass)
    model = LungTriageModel(num_classes=3, freeze_backbone=True)
    model.to(device)
    print(f"Trainable params (frozen backbone): {model.get_trainable_params():,}")
    print(f"Total params:                     {model.get_total_params():,}")

    # Dummy batch
    x = torch.randn(4, 3, 224, 224).to(device)
    with torch.no_grad():
        logits = model(x)
    print(f"Input:  {x.shape}  →  Output: {logits.shape}")
    assert logits.shape == (4, 3), f"Unexpected output shape: {logits.shape}"
    print("✓ Forward pass OK")

    # Test with full fine-tuning
    model2 = LungTriageModel(num_classes=3, freeze_backbone=False)
    print(f"Trainable params (full fine-tune): {model2.get_trainable_params():,}")
    print("✓ All checks passed.")