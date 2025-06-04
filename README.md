# 📝 CVisionary
**Your Dream Job, One Resume Away**  
Craft AI-optimized resumes that match job descriptions, generate professionally formatted content, and score higher in Applicant Tracking Systems (ATS). Built with React 19, Vite, Tailwind CSS, and LLM integration.

---

## 🚀 Features

- 🔐 **OAuth Login** (LinkedIn, GitHub)
- 🔍 **LinkedIn & GitHub Scraper**
- 🧠 **AI-Powered Resume Matching** with job descriptions
- ✨ **LLM-Powered Resume Generation**
- 📤 **PDF/LaTeX Export Support**
- 🧾 **Editable Resume Preview**
- 📊 **Resume Scoring System**
- 📌 **AI-Based Resume Improvement Suggestions**
- 🎯 **ATS-Friendly Output**

---

## 🧩 Tech Stack

| Tech        | Purpose                        |
|-------------|--------------------------------|
| React 19    | Frontend Framework             |
| Vite        | Lightning-fast dev server      |
| Tailwind CSS| Utility-first styling          |
| Shadcn/ui   | UI Components                  |
| Lucide-react| Icon library                   |
| Framer Motion | Animations                   |
| Node.js + Express | Backend APIs             |
| MongoDB     | Vector DB / Resume Storage     |
| OpenAI / Gemini | LLM for resume generation  |

---

## 📁 Folder Structure
```bash
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
├── .env
├── README.md
└── package.json
```


---

## 🖥️ Pages and Routes

| Route               | Page Name               | Description                            |
|--------------------|-------------------------|-----------------------------------------|
| `/`                | Landing Page            | App intro, login buttons                |
| `/dashboard`       | Dashboard               | Overview & scraping/resume status       |
| `/connect`         | LinkedIn/GitHub Connect | OAuth & scraping                        |
| `/job-description` | Job Description Input   | Enter target JD                         |
| `/resume-preview`  | Resume Output + Editing | AI-generated resume + edits             |
| `/ai-improver`     | Resume AI Improver Page | Get suggestions to improve the Resume   |

---

## 🧠 AI Integration

- **Vector Embedding:** For job-resume similarity
- **LLM Prompting:** To generate resume sections
- **Score System:** For ATS compatibility estimation
- **Improvement Suggestions:** Prompt LLM for resume enhancements

---

## ⚙️ Setup & Run

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

### 3. Setup the backend
```bash
cd backend
npm install
npm run dev
```
---
## 4️⃣ Environment Variables
Create a .env file in the backend directory with the following details:

```bash
MONGODB_URL = 
LINKEDIN_API_KEY=...
GITHUB_API_KEY=...
OPENAI_API_KEY=...
```
---

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)

---

## 👩‍💻 Developed By

**Team QuantumRebels**  
Made With 💙 , Made For You so that u dont stay Unplaced anymore !! LOL , ALL THE BEST .


