"""
Movie Recommender — Streamlit frontend.
Simple, beginner-friendly. All pages live in one file.
"""

import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv(
    "API_BASE",
    "https://movie-recommendation-api-7910.onrender.com",
).rstrip("/")

TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# ------------------------------------------------------------------
# Small CSS for a dark, cinematic look
# ------------------------------------------------------------------
st.markdown("""
<style>
.stApp { background: #0b0d12; color: #e6e8ee; }
section[data-testid="stSidebar"] { background: #11141b; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px; }
.movie-title { font-size: 0.9rem; line-height: 1.2rem; min-height: 2.4rem; overflow: hidden; }
.muted { color: #9aa3b2; font-size: 0.9rem; }
.hero {
    padding: 1.6rem 1.4rem; border-radius: 16px;
    background: linear-gradient(120deg, #1b2030, #0e1118);
    border: 1px solid #1e2430;
}
.hero h1 { margin: 0; font-size: 2rem; }
.hero p { color: #9aa3b2; margin-top: .4rem; }
.chip {
    display: inline-block; padding: .2rem .6rem; border-radius: 999px;
    background: #1e2430; color: #cbd5e1; font-size: .8rem; margin-right: .35rem;
}
.score-badge {
    display: inline-block; padding: .15rem .55rem; border-radius: 8px;
    background: #1a3a2a; color: #6ee7b7; font-size: .78rem;
}
.stButton>button {
    border-radius: 10px; border: 1px solid #2a3140;
    background: #161b24; color: #e6e8ee;
}
.stButton>button:hover { border-color: #3b82f6; color: #93c5fd; }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------
if "view" not in st.session_state:
    st.session_state.view = "Home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "selected_title" not in st.session_state:
    st.session_state.selected_title = ""
if "home_category" not in st.session_state:
    st.session_state.home_category = "trending"
if "grid_cols" not in st.session_state:
    st.session_state.grid_cols = 6
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Restore details view from URL (?view=details&id=...)
if st.query_params.get("view") == "details" and st.query_params.get("id"):
    try:
        st.session_state.selected_tmdb_id = int(st.query_params["id"])
        st.session_state.view = "Details"
    except (TypeError, ValueError):
        pass


# ------------------------------------------------------------------
# API helpers — with retry for Render cold starts
# ------------------------------------------------------------------
@st.cache_data(ttl=120, show_spinner=False)
def api_get(path: str, params: Optional[Dict[str, Any]] = None) -> (Any, Optional[str]):
    """GET JSON with a couple of retries for cold starts."""
    for attempt in range(3):
        try:
            r = requests.get(f"{API_BASE}{path}", params=params, timeout=90)
            if r.status_code in (502, 503, 504) and attempt < 2:
                continue
            if r.status_code >= 400:
                return None, f"HTTP {r.status_code}: {r.text[:200]}"
            return r.json(), None
        except requests.RequestException as e:
            if attempt == 2:
                return None, f"Request failed: {e}"
    return None, "Unknown error"


def api_send(method: str, path: str, params=None, body=None) -> (Any, Optional[str]):
    """POST or DELETE (not cached)."""
    try:
        url = f"{API_BASE}{path}"
        if method == "POST":
            r = requests.post(url, params=params, json=body, timeout=60)
        elif method == "DELETE":
            r = requests.delete(url, params=params, timeout=60)
        else:
            return None, "Bad method"
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:200]}"
        try:
            return r.json(), None
        except ValueError:
            return {"ok": True}, None
    except requests.RequestException as e:
        return None, f"Request failed: {e}"


# ------------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------------
def go_to(view_name: str):
    st.session_state.view = view_name
    if "id" in st.query_params:
        del st.query_params["id"]
    if "view" in st.query_params:
        del st.query_params["view"]
    st.rerun()


def open_details(tmdb_id: int, title: str = ""):
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.session_state.selected_title = title
    st.session_state.view = "Details"
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def card_from_tmdb(item: dict) -> dict:
    """Turn a TMDB result OR backend movie card into our standard dict."""
    movie_id = item.get("tmdb_id") or item.get("id")
    if not movie_id:
        return {}
    poster = item.get("poster_url")
    if not poster and item.get("poster_path"):
        poster = f"{TMDB_IMG}{item['poster_path']}"
    return {
        "tmdb_id": int(movie_id),
        "title": item.get("title") or item.get("name") or "Untitled",
        "poster_url": poster,
        "release_date": item.get("release_date") or item.get("first_air_date"),
        "vote_average": item.get("vote_average"),
    }


def poster_grid(movies: List[dict], cols: int, key: str, show_score: bool = False):
    """Draw movie cards in a grid."""
    if not movies:
        st.info("No movies to show.")
        return

    for start in range(0, len(movies), cols):
        columns = st.columns(cols)
        for col, movie in zip(columns, movies[start:start + cols]):
            with col:
                poster = movie.get("poster_url")
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown(
                        "<div style='height:270px; display:flex; align-items:center;"
                        "justify-content:center; background:#161b24; border-radius:8px;"
                        "color:#666;'>🖼️ No poster</div>",
                        unsafe_allow_html=True,
                    )
                title = movie.get("title", "Untitled")
                st.markdown(f"<div class='movie-title'><b>{title}</b></div>",
                            unsafe_allow_html=True)

                year = (movie.get("release_date") or "")[:4]
                rating = to_float(movie.get("vote_average"))
                parts = []
                if year:
                    parts.append(year)
                if rating is not None:
                    parts.append(f"⭐ {rating:.1f}")
                if parts:
                    st.caption(" · ".join(parts))

                if show_score and movie.get("score") is not None:
                    score = to_float(movie["score"]) or 0.0
                    st.markdown(
                        f"<span class='score-badge'>similarity {score:.3f}</span>",
                        unsafe_allow_html=True,
                    )

                if st.button("Open", key=f"{key}_{movie['tmdb_id']}_{start}",
                             use_container_width=True):
                    open_details(movie["tmdb_id"], title)


# ------------------------------------------------------------------
# Sidebar navigation (simplified)
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎬 Movie Recommender")
    st.caption("Content-based recommendations with TF-IDF.")
    st.divider()

    sections = {
        "DISCOVER": ["Home"],
        "MACHINE LEARNING": ["Compare Movies", "Movie Analytics"],
        "MY COLLECTION": ["My Watchlist", "Favorites"],
        "PROJECT": ["About Project"],
    }
    for section, items in sections.items():
        st.markdown(f"**{section}**")
        for item in items:
            label = ("▶ " if st.session_state.view == item else "• ") + item
            if st.button(label, key=f"nav_{item}", use_container_width=True):
                go_to(item)
        st.write("")

    st.divider()
    st.session_state.grid_cols = st.slider(
        "Grid columns", 3, 8, st.session_state.grid_cols
    )
    st.caption("Backend API")
    st.code(API_BASE, language="text")

GRID_COLS = st.session_state.grid_cols


# ==================================================================
# HOME
# ==================================================================
def page_home():
    st.markdown("""
    <div class="hero">
        <h1>🎬 Discover your next favorite movie</h1>
        <p>Search millions of films, browse trending picks, and get TF-IDF recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # Search bar + button
    col1, col2 = st.columns([5, 1])
    with col1:
        typed = st.text_input(
            "Search by movie title",
            value=st.session_state.search_query,
            placeholder="e.g. Inception, Batman, Interstellar...",
            key="home_search_box",
            label_visibility="collapsed",
        )
    with col2:
        search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")

    # If a search was run, show results and stop (don't show feed below)
    if search_clicked:
        st.session_state.search_query = typed.strip()

    if st.session_state.search_query:
        query = st.session_state.search_query
        if len(query) < 2:
            st.caption("Type at least 2 characters.")
        else:
            with st.spinner(f"Searching '{query}'..."):
                data, err = api_get("/tmdb/search", {"query": query, "page": 1})
            if err:
                st.error(f"Search failed: {err}")
            else:
                results = (data or {}).get("results", [])
                cards = [c for c in (card_from_tmdb(m) for m in results) if c]
                st.markdown(f"### 🔍 Results for '{query}'")
                poster_grid(cards[:24], GRID_COLS, key="home_search")
                if not cards:
                    st.info("No matches found.")
        if st.button("Clear search"):
            st.session_state.search_query = ""
            st.rerun()
        return

    # No search → show category tabs
    st.markdown("### 🏠 Browse movies")
    categories = ["trending", "popular", "top_rated", "now_playing", "upcoming"]
    labels = [c.replace("_", " ").title() for c in categories]
    tabs = st.tabs(labels)
    for tab, cat in zip(tabs, categories):
        with tab:
            with st.spinner("Loading..."):
                data, err = api_get("/home", {"category": cat, "limit": 24})
            if err:
                st.error(f"Could not load: {err}")
                st.info("Backend may be waking up. Wait ~30s and refresh.")
            else:
                cards = [c for c in (card_from_tmdb(m) for m in (data or [])) if c]
                poster_grid(cards, GRID_COLS, key=f"home_{cat}")


# ==================================================================
# DETAILS
# ==================================================================
def page_details():
    if st.button("← Back"):
        go_to("Home")

    movie_id = st.session_state.selected_tmdb_id
    if not movie_id:
        st.warning("No movie selected.")
        return

    with st.spinner("Loading details..."):
        data, err = api_get(f"/movie/id/{movie_id}")

    if err:
        st.error(f"Could not load details: {err}")
        return
    if not isinstance(data, dict):
        st.warning("No details returned.")
        return

    title = data.get("title") or st.session_state.selected_title or "Untitled"

    if data.get("backdrop_url"):
        st.image(data["backdrop_url"], use_container_width=True)

    st.header(title)

    left, right = st.columns([1, 2])
    with left:
        if data.get("poster_url"):
            st.image(data["poster_url"], use_container_width=True)
    with right:
        if data.get("release_date"):
            st.write(f"**Release date:** {data['release_date']}")
        if data.get("runtime"):
            st.write(f"**Runtime:** {data['runtime']} min")
        if data.get("vote_average"):
            st.write(f"**Rating:** {data['vote_average']} / 10")

        genres = data.get("genres") or []
        if genres:
            chips = "".join(
                f"<span class='chip'>{g.get('name','')}</span>"
                for g in genres if g.get("name")
            )
            st.markdown(chips, unsafe_allow_html=True)

        st.write(data.get("overview") or "_No overview available._")

        col_a, col_b = st.columns(2)
        if col_a.button("📌 Add to Watchlist", use_container_width=True):
            _, e = api_send("POST", "/collection/add", body={
                "tmdb_id": data["tmdb_id"], "title": title,
                "poster_url": data.get("poster_url"),
                "release_date": data.get("release_date"),
                "vote_average": data.get("vote_average"),
                "kind": "watchlist", "watched": False,
            })
            st.success("Added to watchlist.") if not e else st.error(e)
        if col_b.button("❤️ Add to Favorites", use_container_width=True):
            _, e = api_send("POST", "/collection/add", body={
                "tmdb_id": data["tmdb_id"], "title": title,
                "poster_url": data.get("poster_url"),
                "release_date": data.get("release_date"),
                "vote_average": data.get("vote_average"),
                "kind": "favorite", "watched": False,
            })
            st.success("Added to favorites.") if not e else st.error(e)

    st.divider()
    st.markdown("### 🎯 Genre recommendations")
    with st.spinner("Finding similar movies..."):
        gdata, gerr = api_get("/recommend/genre", {"tmdb_id": movie_id, "limit": 18})
    if gerr:
        st.warning(f"Could not load recommendations: {gerr}")
    else:
        cards = [c for c in (card_from_tmdb(m) for m in (gdata or [])) if c]
        poster_grid(cards, GRID_COLS, key=f"genre_{movie_id}")


# ==================================================================
# COMPARE
# ==================================================================
def page_compare():
    st.markdown("## ⚖️ Compare Movies")
    st.caption("Pick two movies to see them side by side.")

    col1, col2 = st.columns(2)
    with col1:
        title_a = st.text_input("First movie", key="cmp_a")
    with col2:
        title_b = st.text_input("Second movie", key="cmp_b")

    if not st.button("Compare", type="primary"):
        return
    if not title_a.strip() or not title_b.strip():
        st.warning("Enter both movie titles.")
        return

    def first_hit(q):
        d, e = api_get("/tmdb/search", {"query": q.strip(), "page": 1})
        if e or not isinstance(d, dict):
            return None
        r = d.get("results") or []
        return r[0] if r else None

    with st.spinner("Looking up..."):
        m1 = first_hit(title_a)
        m2 = first_hit(title_b)

    if not m1 or not m2:
        st.error("Could not find one or both movies.")
        return

    with st.spinner("Loading details..."):
        d1, e1 = api_get(f"/movie/id/{m1['id']}")
        d2, e2 = api_get(f"/movie/id/{m2['id']}")

    if e1 or e2 or not d1 or not d2:
        st.error("Could not load details.")
        return

    left, right = st.columns(2)
    for col, d in ((left, d1), (right, d2)):
        with col:
            if d.get("poster_url"):
                st.image(d["poster_url"], use_container_width=True)
            st.subheader(d.get("title") or "Untitled")

            for label, val in [
                ("Release", d.get("release_date")),
                ("Runtime", f"{d['runtime']} min" if d.get("runtime") else None),
                ("Rating", f"{d['vote_average']} / 10" if d.get("vote_average") else None),
                ("Votes", d.get("vote_count")),
                ("Popularity", round(d["popularity"], 1) if d.get("popularity") else None),
            ]:
                if val:
                    st.write(f"**{label}:** {val}")

            st.markdown("**Overview**")
            st.write(d.get("overview") or "_No overview._")


# ==================================================================
# ANALYTICS
# ==================================================================
def page_analytics():
    st.markdown("## 📊 Movie Analytics")
    st.caption("Statistics about the local TF-IDF dataset.")

    with st.spinner("Loading analytics..."):
        data, err = api_get("/analytics")

    if err:
        st.error(f"Could not load analytics: {err}")
        st.info(
            "This endpoint exists only on the **new** backend. "
            "Make sure you deployed the updated `main.py` and `database.py` "
            "to Render, then redeploy the backend service."
        )
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Movies in dataset", f"{data.get('total_movies', 0):,}")
    c2.metric("TF-IDF vocabulary", f"{data.get('tfidf_vocab_size', 0):,}")
    c3.metric("Columns", len(data.get("columns", [])))

    st.divider()

    top = data.get("top_genres") or []
    if top:
        st.markdown("### 🎭 Top genres")
        st.bar_chart({g["genre"]: g["count"] for g in top[:15]})

    hist = data.get("rating_histogram") or []
    if hist:
        st.markdown("### ⭐ Ratings distribution")
        st.bar_chart({r["range"]: r["count"] for r in hist})

    pop = data.get("top_popular") or []
    if pop:
        st.markdown("### 🔥 Most popular in dataset")
        st.dataframe(pop, use_container_width=True)

    missing = data.get("missing_values") or {}
    if missing:
        st.markdown("### 🕳️ Missing values")
        st.dataframe(
            [{"column": k, "missing": v} for k, v in missing.items()],
            use_container_width=True,
        )


# ==================================================================
# WATCHLIST
# ==================================================================
def add_search_block(kind: str, key_prefix: str):
    """Reusable 'search and add' block for Watchlist and Favorites."""
    with st.expander(f"➕ Add a movie to your {kind}"):
        title = st.text_input("Movie title", key=f"{key_prefix}_title")
        if st.button("Search", key=f"{key_prefix}_search"):
            if not title.strip():
                st.warning("Type a title.")
            else:
                d, e = api_get("/tmdb/search", {"query": title.strip(), "page": 1})
                if e:
                    st.error(e)
                else:
                    results = (d or {}).get("results") or []
                    if not results:
                        st.info("No matches.")
                    for m in results[:5]:
                        col1, col2 = st.columns([4, 1])
                        col1.write(f"**{m.get('title')}** — {(m.get('release_date') or '')[:4]}")
                        if col2.button("Add", key=f"{key_prefix}_add_{m['id']}"):
                            card = card_from_tmdb(m)
                            _, e2 = api_send("POST", "/collection/add", body={
                                "tmdb_id": card["tmdb_id"], "title": card["title"],
                                "poster_url": card["poster_url"],
                                "release_date": card["release_date"],
                                "vote_average": card["vote_average"],
                                "kind": kind, "watched": False,
                            })
                            if e2:
                                st.error(e2)
                            else:
                                st.success("Added.")
                                api_get.clear()


def page_watchlist():
    st.markdown("## 📌 My Watchlist")
    st.caption("Shared watchlist stored on the backend (SQLite).")

    add_search_block("watchlist", "wl")
    st.divider()

    items, err = api_get("/collection/list", {"kind": "watchlist"})
    if err:
        st.error(f"Could not load watchlist: {err}")
        st.info("This endpoint exists only on the new backend. Deploy the updated `main.py`.")
        return
    if not items:
        st.info("Your watchlist is empty.")
        return

    for row in items:
        c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
        with c1:
            if row.get("poster_url"):
                st.image(row["poster_url"], width=70)
        with c2:
            flag = "✅ Watched" if row.get("watched") else "🕒 Unwatched"
            st.markdown(f"**{row.get('title')}**")
            st.caption(f"{flag} · {(row.get('release_date') or '')[:4]}")
        with c3:
            if st.button("Toggle", key=f"wl_toggle_{row['tmdb_id']}"):
                api_send("POST", "/collection/toggle-watched",
                         params={"tmdb_id": row["tmdb_id"]})
                api_get.clear()
                st.rerun()
        with c4:
            if st.button("Remove", key=f"wl_remove_{row['tmdb_id']}"):
                api_send("DELETE", "/collection/remove",
                         params={"tmdb_id": row["tmdb_id"], "kind": "watchlist"})
                api_get.clear()
                st.rerun()


# ==================================================================
# FAVORITES
# ==================================================================
def page_favorites():
    st.markdown("## ❤️ Favorites")
    st.caption("Movies you love, stored on the backend.")

    add_search_block("favorite", "fav")
    st.divider()

    items, err = api_get("/collection/list", {"kind": "favorite"})
    if err:
        st.error(f"Could not load favorites: {err}")
        st.info("This endpoint exists only on the new backend. Deploy the updated `main.py`.")
        return
    if not items:
        st.info("No favorites yet.")
        return

    cards = [{
        "tmdb_id": r["tmdb_id"], "title": r["title"],
        "poster_url": r.get("poster_url"),
        "release_date": r.get("release_date"),
        "vote_average": r.get("vote_average"),
    } for r in items]
    poster_grid(cards, GRID_COLS, key="fav")

    st.divider()
    st.markdown("**Manage**")
    for row in items:
        c1, c2 = st.columns([5, 1])
        c1.write(row["title"])
        if c2.button("Remove", key=f"fav_remove_{row['tmdb_id']}"):
            api_send("DELETE", "/collection/remove",
                     params={"tmdb_id": row["tmdb_id"], "kind": "favorite"})
            api_get.clear()
            st.rerun()


# ==================================================================
# ABOUT
# ==================================================================
def page_about():
    st.markdown("## ℹ️ About This Project")
    st.markdown("""
**Movie Recommendation System** is a full-stack app that suggests movies using
a **content-based** recommender.

### How it works
1. Combine each movie's `overview`, `genres`, and `tagline` into one text field.
2. Clean the text (lowercase, remove stopwords, lemmatize).
3. Convert each movie's text into a numeric vector with **TF-IDF**.
4. Measure similarity between vectors with **cosine similarity**.
5. Return the top-N most similar movies.

### Stack
- **Frontend:** Streamlit
- **Backend:** FastAPI + Uvicorn
- **ML:** scikit-learn, pandas, numpy
- **Data:** TMDB API
- **Storage:** SQLite
- **Deployment:** Render

### Links
- 🌐 Frontend: https://movie-recommendation-app-sfxg.onrender.com
- ⚡ Backend: https://movie-recommendation-api-7910.onrender.com
- 📚 Docs: https://movie-recommendation-api-7910.onrender.com/docs
- 💻 GitHub: https://github.com/Kazi-Sadman/Movie-Recommendation-System

### Scope
Content-based only — no collaborative filtering, no deep learning, no user profiles.
""")


# ==================================================================
# ROUTER
# ==================================================================
PAGES = {
    "Home": page_home,
    "Details": page_details,
    "Compare Movies": page_compare,
    "Movie Analytics": page_analytics,
    "My Watchlist": page_watchlist,
    "Favorites": page_favorites,
    "About Project": page_about,
}

PAGES.get(st.session_state.view, page_home)()