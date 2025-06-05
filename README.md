# 🚀 CVisionary
**✨ Your Dream Job, One Resume Away ✨**  

🎯 Craft AI-optimized resumes that match job descriptions, generate professionally formatted content, and score higher in Applicant Tracking Systems (ATS). Built with cutting-edge technology including React 19, Vite, Tailwind CSS, and powerful LLM integration.

---

## ✨ Key Features

- 🔐 **OAuth Login** (LinkedIn, GitHub)
- 🔍 **LinkedIn & GitHub Scraper**
- 🎯 **AI-Powered Resume Matching** with job descriptions
- 🧠 **LLM-Powered Resume Generation**
- 📄 **PDF/LaTeX Export Support**
- ✏️ **Editable Resume Preview**
- 📊 **Resume Scoring System**
- 💡 **AI-Based Resume Improvement Suggestions**
- 🏆 **ATS-Friendly Output**

---

## 🛠️ Tech Stack

| Tech            | Purpose                                      |
|-----------------|----------------------------------------------|
| React 19        | Frontend Framework                           |
| Vite            | Lightning-fast dev server                    |
| Tailwind CSS    | Utility-first styling                        |
| Shadcn/ui       | UI Components                                |
| Lucide-react    | Icon library                                 |
| Framer Motion   | Animations                                   |
| Node.js + Express | Backend APIs                              |
| MongoDB         | Vector DB / Resume Storage                   |
| OpenAI / Gemini | LLM for resume generation                    |
| Python 3.10+    | AI/ML microservices (Embedding, Generation)  |
| FastAPI         | AI/ML API framework                          |
| Sentence-Transformers | Embeddings generation             |
| FAISS-CPU       | In-memory vector search                      |
| scikit-learn    | ATS scoring model                            |

---

## 📁 Project Structure
```
📁 root/
├── 📁 backend/
│   ├── 📁 controllers/
│   ├── 📁 routes/
│   ├── 📁 utils/          # Contains LLM prompts, scraping logic, etc.
│   └── server.js
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/ # Reusable UI components
│   │   ├── 📁 pages/      # Route-based pages
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── index.html
├── 📁 ai-services/        # AI/ML microservices (Embedding, Generator, Scoring)
│   ├── 📁 embedding_service/
│   ├── 📁 generator_service/
│   └── 📁 scoring_service/
├── .env
├── README.md
└── package.json
```

---

## 🖥️ Pages and Routes

| Route              | Page Name               | Description                           |
| ------------------ | ----------------------- | ------------------------------------- |
| `/`                | Landing Page            | App intro, login buttons              |
| `/dashboard`       | Dashboard               | Overview & scraping/resume status     |
| `/connect`         | LinkedIn/GitHub Connect | OAuth & scraping                      |
| `/job-description` | Job Description Input   | Enter target JD                       |
| `/resume-preview`  | Resume Output + Editing | AI-generated resume + edits           |
| `/ai-improver`     | Resume AI Improver Page | Get suggestions to improve the Resume |

---

## 🤖 AI Integration

The AI/ML portion consists of three lightweight microservices that operate alongside the existing backend:

1. **Embedding Service**

   * Chunks user profile text (experiences, projects, skills) into small pieces.
   * Uses a sentence-transformer model (e.g., `all-MiniLM-L6-v2`) to convert each chunk (and incoming job descriptions) into 384-dimensional vectors.
   * Indexes these vectors in an in-memory FAISS index (persisted in a local SQLite database).
   * Exposes endpoints to (a) generate embeddings for arbitrary text and (b) retrieve the top-K most relevant profile chunks for a given job-description embedding.

2. **Resume Generator Service**

   * Receives the retrieved profile chunks and job-description embedding.
   * Forms a Retrieval-Augmented Generation (RAG) prompt that combines “must-have” job keywords with the most relevant user passages.
   * Invokes an LLM (either a local LLaMA/Mistral checkpoint or OpenAI/Gemini) to produce concise, job-tailored bullet points.

3. **ATS Scoring Service**

   * Takes the generated bullet points plus job-description features.
   * Computes simple features such as keyword overlap and semantic similarity (via embeddings).
   * Uses a lightweight scikit-learn classifier (e.g., logistic regression) to return an “ATS match score” and a few short improvement suggestions if the score is below a threshold.

> **Note:** Each AI/ML service runs locally on a separate port (e.g., 8001, 8002, 8003) using FastAPI and can be containerized via Docker Compose. When deployed to GCP, these can be migrated to Cloud Run or Vertex AI endpoints without changing the overall flow.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/QuantumRebels/CVisionary.git
cd CVisionary
```

### 2. Setup the Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Setup the Backend

```bash
cd backend
npm install
npm run dev
```

---

### 4. Setup & Run the AI/ML Services

1. **Embedding Service**

   ```bash
   cd ai-services/embedding_service
   pip install -r requirements.txt
   # Ensure a local SQLite DB (e.g., embeddings.db) is in place or will be created on startup
   uvicorn app:app --reload --port 8001
   ```

   * **Endpoints:**

     * `POST /index/{userId}` → Fetches structured profile JSON, chunks it, generates embeddings, and indexes in FAISS.
     * `POST /embed` → Returns an embedding for any input text.
     * `POST /retrieve/{userId}` → Returns the top-K profile chunks for a given query embedding.

2. **Resume Generator Service**

   ```bash
   cd ai-services/generator_service
   pip install -r requirements.txt
   uvicorn app:app --reload --port 8002
   ```

   * **Endpoint:**

     * `POST /generate/{userId}` → Accepts a job-description string, retrieves top profile chunks, assembles a RAG prompt, and calls an LLM to produce tailored bullet points.

3. **ATS Scoring Service**

   ```bash
   cd ai-services/scoring_service
   pip install -r requirements.txt
   uvicorn app:app --reload --port 8003
   ```

   * **Endpoint:**

     * `POST /score` → Accepts the job-description and generated bullet points, computes features, and returns an ATS match score and short improvement suggestions.

> **Tip:** If you don’t have each directory in place yet, create them under `ai-services/` and copy the relevant service code (FastAPI app, models, etc.) into them. Each service uses its own `.env` file for configuration, as shown below.

---

## ⚙️ Environment Variables

**Backend (.env in `backend/`):**

```bash
MONGODB_URL=
LINKEDIN_API_KEY=...
GITHUB_API_KEY=...
OPENAI_API_KEY=...
```

**Embedding Service (`ai-services/embedding_service/.env`):**

```bash
SQLITE_PATH=./embeddings.db
MODEL_NAME=all-MiniLM-L6-v2
```

**Generator Service (`ai-services/generator_service/.env`):**

```bash
LLM_MODEL_PATH=/path/to/local-llama-model.bin  # or leave blank to use OpenAI/Gemini
OPENAI_API_KEY=...
```

**Scoring Service (`ai-services/scoring_service/.env`):**

```bash
ATS_MODEL_PATH=/path/to/ats_model.pkl
```

---

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)

---

## 👩‍💻 Developed By

**Team QuantumRebels**  
💫 Made With Passion & Cutting-Edge AI  
🎯 Helping You Land Your Dream Job, One Resume at a Time!  

> "The future belongs to those who believe in the beauty of their dreams." - Eleanor Roosevelt  
💙 Best of luck on your job search journey! 🚀

```