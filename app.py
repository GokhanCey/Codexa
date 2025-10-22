from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests, os, secrets, sqlite3
from slugify import slugify
import uuid
import db  # local db.py

# --------------------------------------------
# CONFIGURATION
# --------------------------------------------
load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not ELASTIC_URL or not ELASTIC_API_KEY:
    raise ValueError("Elastic credentials not set in .env")

es = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# --------------------------------------------
# ROUTES — UI
# --------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api_keys")
def api_keys_page():
    return render_template("api_keys.html")

@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")

# --------------------------------------------
# API: CREATE PROJECT (admin protected)
# --------------------------------------------
@app.route("/api/create_project", methods=["POST"])
def create_project():
    try:
        if request.headers.get("X-Admin-Token") != os.getenv("ADMIN_TOKEN"):
            return "Unauthorized", 403

        data = request.get_json(force=True)
        name = data.get("name")
        category = data.get("category")

        if not name or not category:
            return "Missing name or category", 400

        index_name = f"codexa-{slugify(name)}-{uuid.uuid4().hex[:8]}"
        api_key = uuid.uuid4().hex

        db.create_elastic_index(index_name)
        db.add_project(name, index_name, api_key, category)


        return jsonify({
            "project": name,
            "index": index_name,
            "api_key": api_key,
            "category": category
        })

    except Exception as e:
        print(f"[ERROR] Failed to create project: {e}")
        return f"Internal Server Error: {e}", 500


# --------------------------------------------
# API: GET PROJECTS (admin protected)
# --------------------------------------------
@app.route("/api/get_projects")
def get_projects():
    token = request.headers.get("X-Admin-Token")
    if ADMIN_TOKEN and token != ADMIN_TOKEN:
        return jsonify({"error": "Forbidden"}), 403

    conn = sqlite3.connect("codexa.db")
    c = conn.cursor()
    c.execute("SELECT name, api_key FROM projects")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"name": r[0], "api_key": r[1]} for r in rows])

# --------------------------------------------
# API: UPLOAD FILE
# --------------------------------------------
@app.route("/api/upload", methods=["POST"])
def api_upload():
    api_key = request.headers.get("X-API-Key")
    file = request.files.get("file")

    if not api_key or not file:
        return jsonify({"error": "Missing API key or file"}), 400

    project = db.get_project(api_key)
    if not project:
        return jsonify({"error": "Invalid API key"}), 403

    _, name, index_name, *_ = project

    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    text = ""
    if filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            return jsonify({"error": f"PDF parsing failed: {str(e)}"}), 500
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    if not text.strip():
        return jsonify({"error": "File is empty or unreadable"}), 400

    es.index(index=index_name, document={"content": text, "filename": filename})
    return jsonify({"message": f"File '{filename}' indexed successfully into {index_name}"}), 200

# --------------------------------------------
# API: QUERY
# --------------------------------------------
@app.route("/api/query", methods=["POST"])
def api_query():
    api_key = request.headers.get("X-API-Key")
    data = request.get_json()
    query = data.get("query")

    if not api_key or not query:
        return jsonify({"error": "Missing API key or query"}), 400

    project = db.get_project(api_key)
    if not project:
        return jsonify({"error": "Invalid API key"}), 403

    _, name, index_name, *_ = project


    try:
        search_body = {
            "size": 5,
            "query": {"match": {"content": query}}
        }
        res = es.search(index=index_name, body=search_body)
        hits = res["hits"]["hits"]

        if not hits:
            return jsonify({"answer": "No relevant information found."}), 200

        context_sections = []
        evidence_snippets = []

        for i, h in enumerate(hits, start=1):
            src = h["_source"]
            text = src.get("content", "")
            fname = src.get("filename", "document.txt")

            snippet = text[:300].strip().replace("\n", " ")
            evidence_snippets.append(f"[Source {i}: {fname}] {snippet}...")

            context_sections.append(f"[Source {i}: {fname}]\n{text[:2000]}")


        context = "\n\n---\n\n".join(context_sections)

        # Prompt
        prompt = f"""
        You are Codexa — an intelligent document understanding assistant.

        Your task:
        - Provide a **direct, confident answer first**, based on the given context.
        - If the answer isn't stated directly but can be clearly inferred, explain the reasoning briefly.
        - Mention relevant evidence only if it strengthens the answer.
        - If the document truly lacks information, say: "That detail isn’t covered in the provided document."

        Style:
        - Write in clear, natural English — no robotic phrasing.
        - Avoid meta-comments like "based on the provided text".
        - Keep it professional, concise, and easy to read.

        Question:
        {query}

        Context:
        {context}
        """

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        ai_res = requests.post(GEMINI_URL, json=payload)

        if ai_res.ok:
            data = ai_res.json()
            summary = data["candidates"][0]["content"]["parts"][0]["text"]
            summary = summary.strip()
            if summary.lower().startswith("based on the provided"):
                summary = summary.replace("Based on the provided text:", "").strip()


            return jsonify({
                "answer": summary,
                "sources": len(hits),
                "source_list": [h["_source"].get("filename", "unknown") for h in hits],
                "evidence_snippets": evidence_snippets
            }), 200


        return jsonify({"error": "Gemini request failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------
# RUN APP
# --------------------------------------------
if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000)
