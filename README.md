# 🎬 Movie Recommender System

A movie recommendation web application built with **FastAPI**, **Streamlit**, **TF-IDF**, and the **TMDB API**.

The system provides movie search, movie details, popular/trending movie feeds, and two types of recommendations:

* 🔎 **TF-IDF-based Similar Movie Recommendation**
* 🎭 **Genre-based Movie Recommendation**

The application uses a **FastAPI backend** for API and recommendation logic and a **Streamlit frontend** for the user interface.

---

## 📌 Features

### 🏠 Home Feed

The application provides different movie categories:

* 🔥 Trending
* ⭐ Popular
* 🏆 Top Rated
* 🎬 Now Playing
* 📅 Upcoming

Users can change the number of movie columns from the sidebar.

### 🔍 Movie Search

Users can search movies using keywords such as:

```text
avengers
batman
love
spider
```

The application provides:

* Search suggestions
* Matching movie results
* Movie posters
* Release year
* TMDB movie ID

### 🎥 Movie Details

After selecting a movie, the application displays:

* Movie title
* Poster
* Backdrop
* Release date
* Genres
* Movie overview

### 🤖 TF-IDF Recommendation

The backend uses a pre-trained TF-IDF matrix to calculate similarity between movies.

The system returns movies that are textually similar to the selected movie.

### 🎭 Genre Recommendation

The application also uses the selected movie's first genre to retrieve popular movies from TMDB belonging to that genre.

### 🖼️ TMDB Integration

Movie information and posters are retrieved from:

**The Movie Database (TMDB)**

The application uses the TMDB API for:

* Movie search
* Movie details
* Posters
* Backdrops
* Trending movies
* Popular movies
* Top-rated movies
* Upcoming movies
* Now-playing movies
* Genre discovery

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Frontend  │
                    │      app.py         │
                    └──────────┬──────────┘
                               │ HTTP Requests
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    │      main.py        │
                    └───────┬───────┬─────┘
                            │       │
                 ┌──────────┘       └──────────┐
                 ▼                             ▼
       ┌──────────────────┐          ┌──────────────────┐
       │ Local ML Models  │          │    TMDB API      │
       │                  │          │                  │
       │ df.pkl           │          │ Search           │
       │ indices.pkl      │          │ Details          │
       │ tfidf.pkl        │          │ Posters          │
       │ tfidf_matrix.pkl │          │ Genres           │
       └──────────────────┘          └──────────────────┘
```

---

# 📂 Project Structure

Recommended project structure:

```text
Movie-Recommender/
│
├── app.py
├── main.py
│
├── df.pkl
├── indices.pkl
├── tfidf.pkl
├── tfidf_matrix.pkl
│
├── movies.ipynb
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### File Description

| File               | Description                                    |
| ------------------ | ---------------------------------------------- |
| `app.py`           | Streamlit frontend                             |
| `main.py`          | FastAPI backend                                |
| `movies.ipynb`     | Movie data processing and ML/model preparation |
| `df.pkl`           | Processed movie DataFrame                      |
| `indices.pkl`      | Movie title-to-index mapping                   |
| `tfidf.pkl`        | TF-IDF vectorizer                              |
| `tfidf_matrix.pkl` | Pre-computed TF-IDF matrix                     |
| `.env`             | TMDB API key                                   |
| `requirements.txt` | Python dependencies                            |
| `README.md`        | Project documentation                          |

---

# ⚙️ Technologies Used

### Frontend

* Python
* Streamlit
* Requests
* HTML/CSS

### Backend

* FastAPI
* Uvicorn
* Pydantic
* HTTPX
* Python-dotenv

### Machine Learning

* TF-IDF
* Cosine Similarity
* NumPy
* Pandas
* SciPy / Scikit-learn

### External API

* TMDB API

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Go inside the project:

