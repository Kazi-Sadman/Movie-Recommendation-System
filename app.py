"""
Movie Recommender — Streamlit frontend.
Same features as before, but with a colorful, polished design.
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


# ==================================================================
# 🎨 COLORFUL CSS
# ==================================================================
st.markdown("""
<style>
/* ---------- Global ---------- */
.stApp {
    background: radial-gradient(circle at 15% 0%, #1a1040 0%, #0a0b14 40%, #05060a 100%);
    color: #eef1f8;
    font-family: "Segoe UI", system-ui, sans-serif;
}
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141026 0%, #0b0a18 100%);
    border-right: 1px solid #251a4a;
}
section[data-testid="stSidebar"] h2 {
    background: linear-gradient(90deg, #a855f7, #ec4899, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
section[data-testid="stSidebar"] .stButton>button {
    background: linear-gradient(90deg, #1c1633, #221a44);
    border: 1px solid #34265c;
    color: #cfc6ff;
    font-weight: 500;
    transition: all 0.18s ease;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    background: linear-gradient(90deg, #7c3aed, #db2777);
    color: white;
    border-color: transparent;
    box-shadow: 0 0 16px rgba(168,85,247,0.45);
    transform: translateX(3px);
}

/* ---------- Headings ---------- */
h1, h2, h3 { color: #ffffff; font-weight: 800; letter-spacing: -0.02em; }
h1 { background: linear-gradient(90deg, #a855f7, #ec4899 45%, #f59e0b);
     -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* ---------- Hero ---------- */
.hero {
    padding: 2rem 1.8rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #4c1d95 0%, #831843 50%, #b45309 100%);
    box-shadow: 0 20px 60px -20px rgba(168,85,247,0.5);
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.15), transparent 45%);
    pointer-events: none;
}
.hero h1 {
    -webkit-text-fill-color: #ffffff;
    background: none;
    margin: 0;
    font-size: 2.2rem;
    text-shadow: 0 2px 24px rgba(0,0,0,0.4);
}
.hero p { color: rgba(255,255,255,0.85); margin-top: .5rem; font-size: 1.05rem; }

/* ---------- Movie cards ---------- */
.movie-title {
    font-size: 0.92rem;
    line-height: 1.25rem;
    min-height: 2.5rem;
    overflow: hidden;
    color: #eef1f8;
    font-weight: 600;
    margin-top: .35rem;
}
.movie-meta {
    display: inline-block;
    padding: .15rem .55rem;
    border-radius: 6px;
    background: rgba(168,85,247,0.15);
    color: #c4b5fd;
    font-size: .78rem;
    margin-right: .3rem;
    margin-top: .2rem;
}
.rating-pill {
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
    color: #1a1a1a;
    font-weight: 700;
}

/* ---------- Buttons (main area) ---------- */
.stButton>button {
    background: linear-gradient(90deg, #7c3aed, #db2777);
    color: white !important;
    border: none;
    font-weight: 600;
    border-radius: 10px;
    transition: all 0.15s ease;
    box-shadow: 0 4px 14px -4px rgba(168,85,247,0.4);
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px -4px rgba(236,72,153,0.6);
}

/* ---------- Inputs ---------- */
.stTextInput>div>div>input,
.stNumberInput>div>div>input {
    background: rgba(20,18,40,0.7);
    border: 1px solid #34265c;
    color: white;
    border-radius: 10px;
}
.stTextInput>div>div>input:focus {
    border-color: #a855f7;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.25);
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    background: rgba(30,24,60,0.6);
    border-radius: 10px;
    padding: 8px 16px;
    color: #a99cd8;
    font-weight: 600;
    border: 1px solid transparent;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #7c3aed, #db2777);
    color: white !important;
    border-color: transparent;
}

/* ---------- Alerts / info boxes ---------- */
.stAlert { border-radius: 12px; }
div[data-testid="stAlert"] {
    background: rgba(124,58,237,0.08);
    border-left: 3px solid #a855f7;
}

/* ---------- Expander ---------- */
.streamlit-expanderHeader, details summary {
    background: rgba(30,24,60,0.5) !important;
    border-radius: 10px !important;
    color: #cfc6ff !important;
}

/* ---------- Metrics ---------- */
[data-testid="stMetricValue"] {
    background: linear-gradient(90deg, #a855f7, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* ---------- Chips ---------- */
.chip {
    display: inline-block;
    padding: .25rem .7rem;
    border-radius: 999px;
    background: linear-gradient(90deg, rgba(168,85,247,0.25), rgba(236,72,153,0.25));
    border: 1px solid rgba(168,85,247,0.4);
    color: #e9d5ff;
    font-size: .8rem;
    margin: 0 .35rem .35rem 0;
}
.score-badge {
    display: inline-block;
    padding: .2rem .65rem;
    border-radius: 8px;
    background: linear-gradient(90deg, #059669, #10b981);
    color: white;
    font-size: .78rem;
    font-weight: 700;
    box-shadow: 0 2px 10px -2px rgba(16,185,129,0.5);
}

/* ---------- Image rounding ---------- */
img { border-radius: 12px; }

/* ---------- Caption colors ---------- */
.stCaption, .muted { color: #9a8fc4 !important; }
</style>
""", unsafe_allow_html=True)


# ==================================================================
# Session state
# ==================================================================
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

if st.query_params.get("view") == "details" and st.query_params.get("id"):
    try:
        st.session_state.selected_tmdb_id = int(st.query_params["id"])
        st.session_state.view = "Details"
    except (TypeError, ValueError):
        pass


# ==================================================================
# API helpers
# ==================================================================
import time

@st.cache_data(ttl=120, show_spinner=False)
def api_get(path: str, params: Optional[Dict[str, Any]] = None):
    """GET JSON with proper retries for Render cold starts."""
    last_error = None
    for attempt in range(4):  # 4 attempts total
        try:
            r = requests.get(f"{API_BASE}{path}", params=params, timeout=90)
            if r.status_code in (502, 503, 504):
                # Backend is booting. Wait longer each retry.
                if attempt < 3:
                    time.sleep(8 + attempt * 4)  # 8s, 12s, 16s = 36s total
                    continue
                else:
                    return None, "Backend is starting up (502). Please wait ~30s and refresh."
            if r.status_code >= 400:
                return None, f"HTTP {r.status_code}: {r.text[:200]}"
            return r.json(), None
        except requests.RequestException as e:
            last_error = str(e)
            if attempt < 3:
                time.sleep(5)
                continue
            return None, f"Request failed: {e}"
    return None, last_error or "Unknown error"

def api_send(method: str, path: str, params=None, body=None):
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


# ==================================================================
# Small helpers
# ==================================================================
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
                        "justify-content:center; background:#1a1430; border-radius:12px;"
                        "color:#7c6899; font-size:.85rem;'>🖼️ No poster</div>",
                        unsafe_allow_html=True,
                    )

                title = movie.get("title", "Untitled")
                st.markdown(
                    f"<div class='movie-title'>{title}</div>",
                    unsafe_allow_html=True,
                )

                year = (movie.get("release_date") or "")[:4]
                rating = to_float(movie.get("vote_average"))

                meta_html = ""
                if year:
                    meta_html += f"<span class='movie-meta'>{year}</span>"
                if rating is not None:
                    meta_html += f"<span class='movie-meta rating-pill'>⭐ {rating:.1f}</span>"
                if meta_html:
                    st.markdown(meta_html, unsafe_allow_html=True)

                if show_score and movie.get("score") is not None:
                    score = to_float(movie["score"]) or 0.0
                    st.markdown(
                        f"<span class='score-badge'>similarity {score:.3f}</span>",
                        unsafe_allow_html=True,
                    )

                if st.button("▶ Open", key=f"{key}_{movie['tmdb_id']}_{start}",
                             use_container_width=True):
                    open_details(movie["tmdb_id"], title)


# ==================================================================
# Sidebar
# ==================================================================
with st.sidebar:
    st.markdown("## 🎬 Movie Recommender")
    st.markdown(
        "<p style='color:#9a8fc4; font-size:.85rem; margin-top:-8px;'>"
        "Content-based recommendations with TF-IDF</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    sections = {
        "DISCOVER": ["Home"],
        "MACHINE LEARNING": ["Compare Movies", "Movie Analytics"],
        "MY COLLECTION": ["My Watchlist", "Favorites"],
        "PROJECT": ["About Project"],
    }
    for section, items in sections.items():
        st.markdown(
            f"<div style='color:#7c6899; font-size:.75rem; font-weight:700; "
            f"letter-spacing:.08em; margin: 12px 0 6px;'>{section}</div>",
            unsafe_allow_html=True,
        )
        for item in items:
            label = ("▶ " if st.session_state.view == item else "• ") + item
            if st.button(label, key=f"nav_{item}", use_container_width=True):
                go_to(item)

    st.divider()
    st.session_state.grid_cols = st.slider(
        "Grid columns", 3, 8, st.session_state.grid_cols
    )
    st.markdown(
        "<div style='color:#7c6899; font-size:.75rem; margin-top:12px;'>BACKEND</div>",
        unsafe_allow_html=True,
    )
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
        if st.button("✖ Clear search"):
            st.session_state.search_query = ""
            st.rerun()
        return

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

    st.markdown(
        f"<h1 style='margin-top:1rem;'>{title}</h1>",
        unsafe_allow_html=True,
    )

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
            st.write(f"**Rating:** ⭐ {data['vote_average']} / 10")

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
        title_a = st.text_input("First movie", key="cmp_a", placeholder="e.g. Inception")
    with col2:
        title_b = st.text_input("Second movie", key="cmp_b", placeholder="e.g. Interstellar")

    if not st.button("⚖️ Compare", type="primary"):
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
    for col, d, accent in (
        (left, d1, "linear-gradient(135deg,#7c3aed,#a855f7)"),
        (right, d2, "linear-gradient(135deg,#db2777,#f59e0b)"),
    ):
        with col:
            if d.get("poster_url"):
                st.image(d["poster_url"], use_container_width=True)
            st.markdown(
                f"<div style='padding:.6rem 1rem; border-radius:10px; "
                f"background:{accent}; margin:.6rem 0 .8rem; font-weight:700; "
                f"text-align:center;'>{d.get('title') or 'Untitled'}</div>",
                unsafe_allow_html=True,
            )

            for label, val in [
                ("Release", d.get("release_date")),
                ("Runtime", f"{d['runtime']} min" if d.get("runtime") else None),
                ("Rating", f"⭐ {d['vote_average']} / 10" if d.get("vote_average") else None),
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
            "Deploy the updated `main.py` and `database.py` to Render."
        )
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("🎬 Movies", f"{data.get('total_movies', 0):,}")
    c2.metric("📚 TF-IDF vocab", f"{data.get('tfidf_vocab_size', 0):,}")
    c3.metric("📋 Columns", len(data.get("columns", [])))

    st.divider()

    top = data.get("top_genres") or []
    if top:
        st.markdown("### 🎭 Top genres")
        st.bar_chart({g["genre"]: g["count"] for g in top[:15]}, color="#a855f7")

    hist = data.get("rating_histogram") or []
    if hist:
        st.markdown("### ⭐ Ratings distribution")
        st.bar_chart({r["range"]: r["count"] for r in hist}, color="#f59e0b")

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
# Collection shared block
# ==================================================================
def add_search_block(kind: str, key_prefix: str):
    with st.expander(f"➕ Add a movie to your {kind}"):
        title = st.text_input("Movie title", key=f"{key_prefix}_title",
                              placeholder="Type a movie and press Search")
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


# ==================================================================
# WATCHLIST
# ==================================================================
def page_watchlist():
    st.markdown("## 📌 My Watchlist")
    st.caption("A shared watchlist stored on the backend (SQLite).")

    add_search_block("watchlist", "wl")
    st.divider()

    items, err = api_get("/collection/list", {"kind": "watchlist"})
    if err:
        st.error(f"Could not load watchlist: {err}")
        st.info("This endpoint exists only on the new backend. Deploy the updated `main.py`.")
        return
    if not items:
        st.info("Your watchlist is empty. Add a movie above!")
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
        st.info("No favorites yet. Add one above!")
        return

    cards = [{
        "tmdb_id": r["tmdb_id"], "title": r["title"],
        "poster_url": r.get("poster_url"),
        "release_date": r.get("release_date"),
        "vote_average": r.get("vote_average"),
    } for r in items]
    poster_grid(cards, GRID_COLS, key="fav")

    st.divider()
    st.markdown("**Manage favorites**")
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