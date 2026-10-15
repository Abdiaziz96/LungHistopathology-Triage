# Image source options (workspace has none)

## 1. Use the synthetic test image (already present)
- File: `test_slide.jpg` (400x400 random)
- Verified: `inference_demo.py test_slide.jpg` returned `squamous_cell_carcinoma 65.0%` with Grad-CAM overlay

## 2. Pull real images
- Run `data_download.py` (Kaggle LC25000; per WORKSPACE_SUMMARY.md line 14, 28)
- Or external: search "LC25000 dataset github" or "lung adenocarcinoma histology jpg example"
- Place under `data/processed/val/adenocarcinoma/`, etc.

## 3. Search terms (no fetch support in this session)
- "LC25000 dataset github"
- "lung adenocarcinoma histology jpg example"
- "histopathology slide image public domain"

## 4. Image used
- `images/image1.png` (4.5MB histopathology, real tissue, user-provided)
- Run: `.venv\Scripts\python.exe inference_demo.py images\image1.png`
- Result: `PREDICTION: benign — 91.5%` (real output, not random)
- Grad-CAM overlay saved to `images\image1_gradcam.png`
- Note: searched image tagged "lung adenocarcinoma" but model predicts benign 91.5%. Either the search returned non-adenocarcinoma tissue or the 18MB model mispredicts on this input.

## 5. Torrent dataset (Academic Torrents — user-provided URL)
- `data/torrents/LC25000_dataset.torrent` (1,118 bytes, saved 26 Aug 2026)
- Source URL: `https://academictorrents.com/details/7a638ed187a6180fd6e464b3666a6ea0499af4af`
- To extract full 25,000 image archive: open `.torrent` in a BitTorrent client (qBittorrent, etc.)
- Once extracted: `data_download.py` can process `lung_colon_image_set/` into `data/processed/`

## 5. Test set
- 2 images verified end-to-end:
  - `test_slide.jpg` (synthetic, 400x400 random) → squamous_cell_carcinoma 65.0%
  - `images/image1.png` (real, 4.5MB) → benign 91.5%
- No additional images available (external fetch failed from harness; `data_download.py` not run)

## 6. Note on prediction discrepancy
- 2 images verified end-to-end:
  - `test_slide.jpg` (synthetic, 400x400 random) → squamous_cell_carcinoma 65.0%
  - `images/image1.png` (real, 4.5MB) → benign 91.5%
- No additional images available (external fetch failed from harness; `data_download.py` not run)

## Constraint
- `danger-full-access` + `approval: never` apply, but cross-site downloads require network/agent capability not available in this session
- Pipeline ready: directory created at `data/processed/val/adenocarcinoma/`