```bash
cd Movie-Recommender
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

# 📦 3. Install Dependencies

Create a `requirements.txt` file containing:

```text
fastapi
uvicorn
streamlit
requests
httpx
python-dotenv
numpy
pandas
scikit-learn
scipy
pydantic
```

Then install:

```bash
pip install -r requirements.txt
```

---

# 🔑 4. Configure TMDB API Key

Create a file named:

```text
.env
```

Add:

```env
TMDB_API_KEY=YOUR_TMDB_API_KEY
```

Example:

```env
TMDB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

Do **not** upload your `.env` file to GitHub.

Add this to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
```

---

# 🧠 5. Required ML Files

The FastAPI backend loads four pickle files when the server starts:

```text
df.pkl
indices.pkl
tfidf_matrix.pkl
tfidf.pkl
```

Make sure these files are in the same directory as `main.py`.

```text
Movie-Recommender/
│
├── main.py
├── app.py
├── df.pkl
├── indices.pkl
├── tfidf_matrix.pkl
└── tfidf.pkl
```

If these files are missing, the backend will not be able to provide the TF-IDF recommendations.

---

# ▶️ Running the Application Locally

The project has **two parts**:

1. FastAPI backend
2. Streamlit frontend

You need to run both.

---

## 6. Start FastAPI Backend

Open Terminal 1:

```bash
uvicorn main:app --reload
```

The backend will normally run at:

```text
http://127.0.0.1:8000
```

You can test the health endpoint:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

### FastAPI Documentation

You can also open:

```text
http://127.0.0.1:8000/docs
```

This opens the interactive Swagger API documentation.

---

# ▶️ 7. Start Streamlit Frontend

Open a second terminal.

Activate the virtual environment if necessary:

```bash
venv\Scripts\activate
```

Then run:

```bash
streamlit run app.py
```

Streamlit will normally open:

```text
http://localhost:8501
```

If it does not automatically open, copy the URL into your browser.

---

# 🔗 Frontend → Backend Connection

For local development, `app.py` should use:

```python
API_BASE = "http://127.0.0.1:8000"
```

For a deployed backend, use the deployed FastAPI URL:

```python
API_BASE = "https://movie-rec-466x.onrender.com"
```

### Important

Do **not** write:

```python
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
```

because Python will always select the first URL.

---

# 🔌 API Endpoints

The FastAPI backend provides the following endpoints.

## Health Check

```http
GET /health
```

Example:

```text
http://127.0.0.1:8000/health
```

---

## Home Movies

```http
GET /home
```

Parameters:

```text
category
limit
```

Supported categories:

```text
trending
popular
top_rated
upcoming
now_playing
```

Example:

```text
/home?category=popular&limit=24
```

---

## TMDB Movie Search

```http
GET /tmdb/search
```

Example:

```text
/tmdb/search?query=batman
```

This returns multiple TMDB search results.

---

## Movie Details

```http
GET /movie/id/{tmdb_id}
```

Example:

```text
/movie/id/550
```

This returns:

* Movie title
* Overview
* Release date
* Poster
* Backdrop
* Genres

---

## Genre Recommendations

```http
GET /recommend/genre
```

Example:

```text
/recommend/genre?tmdb_id=550&limit=18
```

The backend gets the movie's genre and finds popular movies from that genre.

---

## TF-IDF Recommendations

```http
GET /recommend/tfidf
```

Example:

```text
/recommend/tfidf?title=Avatar&top_n=10
```

This uses the local TF-IDF matrix to calculate similar movies.

---

## Complete Movie Search

```http
GET /movie/search
```

Example:

```text
/movie/search?query=Avatar
```

This endpoint combines:

```text
Movie Details
      +
TF-IDF Recommendations
      +
Genre Recommendations
```

The Streamlit application uses this endpoint to display recommendations on the movie details page.

---

# 🧠 Recommendation Workflow

When the user selects a movie:

```text
User selects movie
        │
        ▼
