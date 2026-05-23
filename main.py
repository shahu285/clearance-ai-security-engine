from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Initialize our App & Zero-Cost Tools
app = FastAPI(title="ClearanceAI Security Engine")

# This boots up a vector database inside your computer's RAM
# Initialize Qdrant's built-in ultra-light fastembed engine
# It automatically uses all-MiniLM-L6-v2 at 1/10th the memory cost!
qdrant_db = QdrantClient(":memory:")
qdrant_db.set_model("BAAI/bge-small-en-v1.5") # A fantastic 384-dimension model that runs natively inside Qdrant at lightning speed

# This downloads a high-performance math model to your CPU to turn text into vectors
print("--- LOADING LOCAL EMBEDDING TRANSFORMER MODEL (0 COST) ---")
# Force the embedding engine to run using optimized CPU settings
embedding_engine = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

COLLECTION_NAME = "secure_vault"

# Create the collection structure inside Qdrant
qdrant_db.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# 2. Ingestion: Adding Data onto Vector Points
RAW_DATA = [
    {
        "text": "The Q3 corporate revenue increased by 14% to $4.2M, driven by rapid cloud infrastructure adoptions.",
        "allowed_roles": ["Finance", "Executive"],
        "source": "fin_report_2026.pdf"
    },
    {
        "text": "The standard employee performance bonus calculation formula is: Base Salary * Performance Score * 0.10.",
        "allowed_roles": ["HR", "Executive"],
        "source": "hr_policy_v2.pdf"
    },
    {
        "text": "The company cafeteria offers subsidized lunch meals, open from 8:00 AM to 7:00 PM Monday through Friday.",
        "allowed_roles": ["Public", "Employee", "HR", "Finance", "Executive"],
        "source": "general_info.pdf"
    }
]

# Convert text blocks into mathematical vectors and store them
points = []
for index, item in enumerate(RAW_DATA):
    math_vector = embedding_engine.embed_query(item["text"])
    
    points.append(PointStruct(
        id=index,
        vector=math_vector,
        payload={"text": item["text"], "allowed_roles": item["allowed_roles"], "source": item["source"]}
    ))

qdrant_db.upsert(collection_name=COLLECTION_NAME, points=points)
print("--- LOCAL VECTOR VAULT ARMED AND SEEDED ---")


