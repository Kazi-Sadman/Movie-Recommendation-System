# 🎬 Movie Recommendation System

A full-stack **content-based movie recommender** built with Streamlit, FastAPI,
scikit-learn (TF-IDF + cosine similarity), and the TMDB API.

---

## 🌐 Live Deployment

| Service                     | URL                                                        |
| --------------------------- | ---------------------------------------------------------- |
| 🎨 **Frontend** (Streamlit) | https://movie-recommendation-app-sfxg.onrender.com         |
| ⚡ **Backend** (FastAPI)    | https://movie-recommendation-api-7910.onrender.com         |
| 📚 **API Docs** (Swagger)   | https://movie-recommendation-api-7910.onrender.com/docs    |
| 💻 **GitHub Repo**          | https://github.com/Kazi-Sadman/Movie-Recommendation-System |

> ⚠️ The backend runs on Render's **free tier** and cold-starts after ~15 min idle.
> The first request can take 30–60 seconds. The frontend retries automatically.

---

## ✨ Features

- 🏠 **Home** — trending, popular, top-rated, now playing, upcoming feeds
- 🔍 **Search** — type a title, press Search, browse results
- 🎬 **Movie Details** — poster, backdrop, overview, genres, rating
- 🎯 **Recommendations** — genre-based suggestions on the details page
- ⚖️ **Compare Movies** — two movies side-by-side
- 📊 **Movie Analytics** — dataset statistics & TF-IDF vocabulary
- 📌 **Watchlist** — save movies, mark watched/unwatched (SQLite)
- ❤️ **Favorites** — save your all-time favorites (SQLite)
- ℹ️ **About Project** — how the recommender works

---

## 🧠 How the Recommender Works

Movie text (overview + genres + tagline)
│
▼
Text cleaning (lowercase, stopwords, lemmatize)
│
▼
TF-IDF vectorization → 45,447 × 5,766 matrix
│
▼
Cosine similarity query movie vs all movies
│
▼
Top-N most similar movies

This is **content-based filtering** — no collaborative filtering, no user
profiles, no deep learning.

---

## 🛠 Tech Stack

| Layer      | Technology                  |
| ---------- | --------------------------- |
| Frontend   | Streamlit                   |
| Backend    | FastAPI + Uvicorn           |
| ML         | scikit-learn, pandas, numpy |
| Storage    | SQLite                      |
| Data       | TMDB API                    |
| Deployment | Render                      |

---

## 📂 Project Structure

Movie-Recommendation-System/
├── app.py # Streamlit frontend
├── main.py # FastAPI backend
├── database.py # SQLite helpers (watchlist + favorites)
├── requirements.txt
├── .env # TMDB_API_KEY (not committed)
├── .gitignore
├── README.md # ← you are here
│
├── data/
│ └── processed/
│ ├── df.pkl
│ ├── indices.pkl
│ ├── tfidf.pkl
│ └── tfidf_matrix.pkl
│
├── notebooks/
│ └── movies.ipynb # Data analysis + model training
│
└── docs/
├── 01_PRD.md
├── 02_TRD.md
├── 03_APP_FLOW.md
├── 04_DESIGN_BRIEF.md
├── 05_DATABASE_SCHEMA.md
└── 06_IMPLEMENTATION_PLAN.md

---

## 🚀 Run Locally

### 1. Clone & install

```bash
git clone https://github.com/Kazi-Sadman/Movie-Recommendation-System.git
cd Movie-Recommendation-System

python -m venv .venv
.venv\Scripts\activate         # Windows
source .venv/bin/activate      # macOS / Linux

pip install -r requirements.txt

2. Configure environment
Create .env in the repo root:
TMDB_API_KEY=your_tmdb_api_key
Get a free key from https://www.themoviedb.org/settings/api

3. Start the backend
uvicorn main:app --reload

Backend runs at http://127.0.0.1:8000.
Swagger UI at http://127.0.0.1:8000/docs.

4. Start the frontend
 streamlit run app.py
Opens http://localhost:8501.

🔌 API Endpoints
Method	Path	Purpose
GET	/health	Liveness check
GET	/home?category=trending	Home feed
GET	/tmdb/search?query=...	TMDB search
GET	/movie/id/{id}	Movie details
GET	/recommend/genre?tmdb_id=...	Genre suggestions
GET	/recommend/tfidf?title=...	TF-IDF suggestions
GET	/movie/search?query=...	Full recommendation bundle
GET	/analytics	Dataset statistics
POST	/collection/add	Add to watchlist / favorites
GET	/collection/list?kind=watchlist	List saved movies
DELETE	/collection/remove	Remove from collection
POST	/collection/toggle-watched	Mark watched / unwatched
🗄 Database (Watchlist + Favorites)
Single SQLite table collection with a kind column ('watchlist' | 'favorite').
See docs/05_DATABASE_SCHEMA.md.

⚠️ On Render's free tier, SQLite files are ephemeral. Add a persistent
disk (mount /var/data) and set DB_PATH=/var/data/movies.db to keep data
across restarts.

📖 Documentation
Full docs live in docs/:

Product Requirements

Technical Requirements

App Flow

Design Brief

Database Schema

Implementation Plan

📜 License
Educational / portfolio project.
Movie data, posters, and metadata are provided by TMDB and subject to TMDB's terms.

👨‍💻 Author
Kazi Sadman Zahin — CSE Student
GitHub: https://github.com/Kazi-Sadman
```