Get TMDB movie details
        │
        ├───────────────┐
        │               │
        ▼               ▼
   TF-IDF Model      TMDB Genre
        │               │
        ▼               ▼
Similar Movies      Genre Movies
        │               │
        └───────┬───────┘
                ▼
       Streamlit UI
```

### TF-IDF

The local TF-IDF matrix is used to calculate similarity between movies.

Conceptually:

```text
Movie A
   │
   ▼
TF-IDF Vector
   │
   ▼
Cosine Similarity
   │
   ▼
Top Similar Movies
```

### Genre Recommendation

```text
Selected Movie
      │
      ▼
TMDB Movie Details
      │
      ▼
First Genre
      │
      ▼
TMDB Discover API
      │
      ▼
Popular Movies in Genre
```

---

# 🌐 Deployment

The application can be deployed as two services.

### Backend

Deploy the FastAPI application using a service such as Render.

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Set the environment variable:

```text
TMDB_API_KEY=your_api_key
```

Make sure the following files are available to the backend:

```text
main.py
df.pkl
indices.pkl
tfidf.pkl
tfidf_matrix.pkl
```

### Frontend

Deploy `app.py` using Streamlit Community Cloud or another Streamlit-compatible platform.

Update:

```python
API_BASE = "https://YOUR-BACKEND-URL"
```

For example:

```python
API_BASE = "https://movie-rec-466x.onrender.com"
```

---

# 🔐 Security

Never commit your TMDB API key.

Add:

```text
.env
```

to `.gitignore`.

Example `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
```

If the API key has already been uploaded to GitHub, regenerate/revoke the key from TMDB and replace it with a new one.

---

# 🛠️ Troubleshooting

## `TMDB_API_KEY missing`

Error:

```text
TMDB_API_KEY missing
```

Solution:

Create `.env`:

```env
TMDB_API_KEY=your_key_here
```

Then restart FastAPI.

---

## `Connection refused`

If Streamlit shows:

```text
Request failed
```

make sure FastAPI is running:

```bash
uvicorn main:app --reload
```

Then check:

```text
http://127.0.0.1:8000/health
```

---

## TF-IDF resources not loaded

Make sure these files exist:

```text
df.pkl
indices.pkl
tfidf_matrix.pkl
tfidf.pkl
```

and are located beside `main.py`.

---

## Movie search works but recommendations don't

Check:

1. `df.pkl` contains a `title` column.
2. `indices.pkl` contains the movie title-to-index mapping.
3. `tfidf_matrix.pkl` is available.
4. The selected movie title exists in the local dataset.
5. FastAPI is running without startup errors.

---

# 📸 Application Flow

```text
                    HOME
                      │
          ┌───────────┴───────────┐
          │                       │
       Search                 Home Feed
          │                       │
          ▼                       ▼
    Movie Suggestions      Popular/Trending/etc.
          │
          ▼
    Select Movie
          │
          ▼
    Movie Details
          │
          ├───────────────┐
          │               │
          ▼               ▼
   TF-IDF Similarity   Genre Based
          │               │
          ▼               ▼
   Similar Movies     More Like This
```

---

# 👨‍💻 Project Purpose

This project demonstrates how a movie recommendation system can combine:

* Machine Learning
* Natural Language Processing
* TF-IDF
* Cosine Similarity
* REST APIs
* FastAPI
* Streamlit
* External API integration
* Pre-trained ML artifacts
* Interactive web interfaces

The architecture separates the **frontend** and **backend**, making the recommendation system easier to deploy and maintain.

---

# 📜 License

This project is developed for educational and academic purposes.

Movie metadata, images, and related information are provided through the TMDB API.

---

# 🙏 Acknowledgements

* **TMDB** — Movie metadata, posters, and movie information
* **FastAPI** — Backend API framework
* **Streamlit** — Interactive frontend
* **Scikit-learn** — TF-IDF and machine learning utilities
* **Pandas / NumPy** — Data processing
* **SciPy** — Sparse matrix processing
