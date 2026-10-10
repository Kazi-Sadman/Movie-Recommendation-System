import os
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st

# Set this to your deployed FastAPI backend URL in Render.
API_BASE = os.getenv(
    "API_BASE",
    "https://movie-recommendation-api-7910.onrender.com",
).rstrip("/")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
    .small-muted { color: #6b7280; font-size: 0.92rem; }
    .movie-title { font-size: 0.9rem; line-height: 1.2rem; min-height: 2.4rem; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "selected_title" not in st.session_state:
    st.session_state.selected_title = ""

# Restore view from query parameters when a shared details URL is opened.
query_view = st.query_params.get("view")
query_id = st.query_params.get("id")
if query_view in {"home", "details"}:
    st.session_state.view = query_view
if query_id:
    try:
        st.session_state.selected_tmdb_id = int(query_id)
        st.session_state.view = "details"
    except (TypeError, ValueError):
        pass


def goto_home() -> None:
    st.session_state.view = "home"
    st.session_state.selected_tmdb_id = None
    st.session_state.selected_title = ""
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int, title: str = "") -> None:
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.session_state.selected_title = title
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


@st.cache_data(ttl=60, show_spinner=False)
def api_get_json(path: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Any, Optional[str]]:
    try:
        response = requests.get(f"{API_BASE}{path}", params=params, timeout=60)
        if response.status_code >= 400:
            return None, f"HTTP {response.status_code}: {response.text[:400]}"
        return response.json(), None
    except requests.RequestException as exc:
        return None, f"Request failed: {exc}"
    except ValueError:
        return None, "Backend returned a response that is not valid JSON."


def parse_search_results(data: Any, keyword: str, limit: int = 24) -> Tuple[List[Tuple[str, int]], List[dict]]:
    if not isinstance(data, dict):
        return [], []

    raw_results = data.get("results") or []
    cards: List[dict] = []
    for movie in raw_results:
        movie_id = movie.get("id")
        title = (movie.get("title") or "").strip()
        if not movie_id or not title:
            continue
        release_date = movie.get("release_date") or ""
        cards.append(
            {
                "tmdb_id": int(movie_id),
                "title": title,
                "poster_url": f"{TMDB_IMG}{movie['poster_path']}" if movie.get("poster_path") else None,
                "release_date": release_date,
                "vote_average": movie.get("vote_average"),
            }
        )

    keyword_lower = keyword.strip().lower()
    matched = [movie for movie in cards if keyword_lower in movie["title"].lower()]
    displayed = (matched or cards)[:limit]

    suggestions: List[Tuple[str, int]] = []
    for movie in displayed[:10]:
        year = (movie.get("release_date") or "")[:4]
        label = f"{movie['title']} ({year})" if year else movie["title"]
        suggestions.append((label, movie["tmdb_id"]))

    return suggestions, displayed


def poster_grid(cards: List[dict], cols: int = 6, key_prefix: str = "movie") -> None:
    if not cards:
        st.info("No movies to show.")
        return

    for start in range(0, len(cards), cols):
        columns = st.columns(cols)
        for column, movie in zip(columns, cards[start:start + cols]):
            with column:
                poster = movie.get("poster_url")
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("🖼️ *No poster available*")

                title = movie.get("title") or "Untitled"
                st.markdown(
                    f"<div class='movie-title'><b>{title}</b></div>",
                    unsafe_allow_html=True,
                )
                rating = movie.get("vote_average")
                if rating is not None:
                    st.caption(f"⭐ {float(rating):.1f}/10")

                movie_id = movie.get("tmdb_id") or movie.get("id")
                if movie_id and st.button("Open", key=f"{key_prefix}_{movie_id}_{start}"):
                    goto_details(int(movie_id), title)


def card_list_from_api(data: Any) -> List[dict]:
    """Normalize the backend's movie-card response to the frontend's card shape."""
    if not isinstance(data, list):
        return []
    normalized = []
    for item in data:
        movie_id = item.get("tmdb_id") or item.get("id")
        if not movie_id:
            continue
        normalized.append(
            {
                "tmdb_id": int(movie_id),
                "title": item.get("title") or "Untitled",
                "poster_url": item.get("poster_url")
                or (f"{TMDB_IMG}{item['poster_path']}" if item.get("poster_path") else None),
                "release_date": item.get("release_date"),
                "vote_average": item.get("vote_average"),
            }
        )
    return normalized


with st.sidebar:
    st.markdown("## 🎬 Menu")
    if st.button("🏠 Home", use_container_width=True):
        goto_home()

    st.divider()
    st.markdown("### Home Feed")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", min_value=2, max_value=8, value=6)
    st.caption("Backend API")
    st.code(API_BASE, language="text")

st.title("🎬 Movie Recommender")
st.markdown(
    "<div class='small-muted'>Type a keyword → choose a movie → explore details and recommendations.</div>",
    unsafe_allow_html=True,
)
st.divider()

if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title",
        placeholder="Type a movie name, e.g. Avengers, Batman, Interstellar...",
    )
    st.divider()

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters to search.")
        else:
            with st.spinner("Searching movies..."):
                search_data, search_error = api_get_json(
                    "/tmdb/search",
                    {"query": typed.strip(), "page": 1},
                )

            if search_error:
                st.error(f"Search failed: {search_error}")
            else:
                suggestions, search_cards = parse_search_results(search_data, typed, limit=24)
                if suggestions:
                    labels = ["-- Select a movie --"] + [label for label, _ in suggestions]
                    selected_label = st.selectbox("Suggestions", labels, index=0)
                    if selected_label != "-- Select a movie --":
                        selected_map = dict(suggestions)
                        chosen_id = selected_map.get(selected_label)
                        if chosen_id:
                            goto_details(chosen_id, selected_label)

                st.markdown("### 🔍 Matching Results")
                poster_grid(search_cards, cols=grid_cols, key_prefix="search")
                if not search_cards:
                    st.info("No matching movies found.")
    else:
        st.markdown(f"### 🏠 Home — {home_category.replace('_', ' ').title()}")
        with st.spinner("Loading movies..."):
            feed_data, feed_error = api_get_json(
                "/home",
                {"category": home_category, "limit": 24},
            )

        if feed_error:
            st.error(f"Home feed failed: {feed_error}")
            st.info("If this is the first request after inactivity, wait a minute and refresh.")
        else:
            feed_cards = card_list_from_api(feed_data)
            poster_grid(feed_cards, cols=grid_cols, key_prefix="feed")

