import json
import urllib.request

REPO = "1aurent/vit_base_patch16_224.owkin_pancancer_ft_lc25000_lung"

def get(path):
    url = f"https://huggingface.co/{REPO}/resolve/main/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "py"})
    return urllib.request.urlopen(req, timeout=30).read()

# 1) file list
req = urllib.request.Request(
    f"https://huggingface.co/api/models/{REPO}", headers={"User-Agent": "py"}
)
info = json.loads(urllib.request.urlopen(req, timeout=20).read())
print("files:", [f["rfilename"] for f in info.get("siblings", [])])

# 2) config
try:
    cfg = json.loads(get("config.json"))
    print("config:", json.dumps(cfg, indent=1)[:1200])
except Exception as e:
    print("config.json failed:", e)
