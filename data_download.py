"""
LC25000 Lung Histopathology Data Downloader
===========================================
Downloads the LC25000 dataset from Kaggle using opendatasets.
Filtered to 3 classes: adenocarcinoma, squamous cell carcinoma, benign.

Dataset: "andrewmvd/lung-and-colon-cancer-histopathological-images"
The LC25000 dataset contains 25,000 color images (768×768 px) across 5 classes.
We extract the lung-specific classes:
  - lung_aca   (lung adenocarcinoma)
  - lung_scc   (lung squamous cell carcinoma)
  - lung_n     (lung benign tissue)

Requires: opendatasets, kaggle API credentials (kaggle.json)
"""
import os
import shutil
import argparse
from pathlib import Path

import opendatasets as od


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

KAGGLE_DATASET = "andrewmvd/lung-and-colon-cancer-histopathological-images"

# The Kaggle dataset extracts into a subfolder with this name
EXTRACTED_SUBDIR = "lung_colon_image_set"

# Map LC25000 subfolder names → our canonical class names
CLASS_MAP = {
    "lung_aca": "adenocarcinoma",
    "lung_scc": "squamous_cell_carcinoma",
    "lung_n": "benign",
}


def download_dataset() -> Path:
    """Download and extract the LC25000 dataset into data/raw/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {KAGGLE_DATASET} into {RAW_DIR} ...")
    od.download(KAGGLE_DATASET, data_dir=str(RAW_DIR))
    extracted_path = RAW_DIR / EXTRACTED_SUBDIR
    if not extracted_path.exists():
        raise RuntimeError(f"Expected extracted folder not found: {extracted_path}")
    return extracted_path


def organise_by_class(extracted_path: Path) -> dict:
    """
    Walk the extracted directory tree and organise images into
    {class_name: [Path, ...]} for our three target classes.
    """
    class_images: dict[str, list[Path]] = {v: [] for v in CLASS_MAP.values()}

    # Each subfolder inside extracted_path is a class
    # e.g. lung_colon_image_set/lung_image_sets/lung_aca/
    for subfolder in sorted(extracted_path.rglob("*")):
        if subfolder.is_dir():
            folder_name = subfolder.name.lower()
            if folder_name in CLASS_MAP:
                canonical = CLASS_MAP[folder_name]
                found = list(subfolder.glob("*.jpeg")) + list(subfolder.glob("*.jpg"))
                class_images[canonical].extend(found)

    for cls, paths in class_images.items():
        print(f"  {cls}: {len(paths)} images")

    return class_images


def restructure_for_torchvision(
    class_images: dict[str, list[Path]], split: tuple[float, float] = (0.8, 0.2)
):
    """
    Copy images into data/processed/{train,val}/{class_name}/ structure
    expected by torchvision.datasets.ImageFolder.

    Args:
        class_images: dict mapping class name → list of Path objects.
        split: (train_ratio, val_ratio). Must sum ≤ 1.0.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train_dir = PROCESSED_DIR / "train"
    val_dir = PROCESSED_DIR / "val"

    for cls_name in class_images:
        (train_dir / cls_name).mkdir(parents=True, exist_ok=True)
        (val_dir / cls_name).mkdir(parents=True, exist_ok=True)

    train_ratio, val_ratio = split
    for cls_name, paths in class_images.items():
        n = len(paths)
        n_train = int(n * train_ratio)
        train_paths = paths[:n_train]
        val_paths = paths[n_train:]

        for src in train_paths:
            dst = train_dir / cls_name / src.name
            if not dst.exists():
                shutil.copy2(src, dst)

        for src in val_paths:
            dst = val_dir / cls_name / src.name
            if not dst.exists():
                shutil.copy2(src, dst)

        print(f"  {cls_name} → train: {len(train_paths)}, val: {len(val_paths)}")

    print(f"\nProcessed dataset ready at: {PROCESSED_DIR}")


def main():
    parser = argparse.ArgumentParser(
        description="Download and prepare the LC25000 lung histopathology dataset."
    )
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Skip Kaggle download if data/raw already exists."
    )
    parser.add_argument(
        "--train-ratio", type=float, default=0.8,
        help="Fraction of images to use for training (default: 0.8)."
    )
    args = parser.parse_args()

    if not args.skip_download or not (RAW_DIR / EXTRACTED_SUBDIR).exists():
        extracted = download_dataset()
    else:
        extracted = RAW_DIR / EXTRACTED_SUBDIR
        print(f"Skipping download — using existing data at {extracted}")

    class_images = organise_by_class(extracted)
    restructure_for_torchvision(class_images, split=(args.train_ratio, 1.0 - args.train_ratio))

    print("\n✓ Data preparation complete.")


if __name__ == "__main__":
    main()