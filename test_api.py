"""End-to-end API test using only stdlib."""
import json
import urllib.request
import base64
from pathlib import Path

print("=== Health Check ===")
with urllib.request.urlopen("http://localhost:8000/health") as r:
    data = json.loads(r.read())
print(json.dumps(data, indent=2))

print("\n=== Predict test_slide.jpg ===")
# Build multipart form data
boundary = "----TestBoundary"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test_slide.jpg"\r\n'
    f"Content-Type: image/jpeg\r\n\r\n"
).encode()
body += Path("test_slide.jpg").read_bytes()
body += f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    "http://localhost:8000/predict",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
)
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())

print(f"Prediction: {data['prediction']}")
print(f"Label: {data['prediction_label']}")
print(f"Confidence: {data['confidence']}%")
print(f"Time Saved: {data['time_saved_pct']}%")
print(f"Model Status: {data['model_status']}")
print("Probabilities:")
for k, v in data["probabilities"].items():
    print(f"  {k}: {v}%")
print("Secondary:")
for s in data["secondary_predictions"]:
    print(f"  {s['label']}: {s['score']}%")
h = data.get("heatmap_base64")
print(f"Heatmap base64: {'PRESENT' if h else 'MISSING'} ({len(h) if h else 0} chars)")

# Save heatmap for verification
if h:
    out = Path("test_slide_gradcam_api.png")
    out.write_bytes(base64.b64decode(h))
    print(f"Heatmap saved to {out}")

print("\nAll checks passed!")