"""
LC25000 Pre-trained CNN — matching the Ghost-141 architecture.
================================================================
Architecture: 3 conv blocks (16→32→64) + 3 fc layers (128→64→5)
Trained on all 5 LC25000 classes. We map the 5 outputs to our
3 lung classes: lung_aca→0, lung_scc→1, lung_n→2, ignore colon classes.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


# 5-class index mapping (from the original repo's class order)
# lung_aca=0, lung_n=1, lung_scc=2, colon_aca=3, colon_n=4
LUNG_CLASS_INDICES = [0, 1, 2]  # we take only lung classes, ignoring colon
CLASS_NAMES_5 = [
    "lung_aca",       # 0 → adenocarcinoma
    "lung_n",         # 1 → benign
    "lung_scc",       # 2 → squamous_cell_carcinoma
    "colon_aca",      # 3 (ignored)
    "colon_n",        # 4 (ignored)
]
# Map to our 3-class names
CLASS_NAMES_3 = ["adenocarcinoma", "benign", "squamous_cell_carcinoma"]


class LC25000CNN(nn.Module):
    """
    Matches the Ghost-141 architecture exactly:
        3 conv layers (kernel=3, stride=1) with ReLU + MaxPool2d(2,2) after each
        flatten → fc 128 → fc 64 → fc 5
    Input: 3×192×192 (matching the original repo's preprocessing)
    """
    def __init__(self, num_classes: int = 5):
        super().__init__()

        self.conv_layers = nn.Sequential(
            # Block 1: 3 → 16
            nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            # Block 2: 16 → 32
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            # Block 3: 32 → 64
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )

        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(p=0.0),              # index 1 (not in checkpoint)
            nn.Linear(36864, 128),  # 192×192 input → 24×24 after 3× MaxPool → 24*24*64 = 36864
            nn.ReLU(inplace=True),          # index 3
            nn.Linear(128, 64),             # index 4 in checkpoint
            nn.ReLU(inplace=True),          # index 5
            nn.Linear(64, num_classes),     # index 6 in checkpoint
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

    def get_target_layer(self, name: str = "conv_layers"):
        """Return the target layer/block for Grad-CAM."""
        return self.conv_layers


def load_pretrained(checkpoint_path: str, device: torch.device) -> LC25000CNN:
    """Load the Ghost-141 checkpoint and return model + metadata."""
    model = LC25000CNN(num_classes=5)
    state = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model