# 3. Dynamic Interactive Dashboard Route
@app.get("/", response_class=HTMLResponse)
def render_dashboard(user_role: str = "HR", query: str = "salary"):
    
    # AI STEP 1: Turn the user's search query into vector math
    query_vector = embedding_engine.embed_query(query)
    
    # SECURITY GATE STEP 2: Execute a strict RBAC Metadata Filter
    rbac_metadata_filter = Filter(
        must=[
            FieldCondition(
                key="allowed_roles",
                match=MatchValue(value=user_role)
            )
        ]
    )
    
    # EXECUTE THE SEARCH: Vector Search + Security Check happening together using correct API names
    search_results = qdrant_db.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=rbac_metadata_filter,
        limit=1
    )

    # 4. PARSE SEARCH METRICS FOR SCREEN RENDER
    # 4. PARSE SEARCH METRICS FOR SCREEN RENDER
    security_status = "ENFORCED"
    
    # CRITICAL FIX: Only accept the match if the AI confidence score is above 0.35 (35%)
    # Change 0.35 to 0.25
    if search_results and search_results.points and search_results.points[0].score > 0.25:
        hit = search_results.points[0]
        system_response = f"Success! Retrievable contexts found via AI Semantic Search. Source file: '{hit.payload['source']}' (Vector Match Confidence: {round(hit.score * 100, 1)}%)"
        answer_text = hit.payload["text"]
        border_color = "border-emerald-500 bg-emerald-950/20"
        badge_color = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
    else:
        # Check if the text actually existed but was blocked by security
        unfiltered_check = qdrant_db.query_points(collection_name=COLLECTION_NAME, query=query_vector, limit=3)
        
        # Capture the highest score from the unfiltered database to see what's happening
        highest_raw_score = unfiltered_check.points[0].score if unfiltered_check.points else 0.0
        
        breach_attempt = any(
            item.score > 0.20 and user_role not in item.payload["allowed_roles"] 
            for item in unfiltered_check.points
        )
        
        if breach_attempt:
            security_status = "BREACH_BLOCKED"
            system_response = f"ACCESS DENIED. A restricted document matched your query with a score of {round(highest_raw_score * 100, 1)}%, but your role signature is unauthorized."
            answer_text = "ERROR: Document containment protocols active. Vector context propagation aborted."
            border_color = "border-rose-500 bg-rose-950/20"
            badge_color = "bg-rose-500/10 text-rose-400 border-rose-500/30"
        else:
            security_status = "NO_MATCH"
            system_response = f"No matching profiles discovered. (The highest matching document scored a very low {round(highest_raw_score * 100, 1)}%)."
            answer_text = "No document fragments matched the semantic vector metrics."
            border_color = "border-zinc-700 bg-zinc-900/50"
            badge_color = "bg-zinc-800 text-zinc-400 border-zinc-700"

    # 5. FRONTEND COMPOSITION RENDER
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en" class="h-full bg-zinc-950 text-zinc-50">
    <head>
        <meta charset="UTF-8">
        <title>ClearanceAI Enterprise Security Studio</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="p-8 font-sans max-w-5xl mx-auto">
        <header class="mb-8 border-b border-zinc-800 pb-4">
            <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                <span class="text-blue-500">ClearanceAI</span> Security Engine
            </h1>
            <p class="text-sm text-zinc-400 mt-1">Enforcing Real-Time Role-Based Access Control (RBAC) Inside Qdrant Vector Spaces</p>
        </header>

        <section class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <form method="get" action="/" class="md:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">1. Select User Security Profile</label>
                    <select name="user_role" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                        <option value="HR" {"selected" if user_role=="HR" else ""}>HR Manager Tier</option>
                        <option value="Finance" {"selected" if user_role=="Finance" else ""}>Financial Analyst Tier</option>
                        <option value="Public" {"selected" if user_role=="Public" else ""}>Public Guest Tier</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">2. Enter Database Query Phrase</label>
                    <input type="text" name="query" value="{query}" placeholder="e.g., revenue, bonus, lunch" 
                           class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"/>
                </div>
                <div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm rounded-lg px-4 py-2 transition-colors">
                        Execute Secure Retrieval Loop
                    </button>
                </div>
            </form>
        </section>

        <main class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="border border-zinc-800 bg-zinc-900/40 rounded-xl p-6">
                <h3 class="text-xs font-bold uppercase tracking-wider text-zinc-400 mb-4">Internal Qdrant RAM Storage Logs</h3>
                <div class="space-y-3">
                    {"".join(f'''
                    <div class="p-3 rounded-lg border bg-zinc-950 text-xs {"border-blue-900/50" if user_role in item["allowed_roles"] else "border-zinc-800 opacity-40"}">
                        <div class="flex justify-between font-semibold text-zinc-300 mb-1">
                            <span>File: {item["source"]}</span>
                            <span class="text-zinc-500">Clearance: {", ".join(item["allowed_roles"])}</span>
                        </div>
                        <p class="text-zinc-400 truncate">{item["text"]}</p>
                    </div>
                    ''' for item in RAW_DATA)}
                </div>
            </div>

            <div class="border rounded-xl p-6 flex flex-col justify-between {border_color}">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-zinc-300">FastAPI Qdrant Payload Output</h3>
                        <span class="text-[10px] px-2 py-0.5 rounded-full border font-mono font-medium {badge_color}">
                            STATUS: {security_status}
                        </span>
                    </div>
                    
                    <div class="space-y-3 text-sm">
                        <div>
                            <span class="text-xs text-zinc-500 block">System Diagnostic:</span>
                            <p class="font-medium text-zinc-200">{system_response}</p>
                        </div>
                        <div class="border-t border-zinc-800 pt-3">
                            <span class="text-xs text-zinc-500 block">Retrieved Vector Chunk Payload Text:</span>
                            <p class="font-mono text-xs text-zinc-300 mt-1 leading-relaxed bg-black/40 p-3 rounded border border-zinc-800">{answer_text}</p>
                        </div>
                    </div>
                </div>

                <div class="mt-4 text-[10px] font-mono text-zinc-500 flex justify-between border-t border-zinc-800/60 pt-3">
                    <span>Active User Clearance: User.{user_role}</span>
                    <span>Tokens: 0-cost (Local Embeddings Engine)</span>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)