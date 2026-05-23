from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from qdrant_client import QdrantClient
from qdrant_client import models
from contextlib import asynccontextmanager
import requests
import io
import os
import pypdf

COLLECTION_NAME = "secure_vault"
MODEL_NAME = "BAAI/bge-small-en-v1.5"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Shared Global Objects
qdrant_db = None
SYSTEM_LOGS = []
doc_id_counter = 0
ALL_DISCOVERED_ROLES = set(["Public"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    global qdrant_db
    print("--- WEB PORT DISCOVERED: ARMED CORE APPLICATION LAUNCH ---")
    qdrant_db = QdrantClient(":memory:")
    qdrant_db.set_model(MODEL_NAME)
    qdrant_db.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qdrant_db.get_fastembed_vector_params(),
    )
    print("--- CHANNELS INGESTED NATIVELY: VAULT ONLINE ---")
    yield

app = FastAPI(title="ClearanceAI Security Engine", lifespan=lifespan)

# --- THE AUTONOMOUS AI ROLE GENERATOR ---
def fetch_ai_generated_roles(text: str) -> list:
    if not GEMINI_API_KEY:
        text_lower = text.lower()
        if any(w in text_lower for w in ["mark", "score", "grade", "exam"]):
            return ["Teacher", "Principal"]
        if any(w in text_lower for w in ["revenue", "profit", "salary", "bonus"]):
            return ["Finance", "Executive"]
        return ["Executive"]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
    Analyze the following text fragment and identify what specific professional, corporate, or institutional roles should have access permission to read it.
    Create specific, clean, single-word PascalCase role names (e.g., Student, DepartmentHead, SeniorAuditor, HRManager, Public).
    
    Return ONLY a comma-separated list of the roles you generate. Do not write markdown, prose, or explanations.
    
    Text to analyze:
    "{text[:4000]}"
    """
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        ai_output = response.json()['candidates'][0]['content']['parts'][0]['text']
        return [r.strip() for r in ai_output.split(",") if r.strip()]
    except Exception as e:
        print(f"API Error: {e}")
        return ["Executive"]


@app.get("/", response_class=HTMLResponse)
def render_dashboard(user_role: str = "Public", query: str = ""):
    global ALL_DISCOVERED_ROLES, qdrant_db
    search_results = []
    security_status = "READY"
    system_response = "System workspace idling. Submit a semantic query to test real-time security boundaries."
    answer_text = "No runtime query executed."
    border_color = "border-zinc-800 bg-zinc-900/20"
    badge_color = "bg-zinc-800 text-zinc-400 border-zinc-700"

    if qdrant_db is None:
        return "<h3>Vector Vault is initializing model layers. Please refresh in 10 seconds...</h3>"

    if query:
        rbac_metadata_filter = models.Filter(
            must=[models.FieldCondition(key="allowed_roles", match=models.MatchValue(value=user_role))]
        )
        
        search_results = qdrant_db.query(
            collection_name=COLLECTION_NAME, query_text=query, query_filter=rbac_metadata_filter, limit=1
        )

        if search_results and search_results[0].score > 0.60:
            hit = search_results[0]
            security_status = "ENFORCED"
            system_response = f"Success! Authorized context retrieved. (Confidence Score: {round(hit.score * 100, 1)}%)"
            answer_text = hit.document
            border_color = "border-emerald-500 bg-emerald-950/20"
            badge_color = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
        else:
            unfiltered_check = qdrant_db.query(collection_name=COLLECTION_NAME, query_text=query, limit=1)
            highest_raw_score = unfiltered_check[0].score if unfiltered_check else 0.0
            
            breach_attempt = any(
                item.score > 0.60 and user_role not in item.metadata["allowed_roles"] 
                for item in unfiltered_check
            )
            
            if breach_attempt:
                security_status = "BREACH_BLOCKED"
                system_response = f"ACCESS DENIED. The concept matched a restricted file at {round(highest_raw_score * 100, 1)}% match similarity. Your active signature token '{user_role}' is unauthorized."
                answer_text = "CRITICAL WARNING: Containment protocols activated. Propagation vector nullified."
                border_color = "border-rose-500 bg-rose-950/20"
                badge_color = "bg-rose-500/10 text-rose-400 border-rose-500/30"
            else:
                security_status = "NO_MATCH"
                system_response = f"No document fragments matched the semantic thresholds. (Max similarity discovered: {round(highest_raw_score * 100, 1)}%)."

    role_options_html = "".join(
        f'<option value="{role}" {"selected" if user_role==role else ""}>{role} Profile Signature</option>'
        for role in sorted(list(ALL_DISCOVERED_ROLES))
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en" class="h-full bg-zinc-950 text-zinc-50">
    <head>
        <meta charset="UTF-8"><title>ClearanceAI Autonomous Security Engine</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="p-8 font-sans max-w-5xl mx-auto">
        <header class="mb-8 border-b border-zinc-800 pb-4">
            <h1 class="text-2xl font-bold tracking-tight text-white"><span class="text-blue-500">ClearanceAI</span> Autonomous Engine</h1>
            <p class="text-sm text-zinc-400 mt-1">Generative AI Role-Classification and Enforcement via Local Vector Space Filters</p>
        </header>

        <section class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
                <h3 class="text-xs font-bold uppercase tracking-wider text-blue-400 mb-3">📁 Autonomous PDF / TXT File Ingestion</h3>
                <form method="post" action="/upload" enctype="multipart/form-data" class="space-y-4">
                    <div class="flex items-center justify-center w-full">
                        <label class="flex flex-col items-center justify-center w-full h-32 border-2 border-zinc-800 border-dashed rounded-lg cursor-pointer bg-zinc-950 hover:bg-zinc-900/50 hover:border-zinc-700 transition-colors">
                            <div class="flex flex-col items-center justify-center pt-5 pb-6">
                                <svg class="w-8 h-8 mb-3 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                                <p class="mb-1 text-xs text-zinc-400"><span class="font-semibold">Click to upload</span> security asset</p>
                                <p class="text-[10px] text-zinc-500">PDF or TXT (Max 5MB)</p>
                            </div>
                            <input type="file" name="file" class="hidden" accept=".pdf,.txt" required />
                        </label>
                    </div>
                    <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs rounded-lg py-2.5 transition-colors">
                        Extract Content & Autonomously Allocate Permissions
                    </button>
                </form>
            </div>

            <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col justify-between">
                <div>
                    <h3 class="text-xs font-bold uppercase tracking-wider text-purple-400 mb-3">🔍 Dynamic Identity Gateway</h3>
                    <form method="get" action="/" class="space-y-3">
                        <div>
                            <select name="user_role" class="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-xs text-white">
                                {role_options_html}
                            </select>
                        </div>
                        <input type="text" name="query" value="{query}" placeholder="Search matching concepts..." class="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-xs text-white"/>
                        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs rounded-lg py-2.5 transition-colors">
                            Query Dynamic Index Loop
                        </button>
                    </form>
                </div>
            </div>
        </section>

        <main class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="border border-zinc-800 bg-zinc-900/40 rounded-xl p-6">
                <h3 class="text-xs font-bold uppercase tracking-wider text-zinc-400 mb-4">Active Database Clusters (Autonomously Created Roles)</h3>
                <div class="space-y-3">
                    {"".join(f'''
                    <div class="p-3 rounded-lg border bg-zinc-950 text-xs border-zinc-800">
                        <div class="flex justify-between font-semibold text-blue-400 mb-1">
                            <span>Asset: {item["filename"]}</span>
                            <span class="text-purple-400 font-mono">AI Generated Access Tags: {", ".join(item["roles"])}</span>
                        </div>
                        <p class="text-zinc-400 mt-1 truncate">{item["text"]}</p>
                    </div>
                    ''' for item in SYSTEM_LOGS) if SYSTEM_LOGS else '<p class="text-xs text-zinc-600 italic">No files loaded yet. Drop a PDF or TXT above to run pipeline mechanics.</p>'}
                </div>
            </div>

            <div class="border rounded-xl p-6 flex flex-col justify-between {border_color}">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-zinc-300">FastAPI Qdrant Payload Output</h3>
                        <span class="text-[10px] px-2 py-0.5 rounded-full border font-mono font-medium {badge_color}">STATUS: {security_status}</span>
                    </div>
                    <div class="space-y-3 text-sm">
                        <div><span class="text-xs text-zinc-500 block">System Diagnostic:</span><p class="font-medium text-zinc-200 text-xs">{system_response}</p></div>
                        <div class="border-t border-zinc-800 pt-3"><span class="text-xs text-zinc-500 block">Retrieved Vector Chunk Payload Text:</span><p class="font-mono text-xs text-zinc-300 mt-1 leading-relaxed bg-black/40 p-3 rounded border border-zinc-800">{answer_text}</p></div>
                    </div>
                </div>
                <div class="mt-4 text-[10px] font-mono text-zinc-500 flex justify-between border-t border-zinc-800/60 pt-3">
                    <span>Active Security Context Token: User.{user_role}</span>
                    <span>Tokens: 0-cost (ONNX Index) + Gemini Analytics</span>
                </div>
            </div>
        </main>
    </body>
    </html>
    """

@app.post("/upload")
async def handle_automated_ingestion(file: UploadFile = File(...)):
    global doc_id_counter, ALL_DISCOVERED_ROLES, qdrant_db, SYSTEM_LOGS
    
    # 1. READ PHYSICAL FILE CONTENTS DYNAMICALLY
    contents = await file.read()
    extracted_text = ""
    
    if file.filename.endswith(".pdf"):
        try:
            pdf_stream = io.BytesIO(contents)
            pdf_reader = pypdf.PdfReader(pdf_stream)
            # Extract text across all pages smoothly
            extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        except Exception as e:
            return HTMLResponse(content=f"<h3>Error processing PDF structure: {str(e)}</h3>")
    else:
        # Standard .txt decoding handling
        extracted_text = contents.decode("utf-8", errors="ignore")
        
    if not extracted_text.strip():
        return HTMLResponse(content="<h3>Error: Could not extract valid string content from file asset.</h3>")

    # 2. GENERATIVE BOUNDARY STEP: Let the AI invent the required clearance tags dynamically
    generated_roles = fetch_ai_generated_roles(extracted_text)
    for role in generated_roles:
        ALL_DISCOVERED_ROLES.add(role)
    
    # 3. INGEST INTO THE VECTOR GRID
    qdrant_db.add(
        collection_name=COLLECTION_NAME,
        documents=[extracted_text],
        metadata=[{"allowed_roles": generated_roles}],
        ids=[doc_id_counter]
    )
    
    SYSTEM_LOGS.append({
        "id": doc_id_counter, 
        "filename": file.filename, 
        "text": extracted_text, 
        "roles": generated_roles
    })
    doc_id_counter += 1
    
    return HTMLResponse(content="<script>window.location.href='/';</script>")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)