"""Resumable download of the LC25000 lung ViT from HuggingFace."""
import time
from pathlib import Path
import urllib.request

URL = "https://huggingface.co/1aurent/vit_base_patch16_224.owkin_pancancer_ft_lc25000_lung/resolve/main/model.safetensors"
OUT = Path("vit_lc25000_lung.safetensors")
EXPECTED = 343_000_000  # approx; will re-HEAD to confirm


def head_size():
    req = urllib.request.Request(URL, method="HEAD", headers={"User-Agent": "py"})
    r = urllib.request.urlopen(req, timeout=30)
    cl = r.headers.get("Content-Length")
    return int(cl) if cl else 0


def main():
    total = head_size() or EXPECTED
    print(f"Target size: {total/1e6:.0f} MB", flush=True)

    attempt = 0
    while True:
        have = OUT.stat().st_size if OUT.exists() else 0
        if have >= total:
            print(f"COMPLETE: {have/1e6:.0f} MB", flush=True)
            break
        attempt += 1
        headers = {"User-Agent": "py"}
        if have > 0:
            headers["Range"] = f"bytes={have}-"
        print(f"[attempt {attempt}] resuming from {have/1e6:.1f} MB", flush=True)
        try:
            req = urllib.request.Request(URL, headers=headers)
            r = urllib.request.urlopen(req, timeout=60)
            # If we asked for a range but server sent the full file (200), restart cleanly
            if have > 0 and r.status != 206:
                print("  server ignored Range, restarting from 0", flush=True)
                have = 0
                mode = "wb"
            else:
                mode = "ab" if have > 0 else "wb"
            t0 = time.time()
            n_since_log = 0
            with open(OUT, mode) as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    have += len(chunk)
                    n_since_log += len(chunk)
                    if n_since_log >= (1 << 24):  # log every ~16MB
                        rate = (have - (OUT.stat().st_size - have))  # placeholder
                        print(f"  {have/1e6:.0f}/{total/1e6:.0f} MB "
                              f"({100*have/total:.0f}%) {time.time()-t0:.0f}s", flush=True)
                        n_since_log = 0
            # stream ended; loop re-checks size
        except Exception as e:
            print(f"  [error: {type(e).__name__}] retrying in 3s", flush=True)
            time.sleep(3)


if __name__ == "__main__":
    main()
