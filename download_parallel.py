"""Parallel (multi-range) resumable download of the ViT weights."""
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

URL = "https://huggingface.co/1aurent/vit_base_patch16_224.owkin_pancancer_ft_lc25000_lung/resolve/main/model.safetensors"
OUT = Path("vit_lc25000_lung.safetensors")
PARTS_DIR = Path("dl_parts")
N = 8


def head_size():
    req = urllib.request.Request(URL, method="HEAD", headers={"User-Agent": "py"})
    return int(urllib.request.urlopen(req, timeout=30).headers.get("Content-Length", 0))


def fetch_range(start, end, dest):
    """Download bytes [start, end] to dest with retries."""
    if dest.exists() and dest.stat().st_size == (end - start + 1):
        return True
    for attempt in range(12):
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": "py", "Range": f"bytes={start}-{end}"})
            with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            if dest.stat().st_size == (end - start + 1):
                return True
        except Exception:
            time.sleep(2)
    return False


def main():
    total = head_size()
    print(f"Total: {total/1e6:.0f} MB", flush=True)
    PARTS_DIR.mkdir(exist_ok=True)

    chunk = total // N
    ranges = []
    for i in range(N):
        s = i * chunk
        e = ((i + 1) * chunk - 1) if i < N - 1 else (total - 1)
        ranges.append((i, s, e))

    t0 = time.time()
    results = {}
    with ThreadPoolExecutor(max_workers=N) as ex:
        futs = {ex.submit(fetch_range, s, e, PARTS_DIR / f"part_{i}.tmp"): i for i, s, e in ranges}
        for fut in as_completed(futs):
            i = futs[fut]
            results[i] = fut.result()
            done = sum(1 for v in results.values() if v)
            print(f"  part {i} ok={results[i]}  ({done}/{N})", flush=True)

    if not all(results.values()):
        print("FAILED: some parts incomplete — rerun to resume.", flush=True)
        return

    # Concatenate parts (fresh file)
    print("Concatenating ...", flush=True)
    with open(OUT, "wb") as out:
        for i, _, _ in ranges:
            with open(PARTS_DIR / f"part_{i}.tmp", "rb") as p:
                while True:
                    b = p.read(1 << 22)
                    if not b:
                        break
                    out.write(b)

    final = OUT.stat().st_size
    print(f"Done: {final/1e6:.0f} MB in {time.time()-t0:.0f}s  (expected {total/1e6:.0f})", flush=True)

    # Verify safetensors integrity
    ok = False
    try:
        from safetensors import safe_open
        with safe_open(str(OUT), framework="pt") as f:
            n = len(f.keys())
        ok = True
        print(f"VERIFY: safetensors valid, {n} tensors", flush=True)
    except Exception as e:
        print(f"VERIFY FAILED: {e}", flush=True)

    if final == total and ok:
        for f in PARTS_DIR.glob("part_*.tmp"):
            os.remove(f)
        PARTS_DIR.rmdir()
        print("OK — complete and verified", flush=True)
    else:
        print("INCOMPLETE — rerun to resume parts", flush=True)


if __name__ == "__main__":
    main()
