# ClearanceAI — Autonomous RAG Security Engine

ClearanceAI is a full-stack Document Ingestion & Semantic Search pipeline. The application autonomously classifies uploaded files via generative AI to assign dynamic security clearances and enforces zero-trust boundary isolation inside a high-performance vector database.

### 🌐 Live Production Website
👉 **https://clearance-ai-security-engine.onrender.com**

---

## 💡 What It's About & The Problem It Solves

### The Core Problem
When organizations build standard Retrieval-Augmented Generation (RAG) systems or document vaults, they often face a severe data leakage problem. If a user queries the vector database, the system blindly pulls matching document fragments based purely on semantic similarity—completely ignoring company hierarchy or user access rights. This risks exposing restricted data (like private financial audits or HR payroll sheets) to unauthorized users.

### The Solution
ClearanceAI bridges the gap between semantic AI search and information security. When a user drops a physical document (`.pdf` or `.txt`) into the pipeline:
1. An offloaded Generative AI layer instantly reads the content and **autonomously invents custom security roles** (e.g., `Finance`, `HRManager`, `Principal`) needed to lock that asset down.
2. The document is embedded locally and stored with these exact metadata security stamps.
3. When users query the database, the system applies strict runtime metadata filters based on their active profile signature. If a lower-clearance profile searches for restricted concepts, the engine blocks the adversarial breach attempt in real-time, enforcing zero-trust data confinement.

---

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI (Asynchronous Python ASGI matrix)
* **Vector Index Engine:** Qdrant DB (Instantiated in volatile memory client layout)
* **Quantized Text Embedder:** FastEmbed (ONNX Runtime engine for local CPU-optimized processing)
* **Generative Security Analytics:** Google Gemini 1.5 Flash (Offloaded cloud classification endpoint)
* **Document Stream Parser:** PyPDF2 (Standalone pure-Python binary file extractor)
* **Dashboard Interface:** HTML5 + TailwindCSS (Dynamic web-form telemetry console)
