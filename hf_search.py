import json
import urllib.request

req = urllib.request.Request(
    "https://huggingface.co/api/models?search=lc25000&limit=30",
    headers={"User-Agent": "py"},
)
d = json.loads(urllib.request.urlopen(req, timeout=20).read())
d.sort(key=lambda m: -m.get("downloads", 0))
for m in d:
    print(m["id"], "| downloads:", m.get("downloads", 0), "| likes:", m.get("likes", 0))