elif st.session_state.view == "details":
    if st.button("← Back to Home"):
        goto_home()

    movie_id = st.session_state.selected_tmdb_id
    if not movie_id:
        st.warning("No movie selected. Return home and select a movie.")
    else:
        with st.spinner("Loading movie details..."):
            detail_data, detail_error = api_get_json(f"/movie/id/{movie_id}")

        if detail_error:
            st.error(f"Could not load movie details: {detail_error}")
        elif isinstance(detail_data, dict):
            title = detail_data.get("title") or st.session_state.selected_title or "Untitled"
            st.header(title)

            backdrop = detail_data.get("backdrop_url")
            if backdrop:
                st.image(backdrop, use_container_width=True)

            poster_col, info_col = st.columns([1, 2])
            with poster_col:
                if detail_data.get("poster_url"):
                    st.image(detail_data["poster_url"], use_container_width=True)
            with info_col:
                st.subheader(title)
                release_date = detail_data.get("release_date")
                if release_date:
                    st.write(f"**Release date:** {release_date}")
                genres = detail_data.get("genres") or []
                if genres:
                    st.write("**Genres:** " + ", ".join(g.get("name", "") for g in genres if g.get("name")))
                overview = detail_data.get("overview")
                st.write(overview or "No overview is available for this movie.")

            st.divider()
            st.markdown("### 🎯 Genre Recommendations")
            with st.spinner("Finding similar-genre movies..."):
                genre_data, genre_error = api_get_json(
                    "/recommend/genre",
                    {"tmdb_id": movie_id, "limit": 18},
                )
            if genre_error:
                st.warning(f"Could not load genre recommendations: {genre_error}")
            else:
                poster_grid(card_list_from_api(genre_data), cols=grid_cols, key_prefix=f"genre_{movie_id}")

            st.divider()
            st.markdown("### 🤖 Content-Based TF-IDF Recommendations")
            with st.spinner("Finding content-based recommendations..."):
                bundle_data, bundle_error = api_get_json(
                    "/movie/search",
                    {"query": title, "tfidf_top_n": 12, "genre_limit": 1},
                )
            if bundle_error:
                st.warning(f"Could not load TF-IDF recommendations: {bundle_error}")
            else:
                tfidf_items = bundle_data.get("tfidf_recommendations", []) if isinstance(bundle_data, dict) else []
                tfidf_cards = []
                for item in tfidf_items:
                    movie = item.get("tmdb") or {}
                    if movie.get("tmdb_id"):
                        tfidf_cards.append(
                            {
                                "tmdb_id": movie["tmdb_id"],
                                "title": movie.get("title") or item.get("title") or "Untitled",
                                "poster_url": movie.get("poster_url"),
                                "vote_average": movie.get("vote_average"),
                            }
                        )
                if tfidf_cards:
                    poster_grid(tfidf_cards, cols=grid_cols, key_prefix=f"tfidf_{movie_id}")
                else:
                    st.info("No TF-IDF recommendations are available. Confirm that the four data/processed pickle files are included in the backend deployment.")
        else:
            st.warning("The backend returned no movie details.")
