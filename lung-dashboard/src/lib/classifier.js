/**
 * Client-side inference for the lung histopathology classifier.
 *
 * Runs LungDisease_Classifier.pth (exported to ONNX, 4.75M params) entirely in the
 * browser via onnxruntime-web wasm. No backend required.
 *
 * Numerics match the Python implementation: Resize(192) -> ToTensor() (range 0..1,
 * NO ImageNet normalisation), 5-class head, take the 3 lung logits and softmax them.
 */
// Import the wasm-only entry point. The default 'onnxruntime-web' entry bundles the
// jsep/webgpu backend, which pulls a 27 MB jsep wasm that we neither ship nor need.
import * as ort from 'onnxruntime-web/wasm';

const BASE = import.meta.env.BASE_URL || '/';
const MODEL_URL = `${BASE}models/lung_classifier.onnx`;
const SIZE = 192;

// Position -> class name. Verified by eval_accuracy.py across all 6 permutations:
// this mapping scores 66.7% on 120 labelled LC25000 images and is tied-best.
const CLASS_NAMES_3 = ['adenocarcinoma', 'benign', 'squamous_cell_carcinoma'];
const LUNG_INDICES = [0, 1, 2];
const DISPLAY = {
  adenocarcinoma: 'Adenocarcinoma',
  benign: 'Benign',
  squamous_cell_carcinoma: 'Squamous Cell Carcinoma',
};

// NOTE: carried over from the original API, which returned this as a documented
// stub. Not a measured figure - do not present it as one.
const TIME_SAVED_PLACEHOLDER = 62;

ort.env.wasm.wasmPaths = `${BASE}ort/`;
// Single-threaded: GitHub Pages / Vercel do not send COOP+COEP headers, so
// SharedArrayBuffer is unavailable and multi-threaded wasm would fail.
ort.env.wasm.numThreads = 1;

let sessionPromise = null;

function getSession() {
  if (!sessionPromise) {
    sessionPromise = ort.InferenceSession.create(MODEL_URL, {
      executionProviders: ['wasm'],
      graphOptimizationLevel: 'all',
    }).catch((e) => {
      sessionPromise = null;
      throw e;
    });
  }
  return sessionPromise;
}

/** 'live' once the model is loaded in this tab, otherwise 'ready'. Never triggers a download. */
export async function checkHealth() {
  return sessionPromise ? 'live' : 'ready';
}

/** Optionally warm the model (downloads ~19 MB). Not called on page load. */
export function preload() {
  return getSession();
}

/** Draw a File/Blob into a canvas at SIZE x SIZE and return normalised CHW float32. */
async function toTensor(file, occluders = null) {
  const bitmap = await createImageBitmap(file);
  const canvas = document.createElement('canvas');
  canvas.width = SIZE;
  canvas.height = SIZE;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(bitmap, 0, 0, SIZE, SIZE);
  bitmap.close?.();

  const { data } = ctx.getImageData(0, 0, SIZE, SIZE);
  const arr = new Float32Array(3 * SIZE * SIZE);
  for (let i = 0; i < SIZE * SIZE; i++) {
    const r = data[i * 4] / 255;
    const g = data[i * 4 + 1] / 255;
    const b = data[i * 4 + 2] / 255;
    arr[i] = r;
    arr[SIZE * SIZE + i] = g;
    arr[2 * SIZE * SIZE + i] = b;
  }

  // Occlusion: paint one grid cell a flat mid-grey so it carries no signal.
  if (occluders) {
    for (const { x0, y0, x1, y1 } of occluders) {
      for (let y = y0; y < y1; y++) {
        for (let x = x0; x < x1; x++) {
          const i = y * SIZE + x;
          arr[i] = 0.5;
          arr[SIZE * SIZE + i] = 0.5;
          arr[2 * SIZE * SIZE + i] = 0.5;
        }
      }
    }
  }
  return arr;
}

function softmax3(logits) {
  const v = LUNG_INDICES.map((i) => logits[i]);
  const m = Math.max(...v);
  const ex = v.map((x) => Math.exp(x - m));
  const s = ex.reduce((a, b) => a + b, 0);
  return ex.map((x) => x / s);
}

/**
 * Forward-only explainability. ONNX Runtime has no backward pass, so Grad-CAM is not
 * available in the browser; occlusion sensitivity is the standard substitute and uses
 * only forward passes. Returns a PNG data URL, or null on any failure.
 */
