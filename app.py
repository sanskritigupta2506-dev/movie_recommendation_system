import time
import httpx
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="CineMatch | Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
<style>
    .stApp {
        background: #0b0d12;
        color: #f5f5f5;
    }

    [data-testid="stHeader"] {
        background: rgba(11,13,18,0.90);
    }

    .hero {
        padding: 34px 36px;
        border-radius: 24px;
        margin-bottom: 25px;
        background:
            linear-gradient(110deg, rgba(20,23,32,.98), rgba(35,23,48,.92));
        border: 1px solid rgba(255,255,255,.08);
        box-shadow: 0 15px 45px rgba(0,0,0,.30);
    }

    .hero h1 {
        font-size: 44px;
        margin: 0;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .hero p {
        color: #b9bdc9;
        font-size: 17px;
        margin: 10px 0 0;
    }

    .section-title {
        font-size: 25px;
        font-weight: 750;
        margin: 26px 0 15px;
    }

    .movie-card {
        background: #141720;
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 18px;
        padding: 10px;
        height: 100%;
        box-shadow: 0 8px 25px rgba(0,0,0,.20);
    }

    .movie-title {
        font-size: 15px;
        font-weight: 700;
        margin-top: 8px;
        min-height: 40px;
    }

    .movie-meta {
        color: #9da3b2;
        font-size: 12px;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    .rating {
        color: #ffd166;
        font-weight: 700;
    }

    .details-box {
        background: #141720;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 22px;
        padding: 22px;
        margin: 8px 0 20px;
    }

    .tag {
        display: inline-block;
        background: #242938;
        color: #d9dce5;
        border-radius: 20px;
        padding: 5px 11px;
        margin: 4px 4px 4px 0;
        font-size: 12px;
    }

    .score {
        color: #8be9fd;
        font-weight: 700;
    }

    .small-muted {
        color: #8f95a3;
        font-size: 13px;
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 650;
    }

    section[data-testid="stSidebar"] {
        background: #10121a;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# API HELPERS
# =========================================================
def api_get(endpoint, params=None):
    for attempt in range(3):
        try:
            response = httpx.get(
                f"{API_URL}{endpoint}",
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            if attempt < 2:
                time.sleep(0.5)
            else:
                st.error("API connection error: Make sure FastAPI backend (main.py) is running on http://127.0.0.1:8000")
                return None


def get_home(category):
    return (
        api_get(
            "/home",
            {"category": category, "limit": 24},
        )
        or []
    )


def search_movies(query):
    data = api_get(
        "/tmdb/search",
        {"query": query, "page": 1},
    )
    return (data or {}).get("results", [])


def get_bundle(title):
    return api_get(
        "/movie/search",
        {
            "query": title,
            "tfidf_top_n": 12,
            "genre_limit": 12,
        },
    )


# =========================================================
# SESSION STATE
# =========================================================
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "search_text" not in st.session_state:
    st.session_state.search_text = ""


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🎬 CineMatch")
    st.caption("AI-powered movie discovery")

    st.markdown("---")
    st.markdown("### Browse")

    browse = st.radio(
        "Choose a category",
        [
            "Trending",
            "Popular",
            "Top Rated",
            "Now Playing",
            "Upcoming",
        ],
        label_visibility="collapsed",
    )

    category_map = {
        "Trending": "trending",
        "Popular": "popular",
        "Top Rated": "top_rated",
        "Now Playing": "now_playing",
        "Upcoming": "upcoming",
    }

    st.markdown("---")
    st.markdown("### About")
    st.caption(
        "Search for a movie and get content-based "
        "TF-IDF recommendations along with genre-based suggestions."
    )

    st.markdown("---")
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# =========================================================
# HERO
# =========================================================
st.markdown(
    """
<div class="hero">
    <h1>🎬 CineMatch</h1>
    <p>Discover your next movie using smart content-based recommendations.</p>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SEARCH BAR
# =========================================================
search_col, button_col, clear_col = st.columns([5, 1, 1])

with search_col:
    query = st.text_input(
        "Search movie",
        placeholder="Try: Inception, Interstellar, Avatar...",
        label_visibility="collapsed",
        value=st.session_state.search_text,
    )

with button_col:
    search_clicked = st.button(
        "🔎 Search",
        use_container_width=True,
        type="primary",
    )

with clear_col:
    if st.button("❌ Clear", use_container_width=True):
        st.session_state.search_text = ""
        st.session_state.search_results = []
        st.session_state.selected_movie = None
        st.rerun()

if search_clicked and query.strip():
    st.session_state.search_text = query.strip()
    st.session_state.search_results = search_movies(query.strip())


# =========================================================
# SEARCH RESULTS GRID
# =========================================================
if st.session_state.search_results:
    st.markdown('<div class="section-title">Search Results</div>', unsafe_allow_html=True)
    results = st.session_state.search_results[:12]

    for chunk in [results[k:k+6] for k in range(0, len(results), 6)]:
        cols = st.columns(len(chunk))
        for i, movie in enumerate(chunk):
            with cols[i]:
                poster = movie.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None

                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.markdown("🎞️ No poster")

                title = movie.get("title") or "Unknown title"
                year = (movie.get("release_date") or "")[:4]
                rating = movie.get("vote_average")
                rating_text = f"★ {rating:.1f}" if isinstance(rating, (int, float)) else "N/A"

                st.markdown(
                    f'<div class="movie-title">{title}</div>'
                    f'<div class="movie-meta">{year} · '
                    f'<span class="rating">{rating_text}</span></div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "View movie",
                    key=f"search_{movie.get('id')}_{i}",
                    use_container_width=True,
                ):
                    st.session_state.selected_movie = title
                    st.session_state.search_results = []
                    st.rerun()


# =========================================================
# SELECTED MOVIE + RECOMMENDATIONS
# =========================================================
elif st.session_state.selected_movie:
    bundle = get_bundle(st.session_state.selected_movie)

    if bundle:
        details = bundle.get("movie_details", {})
        title = details.get("title") or st.session_state.selected_movie
        poster = details.get("poster_url")
        backdrop = details.get("backdrop_url")
        overview = details.get("overview") or "No overview available."
        release = details.get("release_date") or "Unknown"
        genres = details.get("genres") or []
        rating = details.get("vote_average")

        st.markdown('<div class="section-title">Movie Details</div>', unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="details-box">', unsafe_allow_html=True)
            left, right = st.columns([1, 2.5])

            with left:
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.info("Poster unavailable")

            with right:
                st.markdown(f"## {title}")

                rating_text = (
                    f"★ {rating:.1f}" if isinstance(rating, (int, float)) else "N/A"
                )

                st.markdown(
                    f"**{release}** &nbsp;&nbsp; "
                    f"<span class='rating'>{rating_text}</span>",
                    unsafe_allow_html=True,
                )

                if genres:
                    tags = "".join(
                        f"<span class='tag'>{g.get('name', '')}</span>"
                        for g in genres
                    )
                    st.markdown(tags, unsafe_allow_html=True)

                st.markdown("### Overview")
                st.write(overview)

            st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------------------------------
        # TF-IDF RECOMMENDATIONS
        # -------------------------------------------------
        tfidf_recs = bundle.get("tfidf_recommendations", [])

        st.markdown(
            '<div class="section-title">✨ Because You Liked This</div>',
            unsafe_allow_html=True,
        )
        st.caption("Content-based recommendations generated using TF-IDF similarity.")

        if tfidf_recs:
            recs_to_show = tfidf_recs[:12]
            for chunk_idx, chunk in enumerate([recs_to_show[k:k+6] for k in range(0, len(recs_to_show), 6)]):
                cols = st.columns(len(chunk))
                for i, item in enumerate(chunk):
                    with cols[i]:
                        card = item.get("tmdb") or {}
                        poster_url = card.get("poster_url")

                        if poster_url:
                            st.image(poster_url, use_container_width=True)
                        else:
                            st.markdown("🎞️ No poster")

                        rec_title = item.get("title", "Unknown")
                        score = item.get("score", 0)

                        st.markdown(
                            f'<div class="movie-title">{rec_title}</div>'
                            f'<div class="movie-meta">'
                            f'<span class="score">Similarity: {score:.2f}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "View",
                            key=f"tfidf_{chunk_idx}_{i}_{rec_title}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_movie = rec_title
                            st.rerun()
        else:
            st.info("No TF-IDF recommendations found for this movie.")

        # -------------------------------------------------
        # GENRE RECOMMENDATIONS
        # -------------------------------------------------
        genre_recs = bundle.get("genre_recommendations", [])

        st.markdown(
            '<div class="section-title">🎭 More From This Genre</div>',
            unsafe_allow_html=True,
        )

        if genre_recs:
            genre_to_show = genre_recs[:12]
            for chunk_idx, chunk in enumerate([genre_to_show[k:k+6] for k in range(0, len(genre_to_show), 6)]):
                cols = st.columns(len(chunk))
                for i, movie in enumerate(chunk):
                    with cols[i]:
                        poster_url = movie.get("poster_url")

                        if poster_url:
                            st.image(poster_url, use_container_width=True)
                        else:
                            st.markdown("🎞️ No poster")

                        rec_title = movie.get("title", "Unknown")
                        year = (movie.get("release_date") or "")[:4]
                        rating = movie.get("vote_average")

                        rating_text = (
                            f"★ {rating:.1f}"
                            if isinstance(rating, (int, float))
                            else "N/A"
                        )

                        st.markdown(
                            f'<div class="movie-title">{rec_title}</div>'
                            f'<div class="movie-meta">{year} · '
                            f'<span class="rating">{rating_text}</span></div>',
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "View",
                            key=f"genre_{chunk_idx}_{i}_{movie.get('tmdb_id')}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_movie = rec_title
                            st.rerun()
        else:
            st.info("No genre recommendations found.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.selected_movie = None
            st.rerun()


# =========================================================
# HOME FEED
# =========================================================
else:
    category = category_map[browse]
    movies = get_home(category)

    st.markdown(
        f'<div class="section-title">{browse} Movies</div>',
        unsafe_allow_html=True,
    )

    if movies:
        movies_to_show = movies[:24]
        for chunk_idx, chunk in enumerate([movies_to_show[k:k+6] for k in range(0, len(movies_to_show), 6)]):
            cols = st.columns(len(chunk))
            for i, movie in enumerate(chunk):
                with cols[i]:
                    poster_url = movie.get("poster_url")

                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.markdown("🎞️ No poster")

                    title = movie.get("title", "Unknown")
                    year = (movie.get("release_date") or "")[:4]
                    rating = movie.get("vote_average")

                    rating_text = (
                        f"★ {rating:.1f}"
                        if isinstance(rating, (int, float))
                        else "N/A"
                    )

                    st.markdown(
                        f'<div class="movie-title">{title}</div>'
                        f'<div class="movie-meta">{year} · '
                        f'<span class="rating">{rating_text}</span></div>',
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "View",
                        key=f"home_{chunk_idx}_{i}_{movie.get('tmdb_id')}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_movie = title
                        st.rerun()

    else:
        st.warning("Could not load movies. Make sure FastAPI is running.")


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("CineMatch • Powered by your TF-IDF model + TMDB data")
