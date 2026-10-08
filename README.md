# 🎬 Movie Recommendation System

A full-stack **Movie Recommendation System** built with **Python, FastAPI, Streamlit, Machine Learning, and the TMDB API**.

The system provides movie search, movie details, personalized recommendations, genre-based recommendations, and a modern Streamlit web interface. The machine learning recommendation engine uses **TF-IDF and cosine similarity** to find movies with similar content.

The application is deployed using **Render**, with the Streamlit frontend and FastAPI backend deployed as separate web services.

---

## 🌐 Live Demo

### 🎨 Frontend — Streamlit

👉 https://movie-recommendation-app-sfxg.onrender.com

### ⚡ Backend — FastAPI

👉 https://movie-recommendation-api-7910.onrender.com

### 📚 API Documentation

👉 https://movie-recommendation-api-7910.onrender.com/docs

---

# 📌 Project Overview

Finding a movie to watch can be difficult when there are thousands of available movies.

This project solves this problem by providing a movie recommendation platform where users can:

- 🔍 Search for movies
- 🎬 View movie details
- 🤖 Get similar movie recommendations
- 🎭 Get recommendations based on genre
- ⭐ View movie ratings and information
- 🖼️ Display movie posters using TMDB
- 🌐 Access the application through a web browser

The project follows a **frontend-backend architecture** where Streamlit handles the user interface and FastAPI provides the backend API.

---

# ✨ Features

## 🎨 Streamlit Frontend

The frontend provides an interactive user interface built with Streamlit.

### Features

- 🏠 Home page
- 🔍 Movie search
- 🎬 Movie details page
- 🤖 Movie recommendations
- 🎭 Genre-based recommendations
- 🖼️ TMDB movie posters
- 📱 Responsive movie grid
- ⚡ API-based communication with FastAPI
- 🔄 Dynamic navigation between pages

---

## ⚡ FastAPI Backend

The FastAPI backend provides REST API endpoints for the frontend.

It handles:

- Movie search
- Movie information
- Recommendation generation
- Genre-based recommendations
- TF-IDF similarity
- TMDB API communication
- Health checking

---

# 🤖 Recommendation System

The recommendation engine uses **content-based filtering**.

The main idea is:

```text
Movie Information
       │
       ▼
Text Processing
       │
       ▼
TF-IDF Vectorization
       │
       ▼
Movie Feature Vectors
       │
       ▼
Cosine Similarity
       │
       ▼
Similar Movies
```

### TF-IDF

TF-IDF (**Term Frequency-Inverse Document Frequency**) converts movie text information into numerical vectors.

Movies with similar descriptions, genres, keywords, or other textual information will have similar vector representations.

### Cosine Similarity

Cosine similarity is used to measure how similar two movie vectors are.

A higher cosine similarity means the movies are more similar.

---

# 🏗️ System Architecture

```text
                         USER
                          │
                          ▼
                ┌──────────────────┐
                │ Streamlit        │
                │ Frontend         │
                │                  │
                │ app.py           │
                └────────┬─────────┘
                         │
                         │ HTTP Requests
                         ▼
                ┌──────────────────┐
                │ FastAPI          │
                │ Backend          │
                │                  │
                │ main.py          │
                └────────┬─────────┘
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │ ML Recommendation│    │ TMDB API         │
    │ Engine           │    │                  │
    │                  │    │ Movie information│
    │ TF-IDF           │    │ Posters          │
    │ Cosine Similarity│    │ Ratings          │
    └──────────────────┘    └──────────────────┘
```

---

# 🔄 Application Flow

## Movie Search

```text
User
 │
 ▼
Streamlit Search
 │
 ▼
FastAPI
 │
 ▼
TMDB API
 │
 ▼
Movie Results
 │
 ▼
Streamlit UI
```

---

## Movie Recommendation

