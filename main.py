# main.py - PulmoScan AI v4 — FastAPI with Grad-CAM + Analytics
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tensorflow as tf
import numpy as np
from PIL import Image
import io, logging, time, json, os, base64
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# ── Logging ──────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ── App ──────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PulmoScan AI — TB Detector API",
    description="TB detection with Grad-CAM explainability and analytics",
    version="4.0"
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Analytics store (JSON file) ──────────────────────────────────────────────────
ANALYTICS_FILE = "analytics.json"

def load_analytics():
    if os.path.exists(ANALYTICS_FILE):
        with open(ANALYTICS_FILE) as f:
            return json.load(f)
    return {"total": 0, "normal": 0, "tb": 0, "history": []}

def save_analytics(data):
    with open(ANALYTICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Load model ───────────────────────────────────────────────────────────────────
logger.info("Loading model...")
try:
    model = tf.keras.models.load_model("my_model.keras", compile=False)
    logger.info(f"Model loaded! Input shape: {model.input_shape}")
except Exception as e:
    logger.error(f"Model load failed: {e}")
    model = None

# ── Preprocessing ────────────────────────────────────────────────────────────────
def preprocess_image(image: Image.Image) -> np.ndarray:
    img = image.resize((300, 300))
    arr = np.array(img)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    elif arr.shape[-1] == 4:
        arr = arr[:, :, :3]
    arr = np.expand_dims(arr, 0)
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    return preprocess_input(arr.astype(np.float32))

# ── Grad-CAM ─────────────────────────────────────────────────────────────────────
def generate_gradcam(image: Image.Image) -> str:
    """Generate Grad-CAM heatmap, return as base64 PNG string."""
    try:
        # Find the last conv layer automatically
        last_conv = None
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                last_conv = layer.name
                break
        if last_conv is None:
            return None

        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[model.get_layer(last_conv).output, model.output]
        )

        img_array = preprocess_image(image)

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            # For binary sigmoid output
            loss = predictions[:, 0]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap).numpy()
        heatmap = np.maximum(heatmap, 0)
        if heatmap.max() > 0:
            heatmap /= heatmap.max()

        # Resize heatmap to image size
        orig = np.array(image.resize((300, 300)))
        if orig.ndim == 2:
            orig = np.stack([orig] * 3, axis=-1)

        heatmap_resized = np.uint8(255 * heatmap)
        heatmap_img = Image.fromarray(heatmap_resized).resize((300, 300))
        colormap = cm.get_cmap("jet")
        heatmap_colored = colormap(np.array(heatmap_img) / 255.0)[:, :, :3]
        heatmap_colored = np.uint8(heatmap_colored * 255)

        # Overlay: 55% original + 45% heatmap
        superimposed = (0.55 * orig + 0.45 * heatmap_colored).astype(np.uint8)

        # Build side-by-side figure
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        fig.patch.set_facecolor("#020810")

        titles = ["Original X-Ray", "Grad-CAM Heatmap", "Overlay (Attention)"]
        images_to_show = [orig, heatmap_colored, superimposed]
        cmaps = [None, "jet", None]

        for ax, img_data, title, cmap in zip(axes, images_to_show, titles, cmaps):
            ax.imshow(img_data, cmap=cmap)
            ax.set_title(title, color="#00c8ff", fontsize=9, fontfamily="monospace", pad=6)
            ax.axis("off")
            for spine in ax.spines.values():
                spine.set_edgecolor("#0a2540")

        plt.tight_layout(pad=1.5)

        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor="#020810", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        return b64

    except Exception as e:
        logger.error(f"Grad-CAM error: {e}")
        return None

# ── Routes ────────────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"app": "PulmoScan AI", "version": "4.0", "status": "running"}

@app.get("/health")
def health():
    if model is None:
        raise HTTPException(503, "Model not loaded")
    return {"status": "healthy", "model": "loaded"}

@app.get("/analytics")
def get_analytics():
    return load_analytics()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(503, "Model not available")
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, f"Expected image, got {file.content_type}")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(422, "Could not decode image")

    try:
        start      = time.perf_counter()
        processed  = preprocess_image(image)
        raw_score  = float(model.predict(processed, verbose=0)[0][0])
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(500, "Inference failed")

    result     = "TUBERCULOSIS" if raw_score >= 0.5 else "NORMAL"
    confidence = round(raw_score if result == "TUBERCULOSIS" else 1.0 - raw_score, 4)

    # ── Grad-CAM ──
    gradcam_b64 = generate_gradcam(image)

    # ── Save analytics ──
    analytics = load_analytics()
    analytics["total"] += 1
    analytics["tb" if result == "TUBERCULOSIS" else "normal"] += 1
    analytics["history"].append({
        "timestamp": datetime.now().isoformat(),
        "result":    result,
        "confidence": confidence,
        "filename":  file.filename,
        "inference_ms": elapsed_ms
    })
    # Keep last 200 records
    analytics["history"] = analytics["history"][-200:]
    save_analytics(analytics)

    logger.info(f"{result} | {confidence:.2%} | {elapsed_ms}ms")

    return {
        "result":       result,
        "confidence":   confidence,
        "raw_score":    round(raw_score, 4),
        "inference_ms": elapsed_ms,
        "message":      f"{result} detected with {confidence:.2%} confidence",
        "note":         "AI screening only. Consult a licensed physician.",
        "gradcam":      gradcam_b64
    }
