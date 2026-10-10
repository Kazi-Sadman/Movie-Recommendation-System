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

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG_500 = "https://image.tmdb.org/t/p/w500"

app = FastAPI(title="Movie Recommender API", version="3.1")

# Streamlit calls this API server-to-server; CORS is retained for browser-based clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DF_PATH = PROCESSED_DIR / "df.pkl"
INDICES_PATH = PROCESSED_DIR / "indices.pkl"
TFIDF_MATRIX_PATH = PROCESSED_DIR / "tfidf_matrix.pkl"
TFIDF_PATH = PROCESSED_DIR / "tfidf.pkl"

df: Optional[pd.DataFrame] = None
indices_obj: Any = None
tfidf_matrix: Any = None
tfidf_obj: Any = None
TITLE_TO_IDX: Dict[str, int] = {}


class TMDBMovieCard(BaseModel):
    tmdb_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None


class TMDBMovieDetails(BaseModel):
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    genres: List[dict] = Field(default_factory=list)


class TFIDFRecItem(BaseModel):
    title: str
    score: float
    tmdb: Optional[TMDBMovieCard] = None


class SearchBundleResponse(BaseModel):
    query: str
    movie_details: TMDBMovieDetails
    tfidf_recommendations: List[TFIDFRecItem]
    genre_recommendations: List[TMDBMovieCard]


def norm_title(title: str) -> str:
    return str(title).strip().lower()


def make_img_url(path: Optional[str]) -> Optional[str]:
    return f"{TMDB_IMG_500}{path}" if path else None


async def tmdb_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="TMDB_API_KEY is not configured in the backend Render environment.",
        )

    query_params = dict(params or {})
    query_params["api_key"] = TMDB_API_KEY

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{TMDB_BASE}{path}", params=query_params)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Could not connect to TMDB: {exc}") from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB returned HTTP {response.status_code}: {response.text[:500]}",
        )

    return response.json()


def cards_from_results(results: List[dict], limit: int = 20) -> List[TMDBMovieCard]:
    cards: List[TMDBMovieCard] = []
    for movie in (results or [])[:limit]:
        if not movie.get("id"):
            continue
        cards.append(
            TMDBMovieCard(
                tmdb_id=int(movie["id"]),
                title=movie.get("title") or movie.get("name") or "Untitled",
                poster_url=make_img_url(movie.get("poster_path")),
                release_date=movie.get("release_date") or movie.get("first_air_date"),
                vote_average=movie.get("vote_average"),
            )
        )
    return cards


async def tmdb_movie_details(movie_id: int) -> TMDBMovieDetails:
    data = await tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})
    return TMDBMovieDetails(
        tmdb_id=int(data["id"]),
        title=data.get("title") or "",
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=make_img_url(data.get("poster_path")),
        backdrop_url=(
            f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}"
            if data.get("backdrop_path")
            else None
        ),
        genres=data.get("genres") or [],
    )


async def tmdb_search_movies(query: str, page: int = 1) -> Dict[str, Any]:
    return await tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        },
    )


async def tmdb_search_first(query: str) -> Optional[dict]:
    data = await tmdb_search_movies(query, 1)
    results = data.get("results") or []
    return results[0] if results else None


def build_title_to_idx_map(indices: Any) -> Dict[str, int]:
    if not hasattr(indices, "items"):
        raise RuntimeError("indices.pkl must contain a dictionary or pandas Series.")
    return {norm_title(key): int(value) for key, value in indices.items()}


def load_recommender_files() -> None:
    """Load local TF-IDF assets. API home/search/details still work if these are absent."""
    global df, indices_obj, tfidf_matrix, tfidf_obj, TITLE_TO_IDX

    required = [DF_PATH, INDICES_PATH, TFIDF_MATRIX_PATH]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("TF-IDF files not found; local recommendations will be disabled:", missing)
        return

    try:
        with DF_PATH.open("rb") as file:
            df = pickle.load(file)
        with INDICES_PATH.open("rb") as file:
            indices_obj = pickle.load(file)
        with TFIDF_MATRIX_PATH.open("rb") as file:
            tfidf_matrix = pickle.load(file)

        if TFIDF_PATH.exists():
            with TFIDF_PATH.open("rb") as file:
                tfidf_obj = pickle.load(file)

        if not isinstance(df, pd.DataFrame) or "title" not in df.columns:
            raise RuntimeError("df.pkl must contain a pandas DataFrame with a 'title' column.")

        TITLE_TO_IDX = build_title_to_idx_map(indices_obj)
        print(f"Loaded TF-IDF resources: {len(df)} movies.")
    except Exception as exc:
        df = None
        tfidf_matrix = None
        TITLE_TO_IDX = {}
        print(f"Could not load TF-IDF resources; local recommendations disabled: {exc}")


@app.on_event("startup")
def startup_event() -> None:
    load_recommender_files()


