import streamlit as st
from db import get_connection, fetch_one, fetch_all, init_schema
from auth import login_page, register_page, logout
from quiz import quiz_page
from leaderboard import leaderboard_page
from admin import admin_page
from components.ui import load_css, hero


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Quiz Intelligence Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()


# =========================
# DATABASE CONNECTION
# =========================
@st.cache_resource
def init_connection():
    conn = get_connection()
    init_schema(conn)
    return conn


conn = init_connection()


# =========================
# HELPER FUNCTIONS
# =========================
def _get_best_score(conn, user_id):
    row = fetch_one(
        conn,
        "SELECT MAX(score) AS best FROM scores WHERE user_id = %s",
        (user_id,),
    )
    return row["best"] if row and row["best"] is not None else 0


def _get_quiz_count(conn, user_id):
    row = fetch_one(
        conn,
        "SELECT COUNT(*) AS total FROM scores WHERE user_id = %s",
        (user_id,),
    )
    return row["total"] if row else 0


def _get_rank(conn, user_id):
    rows = fetch_all(
        conn,
        """
        SELECT user_id,
               RANK() OVER (ORDER BY MAX(score) DESC) AS rnk
        FROM scores
        GROUP BY user_id
        """,
    )

    for row in rows:
        if row["user_id"] == user_id:
            return f"#{row['rnk']}"

    return "N/A"


# =========================
# SESSION STATE
# =========================
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"


# =========================
# AUTHENTICATION SCREEN
# =========================
if st.session_state["user"] is None:
    hero(
        "🧠 Quiz Intelligence Platform",
        "Professional quiz platform for Python, AI, SQL, Data Science and Aptitude."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        switch1, switch2 = st.columns(2)

        with switch1:
            if st.button(
                "Login",
                key="main_login_btn",
                use_container_width=True,
            ):
                st.session_state["page"] = "login"

        with switch2:
            if st.button(
                "Register",
                key="main_register_btn",
                use_container_width=True,
            ):
                st.session_state["page"] = "register"

        st.divider()

        if st.session_state["page"] == "register":
            register_page(conn)
        else:
            login_page(conn)

    st.stop()


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    user = st.session_state["user"]

    st.markdown("## 🧠 Quiz Platform")
    st.markdown("---")

    st.markdown(f"### Welcome, {user['username']}")
    st.caption(f"Role: {user['role'].capitalize()}")

    st.divider()

    nav_options = [
        "🏠 Home",
        "📝 Take Quiz",
        "🏆 Leaderboard",
    ]

    if user["role"] == "admin":
        nav_options.append("⚙️ Admin Panel")

    selected_page = st.radio(
        "Navigation",
        nav_options,
        label_visibility="collapsed",
    )

    st.divider()

    if st.button(
        "🚪 Logout",
        key="logout_btn",
        use_container_width=True,
    ):
        logout()


# =========================
# PAGE ROUTING
# =========================
if selected_page == "🏠 Home":
    hero(
        "🚀 Quiz Intelligence Dashboard",
        "Sharpen your Python, AI, SQL, Machine Learning, and Data Science skills."
    )

    st.markdown("### Platform Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🏆 Best Score",
            _get_best_score(conn, user["id"])
        )

    with col2:
        st.metric(
            "📝 Quizzes Taken",
            _get_quiz_count(conn, user["id"])
        )

    with col3:
        st.metric(
            "🌍 Global Rank",
            _get_rank(conn, user["id"])
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="custom-card">
        <h3>✨ Features</h3>
        <ul>
            <li>Timed quizzes</li>
            <li>Multiple categories</li>
            <li>Difficulty-based challenges</li>
            <li>Leaderboard competition</li>
            <li>Performance tracking</li>
            <li>Admin content management</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


elif selected_page == "📝 Take Quiz":
    quiz_page(conn)

elif selected_page == "🏆 Leaderboard":
    leaderboard_page(conn)

elif selected_page == "⚙️ Admin Panel":
    admin_page(conn)