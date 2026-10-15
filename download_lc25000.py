"""Download LC25000 from the GitHub mirror (tampapath/lung_colon_image_set)."""
import sys
import time
import zipfile
from pathlib import Path
import urllib.request

URL = "https://github.com/tampapath/lung_colon_image_set/archive/refs/heads/main.zip"
OUT = Path("data/lc25000.zip")
DEST = Path("data/raw")

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUT.exists():
        print(f"Downloading {URL} ...", flush=True)
        t0 = time.time()

        def hook(bnum, bsize, total):
            mb = bnum * bsize / 1e6
            if bnum % 500 == 0:
                pct = (bnum * bsize / total * 100) if total > 0 else 0
                print(f"  {mb:.0f} MB ({pct:.1f}%)", flush=True)

        urllib.request.urlretrieve(URL, OUT, reporthook=hook)
        print(f"Downloaded {OUT.stat().st_size/1e9:.2f} GB in {time.time()-t0:.0f}s", flush=True)
    else:
        print(f"Zip already exists: {OUT} ({OUT.stat().st_size/1e9:.2f} GB)", flush=True)

    DEST.mkdir(parents=True, exist_ok=True)
    marker = DEST / ".extracted"
    if not marker.exists():
        print("Extracting (lung folders only) ...", flush=True)
        with zipfile.ZipFile(OUT) as z:
            lung = [n for n in z.namelist() if "lung_image_sets/" in n]
            print(f"  {len(lung)} lung entries to extract", flush=True)
            for i, name in enumerate(lung):
                z.extract(name, DEST)
                if i % 1000 == 0:
                    print(f"  extracted {i}/{len(lung)}", flush=True)
        marker.write_text("done")
        print("Extraction complete", flush=True)
    else:
        print("Already extracted", flush=True)

if __name__ == "__main__":
    main()