async function occlusionHeatmap(file, session, baseProbs, grid = 6) {
  try {
    const cell = SIZE / grid;
    const cells = [];
    for (let gy = 0; gy < grid; gy++) {
      for (let gx = 0; gx < grid; gx++) {
        cells.push({
          gx, gy,
          x0: Math.floor(gx * cell), y0: Math.floor(gy * cell),
          x1: Math.floor((gx + 1) * cell), y1: Math.floor((gy + 1) * cell),
        });
      }
    }

    const winner = baseProbs.indexOf(Math.max(...baseProbs));
    const drops = new Array(cells.length);
    for (let i = 0; i < cells.length; i++) {
      const t = await toTensor(file, [cells[i]]);
      const out = await session.run({ input: new ort.Tensor('float32', t, [1, 3, SIZE, SIZE]) });
      const p = softmax3(Array.from(out.logits.data));
      drops[i] = Math.max(0, baseProbs[winner] - p[winner]);
    }

    const maxDrop = Math.max(...drops, 1e-6);
    const sal = drops.map((d) => d / maxDrop);

    // Upscale the coarse grid and blend over the original image.
    const small = document.createElement('canvas');
    small.width = grid;
    small.height = grid;
    const sctx = small.getContext('2d');
    const img = sctx.createImageData(grid, grid);
    for (let i = 0; i < sal.length; i++) {
      const [r, g, b] = ramp(sal[i]);
      img.data[i * 4] = r;
      img.data[i * 4 + 1] = g;
      img.data[i * 4 + 2] = b;
      img.data[i * 4 + 3] = 255;
    }
    sctx.putImageData(img, 0, 0);

    const bitmap = await createImageBitmap(file);
    const out = document.createElement('canvas');
    out.width = SIZE;
    out.height = SIZE;
    const octx = out.getContext('2d');
    octx.drawImage(bitmap, 0, 0, SIZE, SIZE);
    bitmap.close?.();
    octx.globalAlpha = 0.45;
    octx.imageSmoothingEnabled = true;
    octx.drawImage(small, 0, 0, SIZE, SIZE);
    octx.globalAlpha = 1;
    return out.toDataURL('image/png');
  } catch {
    return null;
  }
}

/** Blue (low) -> amber -> red (high), matching the viewer's legend gradient. */
function ramp(t) {
  const stops = [
    [0.0, [37, 99, 235]],
    [0.5, [217, 119, 6]],
    [1.0, [220, 38, 38]],
  ];
  for (let i = 0; i < stops.length - 1; i++) {
    const [p0, c0] = stops[i];
    const [p1, c1] = stops[i + 1];
    if (t <= p1) {
      const f = (t - p0) / (p1 - p0 || 1);
      return [
        Math.round(c0[0] + (c1[0] - c0[0]) * f),
        Math.round(c0[1] + (c1[1] - c0[1]) * f),
        Math.round(c0[2] + (c1[2] - c0[2]) * f),
      ];
    }
  }
  return stops[stops.length - 1][1];
}

/**
 * Classify an uploaded image. Returns the same response shape the FastAPI /predict
 * endpoint produced, so callers did not need to change.
 */
export async function predictImage(file) {
  const session = await getSession();
  const tensor = await toTensor(file);

  const t0 = performance.now();
  const out = await session.run({
    input: new ort.Tensor('float32', tensor, [1, 3, SIZE, SIZE]),
  });
  const probs = softmax3(Array.from(out.logits.data));
  const ms = Math.round(performance.now() - t0);

  const best = probs.indexOf(Math.max(...probs));
  const prediction = CLASS_NAMES_3[best];

  const secondary = CLASS_NAMES_3
    .map((name, i) => ({ label: DISPLAY[name], score: probs[i] * 100 }))
    .filter((_, i) => i !== best);

  const probabilities = {};
  CLASS_NAMES_3.forEach((name, i) => {
    probabilities[DISPLAY[name]] = +(probs[i] * 100).toFixed(2);
  });

  const heatmap_base64 = await occlusionHeatmap(file, session, probs);

  return {
    prediction: DISPLAY[prediction],
    prediction_label: prediction === 'benign' ? 'Benign' : 'Malignant',
    confidence: +(probs[best] * 100).toFixed(1),
    time_saved_pct: TIME_SAVED_PLACEHOLDER,
    model_status: 'live',
    secondary_predictions: secondary,
    probabilities,
    heatmap_base64,
    inference_ms: ms,
    model: 'LC25000CNN · ONNX · in-browser',
  };
}