```text
User selects movie
        │
        ▼
Streamlit
        │
        ▼
FastAPI
        │
        ▼
TF-IDF Movie Vector
        │
        ▼
Cosine Similarity
        │
        ▼
Similar Movies
        │
        ▼
Streamlit
```

---

# 📂 Project Structure

```text
Movie-Recommendation-System/
│
├── data/
│   │
│   ├── processed/
│   │   ├── df.pkl
│   │   ├── indices.pkl
│   │   ├── tfidf.pkl
│   │   └── tfidf_matrix.pkl
│   │
│   └── raw/
│
├── notebooks/
│   └── movies.ipynb
│
├── app.py
├── main.py
├── requirements.txt
├── .python-version
├── .gitignore
└── README.md
```

---

# 📄 Main Files

| File / Folder      | Description                             |
| ------------------ | --------------------------------------- |
| `app.py`           | Streamlit frontend application          |
| `main.py`          | FastAPI backend and recommendation APIs |
| `movies.ipynb`     | Data analysis and ML model development  |
| `df.pkl`           | Processed movie dataset                 |
| `indices.pkl`      | Movie index mapping                     |
| `tfidf.pkl`        | Trained TF-IDF vectorizer               |
| `tfidf_matrix.pkl` | TF-IDF feature matrix                   |
| `requirements.txt` | Python dependencies                     |
| `.python-version`  | Python version configuration            |
| `.gitignore`       | Git ignored files                       |

---

# 🛠️ Technologies Used

## Programming Language

- Python 3.14.5

## Frontend

- Streamlit

## Backend

- FastAPI
- Uvicorn

## Machine Learning

- Scikit-learn
- TF-IDF
- Cosine Similarity
- Content-Based Filtering

## Data Processing

- Pandas
- NumPy
- SciPy

## External API

- TMDB API

## HTTP Communication

- Requests
- HTTPX

## Environment Management

- python-dotenv

## Deployment

- Render
- GitHub

---

# 📦 Python Dependencies

The project uses the following major dependencies:

```text
fastapi
uvicorn
streamlit
pandas
numpy
scikit-learn
scipy
requests
python-dotenv
httpx
```

---

# 🚀 Run the Project Locally

## 1. Clone the Repository

```bash
git clone https://github.com/Kazi-Sadman/Movie-Recommendation-System.git
```

Go to the project directory:

```bash
cd Movie-Recommendation-System
```

---

# 🐍 2. Create Virtual Environment

Windows:

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# 📥 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 4. Configure TMDB API

The backend requires a TMDB API key.

Create a `.env` file in the project root:

```text
TMDB_API_KEY=your_tmdb_api_key
```

The `.env` file should **not** be uploaded to GitHub.

It is already included in `.gitignore`.

---

# ⚡ 5. Run FastAPI Backend

Open a terminal and run:

```bash
uvicorn main:app --reload
```

The backend will normally run at:

```text
http://127.0.0.1:8000
```

### API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

### Health Check

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

# 🎨 6. Run Streamlit Frontend

Open another terminal.

Activate the virtual environment if necessary:

```bash
.venv\Scripts\activate
```

Then run:

```bash
streamlit run app.py
```

Streamlit will provide a local URL similar to:

```text
http://localhost:8501
```

Open the URL in your browser.

---

# 🔗 Frontend → Backend Configuration

For local development, the frontend can communicate with the local FastAPI server:

```text
http://127.0.0.1:8000
```

For production, the Streamlit frontend communicates with the deployed FastAPI backend:

```text
https://movie-recommendation-api-7910.onrender.com
```

The architecture is therefore:

```text
LOCAL

Streamlit
   │
   ▼
127.0.0.1:8000
   │
   ▼
FastAPI
```

Production:

```text
Internet User
      │
      ▼
Streamlit Frontend
      │
      ▼
FastAPI Backend
      │
      ▼
TMDB API
```

---

# 🔌 API Endpoints

The FastAPI backend provides several endpoints.

## Health Check

```http
GET /health
```

