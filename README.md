# Codexa  
**Evidence-Powered AI for Smarter Search**

Codexa combines **Elastic Search** and **Google Gemini** to deliver AI answers that are grounded in real data — not guesses.  
Upload your documents, ask questions, and get verified insights with full reasoning and context.

---

## Overview  
Most AI tools guess their way to answers. Codexa doesn’t.  
It connects Elastic’s fast, context-aware retrieval with Gemini’s advanced reasoning to create an AI that **explains with evidence**.  

Codexa is designed for professionals, researchers, and developers who want factual, traceable, and intelligent results from their own data.

---

## Features  
- **Evidence-Based Answers** – Every response includes reasoning grounded in your own indexed data  
- **Elastic + Gemini Integration** – Combines the speed of Elastic with the intelligence of Gemini  
- **Simple Dashboard** – Upload PDFs or text files and ask questions instantly  
- **Secure Local API Storage** – Uses SQLite for API key management  
- **Modern Interface** – Custom dark UI built with clean HTML and CSS  

---

## Architecture  

<img width="1638" height="543" alt="codexa-architecture" src="https://github.com/user-attachments/assets/b40bbf92-5ca5-496f-8241-b35daeb53bda" />


**Codexa Architecture — Elastic + Gemini Powered AI Search**

**Workflow:**
1. The user uploads a PDF or text file through the dashboard.  
2. Flask processes and indexes the document into Elastic Cloud.  
3. Elastic retrieves relevant context when a question is asked.  
4. Gemini 2.5 processes that context and returns a summarized, reasoned answer.  
5. Codexa displays the evidence-based result instantly.

---

## ⚙️ Installation  

### 1. Clone the repository
```bash
git clone https://github.com/GokhanCey/Codexa.git
cd Codexa
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux  
.venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
Create a .env file in the root directory:
```bash
ELASTIC_URL=https://your-elastic-endpoint
ELASTIC_API_KEY=your_elastic_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Run the app
```bash
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

---

### Built With
- **Python (Flask)** — Backend and API routing  
- **Elastic Cloud** — Document indexing and search  
- **Google Gemini API** — Summarization and reasoning  
- **SQLite** — Local database for API key storage  
- **HTML + CSS (Custom Dark UI)** — Frontend design  
- **PyPDF2** — PDF text extraction  

---

### Hackathon Entry
- **Challenge:** AI Accelerate – Unlocking New Frontiers  
- **Partner Focus:** Elastic  
Codexa shows how Elastic can work with generative AI to produce factual, verifiable insights by combining retrieval, reasoning, and explainability in one system.

---

### Roadmap
- Add user accounts and usage tracking  
- Support multiple document contexts  
- Highlight evidence citations in summaries  
- Deploy on Render or Vercel with a managed backend  

---

### License 📄
Released under the **MIT License**.  
You’re free to use, modify, and share with credit.

---

### Live Demo & Links
- **Website:** [thecodexa.com](https://thecodexa.com)  
- **Frontend Demo:** `/templates/index.html`  
- **Architecture Image:** `/static/img/codexa-architecture.png`  

---

### Author Developed by Gökhan Ceylan 
GitHub: @GokhanCey
