# 🫁 PulmoScan AI — Tuberculosis Detection from Chest X-Rays

## 📌 Overview

PulmoScan AI is an end-to-end deep learning application that screens chest X-ray images for **Tuberculosis (TB)** in near real-time. A fine-tuned **MobileNetV2** model runs behind a **FastAPI** REST backend; a styled **Streamlit** dashboard provides clinicians and researchers with an accessible interface including confidence scores and actionable precautions on positive findings.

> ⚕️ **Medical Disclaimer** — This tool is intended for research and screening assistance only. It is not a certified medical device and does not replace professional clinical diagnosis.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🔬 AI Inference | MobileNetV2 (transfer-learned) – 300×300 px input |
| ⚡ Low Latency | ~30 ms inference on CPU via TF SavedModel |
| 🎨 Healthcare UI | Dark clinical theme, confidence bar, animated feedback |
| ⚠️ TB Precautions | Actionable isolation/treatment guidance on positive results |
| 🐳 Docker Ready | Single `docker-compose up` launches both services |
| 📄 REST API | OpenAPI docs at `/docs`, JSON prediction responses |
| 🧪 Modular Design | Backend & frontend decoupled — swap UI or model independently |

---

## 🗂 Project Structure

```
pulmoscan-ai/
├── main.py              # FastAPI backend — /predict endpoint
├── streamlit_app.py     # Streamlit frontend — healthcare UI
├── my_model.keras       # Trained MobileNetV2 model (add manually)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Single-image build (API + UI)
├── docker-compose.yml   # Recommended: separate service containers
├── start.sh             # Entrypoint for single-container mode
└── README.md
```

---

## 🚀 Quick Start

### Option A — Docker Compose (Recommended)

```bash
# 1. Clone
git clone https://github.com/AMANDyer/pulmoscan-ai.git
cd pulmoscan-ai

# 2. Add your trained model
cp /path/to/my_model.keras .

# 3. Launch
docker-compose up --build

# API  → http://localhost:8000/docs
# UI   → http://localhost:8501
```

### Option B — Local Python

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start FastAPI backend
uvicorn main:app --reload --port 8000

# 3. In a second terminal, start Streamlit
streamlit run streamlit_app.py
```

---

## 🔌 API Reference

### `GET /`
Health check — returns welcome message.

### `POST /predict`
Upload a chest X-ray and receive a prediction.

**Request**
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@chest_xray.jpg"
```

**Response**
```json
{
  "result": "TUBERCULOSIS",
  "confidence": 0.9241,
  "message": "TUBERCULOSIS with 92.41% confidence",
  "note": "This is an AI prediction. Always consult a doctor."
}
```

| Field | Type | Description |
|---|---|---|
| `result` | `"NORMAL"` \| `"TUBERCULOSIS"` | Binary classification |
| `confidence` | `float [0–1]` | Model confidence for the predicted class |
| `message` | `string` | Human-readable summary |
| `note` | `string` | Medical disclaimer |

---

## 🧠 Model Details

| Property | Value |
|---|---|
| Base Architecture | MobileNetV2 (ImageNet pretrained) |
| Input Size | 300 × 300 × 3 (RGB) |
| Output | Sigmoid — single probability score |
| Threshold | 0.5 (≥ 0.5 → TB, < 0.5 → Normal) |
| Preprocessing | `tf.keras.applications.mobilenet_v2.preprocess_input` |
| Format | `.keras` (TF 2.12+) |

---

## 🐳 Docker Notes

The `docker-compose.yml` spins up two containers:

| Container | Port | Role |
|---|---|---|
| `pulmoscan-api` | 8000 | FastAPI inference server |
| `pulmoscan-ui` | 8501 | Streamlit dashboard |

The UI container communicates with the API using Docker's internal network (`http://api:8000`). The model file is mounted as a read-only volume — no rebuild needed when updating weights.

---

## 📁 Dataset (Reference)

This model was trained on publicly available TB chest X-ray datasets:

- [Montgomery County Chest X-ray Set](https://openi.nlm.nih.gov/)
- [Shenzhen Hospital Chest X-ray Set](https://openi.nlm.nih.gov/)
- [Kaggle TB Chest X-ray Dataset](https://www.kaggle.com/datasets/tawsifurrahman/tuberculosis-tb-chest-xray-dataset)

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

Made with ❤️ for global TB elimination -10 million new TB cases diagnosed annually worldwide
