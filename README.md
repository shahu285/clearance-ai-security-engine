# 🔐 ClearanceAI — Autonomous RAG Security Engine

> A full-stack Document Ingestion & Semantic Search pipeline that autonomously classifies uploaded files via Generative AI, assigns dynamic security clearances, and enforces zero-trust boundary isolation inside a high-performance vector database.

🌐 **Live Production Demo** → [clearance-ai-security-engine.onrender.com](https://clearance-ai-security-engine.onrender.com)

---

## 📌 The Problem It Solves

Standard RAG systems and document vaults have a critical security flaw — when a user queries the vector database, the system blindly pulls matching document fragments based purely on **semantic similarity**, completely ignoring company hierarchy or user access rights.

This means a junior employee could semantically query for "salary information" and receive fragments from a confidential HR payroll sheet — a real, exploitable data leakage .

**ClearanceAI solves this.**

---

## 💡 How It Works

```
User Uploads Document (PDF / TXT)
          │
          ▼
┌─────────────────────────────────────────────────┐
│           Generative AI Classification           │
│                                                 │
│  Gemini 1.5 Flash reads document content and    │
│  autonomously generates custom security roles   │
│  e.g. ["Finance", "HRManager", "Principal"]     │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│           Embedding + Vector Storage             │
│                                                 │
│  FastEmbed converts document to dense vectors   │
│  Stored in Qdrant DB with security metadata     │
│  stamps attached to every chunk                 │
└────────────────────┬────────────────────────────┘
                     │
          User Submits Query
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         Zero-Trust Runtime Filter                │
│                                                 │
│  System checks user's active profile clearance  │
│  Metadata filter applied before retrieval       │
│  Unauthorized matches → blocked in real-time    │
│  Authorized matches → returned to user          │
└─────────────────────────────────────────────────┘
```

---

## 🛡️ Security Model

ClearanceAI implements a **zero-trust metadata filter** at the vector retrieval layer. Here's what that means in practice:

| Scenario | Result |
|---|---|
| `HRManager` queries HR payroll document | ✅ Access granted |
| `Engineer` queries same HR payroll document | ❌ Breach blocked |
| `Principal` queries any document | ✅ Full access |
| `Finance` queries engineering specs | ❌ Breach blocked |

Security roles are **not hardcoded**. Gemini reads each document and invents the exact roles needed to protect that specific asset. A legal brief gets `["LegalCounsel", "Executive"]`. A salary sheet gets `["HRManager", "CFO"]`. No human configuration needed.

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **FastAPI** | Asynchronous Python backend (ASGI) |
| **Qdrant DB** | High-performance vector index engine (in-memory) |
| **FastEmbed** | Local CPU-optimized ONNX embedding engine |
| **Google Gemini 1.5 Flash** | Generative AI security classification |
| **PyPDF2** | PDF binary stream parser |
| **HTML5 + TailwindCSS** | Frontend dashboard interface |

---

## 📁 Project Structure

```
clearance-ai-security-engine/
│
├── main.py                # FastAPI app — all routes, ingestion pipeline,
│                          # embedding logic, query engine, security filter
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

### Inside `main.py`

The entire backend lives in a single file covering:

- `POST /upload` — document ingestion endpoint
- `POST /query` — semantic search with clearance filter
- Gemini classification call — autonomous role generation
- FastEmbed vectorization — local ONNX embedding
- Qdrant upsert — storing vectors with metadata stamps
- Runtime metadata filter — zero-trust enforcement at query time

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- A free [Google Gemini API key](https://aistudio.google.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/shahu285/clearance-ai-security-engine.git
cd clearance-ai-security-engine

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your-gemini-key-here
```

### Run the App

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## 🔬 Key Engineering Decisions

**Why Qdrant in volatile memory?**
For this use case, spinning up Qdrant as an in-memory client eliminates infrastructure overhead while keeping vector operations blazing fast. No Docker, no managed cluster needed for a production demo.

**Why FastEmbed over OpenAI embeddings?**
FastEmbed runs entirely on CPU via ONNX Runtime — zero API calls, zero cost, zero latency spikes. For a security-critical pipeline, local embeddings also mean document content never leaves the machine during vectorization.

**Why Gemini for classification and not a rules engine?**
A rules-based classifier would need manual configuration for every new document type. Gemini reads the content and *reasons* about what kind of user should access it — a completely autonomous, zero-configuration approach that scales to any document type without human intervention.

---

## 💡 Key Concepts Demonstrated

- **Retrieval-Augmented Generation (RAG)** pipeline architecture
- **Vector database** operations — upsert, metadata filtering, semantic search
- **Zero-trust security** enforcement at the retrieval layer
- **Generative AI classification** — autonomous role invention via Gemini
- **Local CPU embeddings** with FastEmbed + ONNX Runtime
- **Async REST API** design with FastAPI
- **Production deployment** on Render

---

## 📈 Future Improvements

- [ ] Support for complex document types — Word (`.docx`), Excel (`.xlsx`), PowerPoint (`.pptx`)
- [ ] Persistent Qdrant storage — disk-based vector index for production use
- [ ] Multi-user session management with JWT authentication
- [ ] Role hierarchy — `Principal` auto-inherits all sub-roles
- [ ] Audit log — track every query attempt, granted or blocked
- [ ] Batch document ingestion — upload entire folder at once

---

## 👤 Author

**Shahu Ugale** | AI Engineer

[LinkedIn](https://www.linkedin.com/in/shahu-ugale/) · [GitHub](https://github.com/shahu285)

---

## 📄 License

MIT License — free to use, modify, and distribute.
