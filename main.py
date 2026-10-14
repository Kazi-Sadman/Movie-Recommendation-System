"""
FastAPI backend for the Movie Recommendation System.

Endpoints:
- TMDB proxy:      /home, /tmdb/search, /movie/id/{id}
- Recommendations: /recommend/genre, /recommend/tfidf, /movie/search
- Analytics:       /analytics
- Collection:      /collection/add, /collection/list, /collection/remove, /collection/toggle-watched
"""

import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import database

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG_500 = "https://image.tmdb.org/t/p/w500"
TMDB_IMG_1280 = "https://image.tmdb.org/t/p/w1280"

app = FastAPI(title="Movie Recommender API", version="3.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Load TF-IDF files (df, indices, matrix, vectorizer)
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

df = None
indices_obj = None
tfidf_matrix = None
tfidf_obj = None
TITLE_TO_IDX: Dict[str, int] = {}


def load_recommender_files():
    """Load the pickle files. If any are missing, recommendations are disabled."""
    global df, indices_obj, tfidf_matrix, tfidf_obj, TITLE_TO_IDX

    required = [
        PROCESSED_DIR / "df.pkl",
        PROCESSED_DIR / "indices.pkl",
        PROCESSED_DIR / "tfidf_matrix.pkl",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("TF-IDF files not found:", missing)
        return

    try:
        with (PROCESSED_DIR / "df.pkl").open("rb") as f:
            df = pickle.load(f)
        with (PROCESSED_DIR / "indices.pkl").open("rb") as f:
            indices_obj = pickle.load(f)
        with (PROCESSED_DIR / "tfidf_matrix.pkl").open("rb") as f:
            tfidf_matrix = pickle.load(f)

        tfidf_path = PROCESSED_DIR / "tfidf.pkl"
        if tfidf_path.exists():
            with tfidf_path.open("rb") as f:
                tfidf_obj = pickle.load(f)

        if not isinstance(df, pd.DataFrame) or "title" not in df.columns:
            raise RuntimeError("df.pkl must contain a DataFrame with a 'title' column.")

        TITLE_TO_IDX = {
            str(k).strip().lower(): int(v)
            for k, v in indices_obj.items()
        }
        print(f"Loaded TF-IDF resources: {len(df)} movies.")
    except Exception as e:
        df = None
        tfidf_matrix = None
        TITLE_TO_IDX = {}
        print(f"Could not load TF-IDF resources: {e}")


@app.on_event("startup")
def on_startup():
    load_recommender_files()
    database.init_db()
    print("Database ready.")


# ------------------------------------------------------------------
# Pydantic models (shape of API responses)
# ------------------------------------------------------------------
class MovieCard(BaseModel):
    tmdb_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None


class MovieDetails(BaseModel):
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    genres: List[dict] = Field(default_factory=list)
    runtime: Optional[int] = None
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    tagline: Optional[str] = None
    status: Optional[str] = None


class TFIDFItem(BaseModel):
    title: str
    score: float
    tmdb: Optional[MovieCard] = None


class SearchBundle(BaseModel):
    query: str
    movie_details: MovieDetails
    tfidf_recommendations: List[TFIDFItem]
    genre_recommendations: List[MovieCard]


class CollectionItem(BaseModel):
    tmdb_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    kind: str
    watched: bool = False


# ------------------------------------------------------------------
# TMDB helpers
# ------------------------------------------------------------------
def img_url(path):
    return f"{TMDB_IMG_500}{path}" if path else None


async def tmdb_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call the TMDB API. Throws a clear error if the key is missing."""
    if not TMDB_API_KEY:
        raise HTTPException(500, "TMDB_API_KEY is not set in the environment.")

    params = dict(params or {})
    params["api_key"] = TMDB_API_KEY

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(f"{TMDB_BASE}{path}", params=params)
    except httpx.RequestError as e:
        raise HTTPException(502, f"Could not connect to TMDB: {e}")

    if r.status_code != 200:
        raise HTTPException(502, f"TMDB returned HTTP {r.status_code}")

    return r.json()


def cards_from_tmdb(results: List[dict], limit: int = 20) -> List[MovieCard]:
    """Convert raw TMDB results into our MovieCard format."""
    cards = []
    for m in (results or [])[:limit]:
        if not m.get("id"):
            continue
        cards.append(MovieCard(
            tmdb_id=int(m["id"]),
            title=m.get("title") or m.get("name") or "Untitled",
            poster_url=img_url(m.get("poster_path")),
            release_date=m.get("release_date") or m.get("first_air_date"),
            vote_average=m.get("vote_average"),
        ))
    return cards


async def tmdb_movie_details(movie_id: int) -> MovieDetails:
    data = await tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})
    return MovieDetails(
        tmdb_id=int(data["id"]),
        title=data.get("title") or "",
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=img_url(data.get("poster_path")),
        backdrop_url=f"{TMDB_IMG_1280}{data['backdrop_path']}" if data.get("backdrop_path") else None,
        genres=data.get("genres") or [],
        runtime=data.get("runtime"),
        popularity=data.get("popularity"),
        vote_average=data.get("vote_average"),
        vote_count=data.get("vote_count"),
        tagline=data.get("tagline"),
        status=data.get("status"),
    )


async def tmdb_search_first(query: str) -> Optional[dict]:
    data = await tmdb_get("/search/movie", {
        "query": query, "include_adult": "false", "language": "en-US", "page": 1,
    })
    results = data.get("results") or []
    return results[0] if results else None


# ------------------------------------------------------------------
# TF-IDF recommendation
# ------------------------------------------------------------------
def tfidf_recommend(title: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """Return (title, score) pairs from the local dataset."""
    if df is None or tfidf_matrix is None or not TITLE_TO_IDX:
        return []

    idx = TITLE_TO_IDX.get(title.strip().lower())
    if idx is None or idx < 0 or idx >= len(df):
        return []

    try:
        scores = (tfidf_matrix @ tfidf_matrix[idx].T).toarray().ravel()
    except Exception as e:
        print("TF-IDF failed:", e)
        return []

    order = np.argsort(-scores)
    out = []
    for i in order:
        i = int(i)
        if i == idx or i >= len(df):
            continue
        out.append((str(df.iloc[i]["title"]), float(scores[i])))
        if len(out) >= top_n:
            break
    return out


async def attach_card(title: str) -> Optional[MovieCard]:
    """Look up a TMDB card for a recommendation title."""
    try:
        m = await tmdb_search_first(title)
        if not m:
            return None
        return MovieCard(
            tmdb_id=int(m["id"]),
            title=m.get("title") or title,
            poster_url=img_url(m.get("poster_path")),
            release_date=m.get("release_date"),
            vote_average=m.get("vote_average"),
        )
    except HTTPException:
        return None


async def genre_recommendations(tmdb_id: int, limit: int = 18) -> List[MovieCard]:
    details = await tmdb_movie_details(tmdb_id)
    if not details.genres:
        return []
    genre_id = details.genres[0]["id"]
    data = await tmdb_get("/discover/movie", {
        "with_genres": genre_id,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": 1,
    })
    cards = cards_from_tmdb(data.get("results") or [], limit)
    return [c for c in cards if c.tmdb_id != tmdb_id]


# ------------------------------------------------------------------
# Basic routes
# ------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Movie Recommender API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------------------------------
# Home feed
# ------------------------------------------------------------------
async def get_home(category: str, limit: int) -> List[MovieCard]:
    if category == "trending":
        data = await tmdb_get("/trending/movie/day", {"language": "en-US"})
    elif category in {"popular", "top_rated", "upcoming", "now_playing"}:
        data = await tmdb_get(f"/movie/{category}", {"language": "en-US", "page": 1})
    else:
        raise HTTPException(400, "Invalid category.")
    return cards_from_tmdb(data.get("results") or [], limit)


@app.get("/home", response_model=List[MovieCard])
async def home(category: str = Query("popular"), limit: int = Query(24, ge=1, le=50)):
    return await get_home(category, limit)


@app.get("/movies/{category}", response_model=List[MovieCard], include_in_schema=False)
async def legacy_home(category: str, limit: int = Query(24, ge=1, le=50)):
    return await get_home(category, limit)


# ------------------------------------------------------------------
# Search
# ------------------------------------------------------------------
@app.get("/tmdb/search")
async def tmdb_search(query: str = Query(..., min_length=1), page: int = Query(1, ge=1, le=10)):
    return await tmdb_get("/search/movie", {
        "query": query.strip(), "include_adult": "false",
        "language": "en-US", "page": page,
    })


# ------------------------------------------------------------------
# Movie details
# ------------------------------------------------------------------
@app.get("/movie/id/{tmdb_id}", response_model=MovieDetails)
@app.get("/movies/id/{tmdb_id}", response_model=MovieDetails, include_in_schema=False)
@app.get("/movies/{tmdb_id}", response_model=MovieDetails, include_in_schema=False)
async def movie_details(tmdb_id: int):
    return await tmdb_movie_details(tmdb_id)


# ------------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------------
@app.get("/recommend/genre", response_model=List[MovieCard])
async def recommend_genre(tmdb_id: int = Query(...), limit: int = Query(18, ge=1, le=50)):
    return await genre_recommendations(tmdb_id, limit)


@app.get("/recommend/tfidf")
async def recommend_tfidf(title: str = Query(..., min_length=1), top_n: int = Query(10, ge=1, le=50)):
    return [{"title": t, "score": s} for t, s in tfidf_recommend(title, top_n)]


@app.get("/movie/search", response_model=SearchBundle)
async def search_bundle(
    query: str = Query(..., min_length=1),
    tfidf_top_n: int = Query(12, ge=1, le=30),
    genre_limit: int = Query(12, ge=1, le=30),
):
    best = await tmdb_search_first(query.strip())
    if not best:
        raise HTTPException(404, f"No TMDB movie found for: {query}")

    details = await tmdb_movie_details(int(best["id"]))

    tfidf_items = []
    for title, score in tfidf_recommend(details.title, tfidf_top_n):
        tfidf_items.append(TFIDFItem(
            title=title, score=score, tmdb=await attach_card(title),
        ))

    genre_recs = await genre_recommendations(details.tmdb_id, genre_limit)

    return SearchBundle(
        query=query,
        movie_details=details,
        tfidf_recommendations=tfidf_items,
        genre_recommendations=genre_recs,
    )


# ------------------------------------------------------------------
# Analytics
# ------------------------------------------------------------------
@app.get("/analytics")
def analytics():
    """Dataset statistics — used by the Movie Analytics page."""
    if df is None:
        raise HTTPException(503, "Dataset not loaded. Make sure the .pkl files exist.")

    # Top genres
    top_genres = []
    if "genres" in df.columns:
        counts = {}
        for value in df["genres"].fillna(""):
            for g in str(value).split():
                counts[g] = counts.get(g, 0) + 1
        top_genres = sorted(counts.items(), key=lambda x: -x[1])[:20]

    # Rating histogram
    rating_hist = []
    if "vote_average" in df.columns:
        values = pd.to_numeric(df["vote_average"], errors="coerce").dropna()
        bins = [0, 2, 4, 6, 8, 10]
        labels = ["0-2", "2-4", "4-6", "6-8", "8-10"]
        cut = pd.cut(values, bins=bins, labels=labels, include_lowest=True)
        counts = cut.value_counts().reindex(labels).fillna(0)
        rating_hist = [{"range": str(lbl), "count": int(c)} for lbl, c in counts.items()]

    # Top popular
    top_popular = []
    if {"title", "popularity"}.issubset(df.columns):
        pop = df[["title", "popularity"]].copy()
        pop["popularity"] = pd.to_numeric(pop["popularity"], errors="coerce")
        pop = pop.dropna().sort_values("popularity", ascending=False).head(10)
        top_popular = [
            {"title": str(row["title"]), "popularity": float(row["popularity"])}
            for _, row in pop.iterrows()
        ]

    # Missing values
    missing = {col: int(df[col].isna().sum()) for col in df.columns}

    # TF-IDF vocabulary size
    vocab_size = 0
    if tfidf_obj is not None and hasattr(tfidf_obj, "vocabulary_"):
        vocab_size = len(tfidf_obj.vocabulary_)

    return {
        "total_movies": int(len(df)),
        "columns": list(df.columns),
        "missing_values": missing,
        "top_genres": [{"genre": g, "count": c} for g, c in top_genres],
        "rating_histogram": rating_hist,
        "top_popular": top_popular,
        "tfidf_vocab_size": vocab_size,
    }


# ------------------------------------------------------------------
# Watchlist + Favorites
# ------------------------------------------------------------------
@app.post("/collection/add", response_model=CollectionItem)
def collection_add(item: CollectionItem):
    if item.kind not in {"watchlist", "favorite"}:
        raise HTTPException(400, "kind must be 'watchlist' or 'favorite'")
    database.add_item(
        item.tmdb_id, item.title, item.poster_url,
        item.release_date, item.vote_average, item.kind,
    )
    return item


@app.get("/collection/list", response_model=List[CollectionItem])
def collection_list(kind: str = Query(..., pattern="^(watchlist|favorite)$")):
    rows = database.list_items(kind)
    return [
        CollectionItem(
            tmdb_id=r["tmdb_id"],
            title=r["title"],
            poster_url=r.get("poster_url"),
            release_date=r.get("release_date"),
            vote_average=r.get("vote_average"),
            kind=r["kind"],
            watched=bool(r.get("watched", 0)),
        )
        for r in rows
    ]


@app.delete("/collection/remove")
def collection_remove(tmdb_id: int, kind: str = Query(..., pattern="^(watchlist|favorite)$")):
    return {"removed": database.remove_item(tmdb_id, kind)}


@app.post("/collection/toggle-watched")
def collection_toggle_watched(tmdb_id: int):
    result = database.toggle_watched(tmdb_id)
    if result is None:
        raise HTTPException(404, "Movie not in watchlist")
    return result