Used to check whether the backend is running.

---

## Home

```http
GET /home
```

Returns movie information used by the home page.

---

## TMDB Movie Search

```http
GET /tmdb/search
```

Searches movies using the TMDB API.

Example:

```text
/tmdb/search?query=Inception
```

---

## Movie Details

```http
GET /movie/id/{tmdb_id}
```

Returns details for a specific movie.

Example:

```text
/movie/id/27205
```

---

## Genre Recommendation

```http
GET /recommend/genre
```

Returns recommendations based on movie genre.

---

## TF-IDF Recommendation

```http
GET /recommend/tfidf
```

Returns recommendations using the content-based TF-IDF recommendation engine.

---

## Movie Search

```http
GET /movie/search
```

Searches the processed movie dataset.

---

# 📚 API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
https://movie-recommendation-api-7910.onrender.com/docs
```

### ReDoc

```text
https://movie-recommendation-api-7910.onrender.com/redoc
```

---

# ☁️ Deployment

The project is deployed on **Render**.

There are two separate web services.

## 1. FastAPI Backend

```text
Service:
movie-recommendation-api

URL:
https://movie-recommendation-api-7910.onrender.com
```

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 2. Streamlit Frontend

```text
Service:
movie-recommendation-app

URL:
https://movie-recommendation-app-sfxg.onrender.com
```

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

---

# 🔐 Environment Variables

The backend requires:

```text
TMDB_API_KEY
```

Example:

```text
TMDB_API_KEY=your_api_key
```

For production deployment, the API key should be stored in Render's **Environment Variables** instead of committing it to GitHub.

---

# 🧪 Testing

The application can be tested through:

### Backend Health

```text
/health
```

### Swagger API

```text
/docs
```

### Frontend

Open the Streamlit deployment URL and test:

- Movie search
- Movie details
- Recommendations
- Genre recommendations
- Posters
- Navigation

---

# ⚠️ Important Notes

## Render Free Instance

If the project is deployed using Render's free instance, the service may **sleep after a period of inactivity**.

The first request after inactivity may therefore take some time while the service starts again.

---

## Pickle Files

The recommendation system depends on preprocessed `.pkl` files:

```text
df.pkl
indices.pkl
tfidf.pkl
tfidf_matrix.pkl
```

These files are required by the FastAPI backend for the recommendation system.

---

# 🔮 Future Improvements

Possible future improvements include:

- ⭐ User-based personalized recommendations
- 👤 User accounts
- ❤️ Favorite movies
- 📜 Recommendation history
- 🎯 Personalized recommendation profiles
- 🧠 Hybrid recommendation system
- 🔥 Trending movie section
- 🎭 Better genre filtering
- 📊 Recommendation explanation
- 🗄️ Database integration
- 📱 Improved mobile UI
- ⚡ Recommendation caching
- 🔐 Authentication and authorization

---

# 🎯 Learning Objectives

This project demonstrates practical experience with:

- Machine Learning
- Natural Language Processing
- Recommendation Systems
- TF-IDF
- Cosine Similarity
- REST APIs
- FastAPI
- Streamlit
- API integration
- Data preprocessing
- Python backend development
- Frontend-backend communication
- Git and GitHub
- Cloud deployment
- Render deployment

---

# 👨‍💻 Author

**Kazi Sadman Zahin**

Computer Science & Engineering Student

### GitHub

https://github.com/Kazi-Sadman

---

# 📜 License

This project is developed for **educational and portfolio purposes**.

Movie data, posters, ratings, and related metadata are provided through the **TMDB API** and are subject to TMDB's terms and policies.

---

# ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

## 🚀 Live Application

### 🎬 Movie Recommendation System

**Frontend:**
https://movie-recommendation-app-sfxg.onrender.com

**Backend:**
https://movie-recommendation-api-7910.onrender.com

**API Documentation:**
https://movie-recommendation-api-7910.onrender.com/docs

---
