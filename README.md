# 🧊 Instalily Case Study – Chat Agent for PartSelect

## 🧠 Overview

This project implements a **agentic chat system** to support users browsing **Refrigerator** and **Dishwasher** parts on [PartSelect.com](https://www.partselect.com). Initially the goal was to implement a **corrective agentic RAG system**, however this was infeasible with my current skills due to permission rules and bot detection on *PartSelect.com*. The repo leverages:

- **LangChain** + **DeepSeek** for agentic reasoning
- **Playwright** for real-time search and product data scraping
- **ChromaDB** for optional document-based retrieval
- **React** for a responsive chat-based frontend inspired by PartSelect branding

The goal is to build an extensible, task-aware assistant that provides product compatibility, pricing, reviews, installation tips, and troubleshooting help.

---

## 🚀 Installation Instructions

### 🧪 Local Installation (only Windows 11 option available)

#### 🔧 Python Backend

1. Create the Conda environment and activate:
   ```bash
   conda env create -f environment.yml
   conda activate instalily
   ```

2. Start the backend:
   ```bash
   cd backend
   python main.py
   ```

> 📝 **Note**: Make sure your `.env` file exists in the root directory with `DEEPSEEK_API_KEY` and `OPENAI_API_KEY` configured.

> 🧠 If the Chroma vector DB (`backend/db` or `backend/chroma`) was generated with an older LangChain version, **delete the directory** before running to avoid metadata errors.

#### 🌐 React Frontend

1. Start the React interface:
   ```bash
   cd case-study-main
   npm install
   npm start
   ```

> 📝 This will serve the frontend at `http://localhost:3000` and connect to the Flask backend on `http://localhost:8000`.

---

### 🐳 Docker Installation (Linux - xvfb for headful)

> ✅ Recommended if you want reproducibility or avoid dependency issues.

#### 1. Build and start both frontend and backend

```bash
docker compose up --build
```

This will:

- Start the Flask backend on `http://localhost:8000`
- Serve the React frontend on `http://localhost:3000`

#### 2. Important Notes

- 📦 **Chroma vector DB must be rebuilt in Docker** if any metadata errors occur.
  - Delete any old DB folders (e.g., `backend/db` or `backend/chroma`) on your host before first compose run:
    ```bash
    rm -rf backend/db
    ```

- 🔐 Ensure your `.env` file is included in the build context and contains valid API keys for both DeepSeek and OpenAI:
    ```
    OPENAI_API_KEY=sk-...
    DEEPSEEK_API_KEY=sk-...
    SCRAPER_API_KEY=<api-key>
    BRIGHTDATA_USERNAME = <your-username>
    BRIGHTDATA_PASSWORD = <your-pw>
    # This is for the retriever
    USE_DEEPSEEK=false # These matter less but need to be set
    DEBUG=false
    USE_DOCKER=true
    REACT_APP_USE_DOCKER=true
    REACT_APP_BACKEND_HOST=http://backend:8000
    ```

- 🧪 You can verify the backend is running by visiting:
    - `http://localhost:8000/` (backend)
    - `http://localhost:3000/` (frontend)

### ⚠️ RAG Limitations & Countermeasures
Scraping product details in bulk proved unreliable due to aggressive anti-bot defenses.

#### Attempted Workarounds
✅ Rotating proxies (BrightData, ScraperAPI)

✅ Header spoofing & user-agent substitution

✅ Playwright stealth mode & randomized delays

❌ Still blocked when scraping many product pages or running fully headless

### ⚠️ LLM Limitations
Despite a working toolchain, I wasn’t able to get the system prompt to consistently handle ambiguous open-ended queries (e.g., no explicit SKU or part number). With more time, I could refine the regex preprocessing and prompt scaffolding to address this by iterating though all possible combination of part ypes and brand names.

Time was unfortunately lost trying to build out a full RAG pipeline to provide a better user experience and avoid excessive dynamic searching—ultimately not viable given scraping constraints.

### Final Approach
I use on-demand search agents via Playwright to dynamically extract structured product information only when needed, drastically reducing suspicion while preserving functionality. 