def tfidf_recommend_titles(query_title: str, top_n: int = 10) -> List[Tuple[str, float]]:
    if df is None or tfidf_matrix is None or not TITLE_TO_IDX:
        return []

    idx = TITLE_TO_IDX.get(norm_title(query_title))
    if idx is None:
        return []

    if idx < 0 or idx >= len(df):
        return []

    try:
        query_vector = tfidf_matrix[idx]
        scores = (tfidf_matrix @ query_vector.T).toarray().ravel()
    except Exception as exc:
        print(f"TF-IDF calculation failed: {exc}")
        return []

    order = np.argsort(-scores)
    recommendations: List[Tuple[str, float]] = []
    for item_idx in order:
        item_idx = int(item_idx)
        if item_idx == idx or item_idx >= len(df):
            continue
        title = str(df.iloc[item_idx]["title"])
        recommendations.append((title, float(scores[item_idx])))
        if len(recommendations) >= top_n:
            break
    return recommendations


async def attach_tmdb_card_by_title(title: str) -> Optional[TMDBMovieCard]:
    try:
        movie = await tmdb_search_first(title)
        if not movie:
            return None
        return TMDBMovieCard(
            tmdb_id=int(movie["id"]),
            title=movie.get("title") or title,
            poster_url=make_img_url(movie.get("poster_path")),
            release_date=movie.get("release_date"),
            vote_average=movie.get("vote_average"),
        )
    except HTTPException:
        return None


async def genre_recommendations(tmdb_id: int, limit: int = 18) -> List[TMDBMovieCard]:
    details = await tmdb_movie_details(tmdb_id)
    if not details.genres:
        return []
    genre_id = details.genres[0]["id"]
    data = await tmdb_get(
        "/discover/movie",
        {
            "with_genres": genre_id,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": 1,
        },
    )
    return [
        card for card in cards_from_results(data.get("results") or [], limit)
        if card.tmdb_id != tmdb_id
    ]


@app.get("/")
def root() -> dict:
    return {
        "message": "Movie Recommender API is running",
        "docs": "/docs",
        "health": "/health",
        "home": "/home?category=trending",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


async def get_home_movies(category: str, limit: int) -> List[TMDBMovieCard]:
    if category == "trending":
        data = await tmdb_get("/trending/movie/day", {"language": "en-US"})
    elif category in {"popular", "top_rated", "upcoming", "now_playing"}:
        data = await tmdb_get(f"/movie/{category}", {"language": "en-US", "page": 1})
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid category. Use trending, popular, top_rated, upcoming, or now_playing.",
        )
    return cards_from_results(data.get("results") or [], limit)


@app.get("/home", response_model=List[TMDBMovieCard])
async def home(
    category: str = Query("popular"),
    limit: int = Query(24, ge=1, le=50),
) -> List[TMDBMovieCard]:
    return await get_home_movies(category, limit)


# Backward compatibility for older frontend deployments calling /movies/trending.
@app.get("/movies/{category}", response_model=List[TMDBMovieCard], include_in_schema=False)
async def legacy_home(
    category: str,
    limit: int = Query(24, ge=1, le=50),
) -> List[TMDBMovieCard]:
    return await get_home_movies(category, limit)


@app.get("/tmdb/search")
async def tmdb_search(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=10),
) -> Dict[str, Any]:
    return await tmdb_search_movies(query.strip(), page)


@app.get("/movie/id/{tmdb_id}", response_model=TMDBMovieDetails)
@app.get("/movies/id/{tmdb_id}", response_model=TMDBMovieDetails, include_in_schema=False)
@app.get("/movies/{tmdb_id}", response_model=TMDBMovieDetails, include_in_schema=False)
async def movie_details_route(tmdb_id: int) -> TMDBMovieDetails:
    return await tmdb_movie_details(tmdb_id)


@app.get("/recommend/genre", response_model=List[TMDBMovieCard])
async def recommend_genre(
    tmdb_id: int = Query(...),
    limit: int = Query(18, ge=1, le=50),
) -> List[TMDBMovieCard]:
    return await genre_recommendations(tmdb_id, limit)


@app.get("/recommend/tfidf")
async def recommend_tfidf(
    title: str = Query(..., min_length=1),
    top_n: int = Query(10, ge=1, le=50),
) -> List[dict]:
    return [{"title": title, "score": score} for title, score in tfidf_recommend_titles(title, top_n)]


@app.get("/movie/search", response_model=SearchBundleResponse)
async def search_bundle(
    query: str = Query(..., min_length=1),
    tfidf_top_n: int = Query(12, ge=1, le=30),
    genre_limit: int = Query(12, ge=1, le=30),
) -> SearchBundleResponse:
    best = await tmdb_search_first(query.strip())
    if not best:
        raise HTTPException(status_code=404, detail=f"No TMDB movie found for query: {query}")

    details = await tmdb_movie_details(int(best["id"]))
    tfidf_items: List[TFIDFRecItem] = []
    for title, score in tfidf_recommend_titles(details.title, tfidf_top_n):
        tfidf_items.append(
            TFIDFRecItem(
                title=title,
                score=score,
                tmdb=await attach_tmdb_card_by_title(title),
            )
        )

    genre_recs = await genre_recommendations(details.tmdb_id, genre_limit)
    return SearchBundleResponse(
        query=query,
        movie_details=details,
        tfidf_recommendations=tfidf_items,
        genre_recommendations=genre_recs,
    )
