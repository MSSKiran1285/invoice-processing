# app.py
import streamlit as st
import pandas as pd

from invoice_qa_engine import load_database, answer_chatty_openai

# -----------------------------------------------------------
# Page config
# -----------------------------------------------------------
st.set_page_config(
    page_title="Invoice Question Answering Assistant",
    page_icon="📄",
    layout="wide",
)

DB_PATH = "your_database.xlsx"

# -----------------------------------------------------------
# Session state
# -----------------------------------------------------------
if "user_question" not in st.session_state:
    st.session_state["user_question"] = ""

if "follow_up" not in st.session_state:
    st.session_state["follow_up"] = ""

if "last_raw_result" not in st.session_state:
    st.session_state["last_raw_result"] = None

if "last_answer" not in st.session_state:
    st.session_state["last_answer"] = ""

# -----------------------------------------------------------
# Callbacks
# -----------------------------------------------------------
def use_follow_up():
    fu = st.session_state.get("follow_up", "")
    if fu:
        st.session_state["user_question"] = fu


def set_chip_question(text: str):
    st.session_state["user_question"] = text


# -----------------------------------------------------------
# Load database (cached)
# -----------------------------------------------------------
@st.cache_resource(show_spinner=True)
def _load_db_cached(path: str) -> pd.DataFrame:
    return load_database(path)


try:
    df = _load_db_cached(DB_PATH)
    st.toast(f"Loaded database with {len(df):,} rows.", icon="✅")
except Exception as e:
    st.error(f"Could not load database from '{DB_PATH}': {e}")
    st.stop()

# -----------------------------------------------------------
# Minimal / fluid CSS
# -----------------------------------------------------------
st.markdown(
    """
    <style>
    /* Center content and limit width for a calmer layout */
    .block-container {
        max-width: 1000px;
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }

    /* Headline + subtitle */
    .app-title {
        font-size: 1.7rem;
        font-weight: 650;
        letter-spacing: 0.01em;
    }
    .app-subtitle {
        font-size: 0.9rem;
        color: #6f6f6f;
        margin-top: 0.2rem;
    }

    /* Light pill buttons for chips */
    .stButton>button {
        border-radius: 999px;
        padding: 0.25rem 1.1rem;
        font-size: 0.87rem;
        border: 1px solid rgba(0,0,0,0.08);
        background-color: #ffffff;
        color: #333333;
    }
    .stButton>button:hover {
        border-color: rgba(0,0,0,0.18);
        background-color: #f7f7f7;
    }

    /* Primary ask button – keep but soften */
    .ask-button>button {
        border-radius: 999px;
        padding: 0.4rem 1.8rem;
        font-weight: 600;
        background: #ff4b4b;
        border: none;
    }

    /* Answer section: simple card */
    .answer-card {
        margin-top: 0.8rem;
        padding: 0.9rem 1.1rem;
        border-radius: 0.8rem;
        border: 1px solid rgba(0,0,0,0.06);
        background-color: #ffffff;
    }
    .answer-header {
        font-weight: 600;
        font-size: 0.97rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
        margin-bottom: 0.2rem;
    }
    .answer-body {
        font-size: 0.94rem;
        line-height: 1.45;
    }

    /* Follow-up row */
    .followup-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #9a9a9a;
        letter-spacing: 0.06em;
        margin-top: 0.9rem;
        margin-bottom: 0.2rem;
    }
    .followup-text {
        font-size: 0.9rem;
        color: #555555;
    }
    .followup-btn>button {
        border-radius: 999px;
        padding: 0.25rem 0.9rem;
        font-size: 0.85rem;
    }

    /* Expander title – lighter */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
header_col1, header_col2 = st.columns([4, 1.5])

with header_col1:
    st.markdown(
        '<div class="app-title">📄 Invoice Question Answering Assistant</div>'
        '<div class="app-subtitle">'
        'Ask free-form questions about invoices, customers, regions, due dates, and more.'
        '</div>',
        unsafe_allow_html=True,
    )

with header_col2:
    st.caption("Rows in database")
    st.markdown(f"**{len(df):,}**")

st.markdown("---")

# -----------------------------------------------------------
# QUESTION INPUT
# -----------------------------------------------------------
st.markdown(
    "#### 💬 Ask a question "
    "<span style='font-size:0.85rem;color:#a0a0a0;'>NATURAL LANGUAGE</span>",
    unsafe_allow_html=True,
)

question = st.text_input(
    label="",
    key="user_question",
    placeholder="For example: “What is the total overdue amount by region this month?”",
)

# Chips row – more subtle, spaced
chip_col1, chip_col2, chip_col3 = st.columns(3)
with chip_col1:
    st.button(
        "🔍 Overdue summary",
        key="chip_overdue",
        on_click=set_chip_question,
        kwargs={
            "text": "Give me an overview of overdue invoices by region and month."
        },
    )
with chip_col2:
    st.button(
        "👑 Top customers",
        key="chip_top_customers",
        on_click=set_chip_question,
        kwargs={
            "text": "Show the top 10 customers by total spend with amounts."
        },
    )
with chip_col3:
    st.button(
        "🌍 Regional performance",
        key="chip_regional",
        on_click=set_chip_question,
        kwargs={
            "text": "Compare revenue and overdue amounts for each region."
        },
    )

st.write("")

ask_col, _ = st.columns([1, 5])
with ask_col:
    ask_pressed = st.button("Ask", key="ask_btn", type="primary", use_container_width=False)

# -----------------------------------------------------------
# ANSWERING
# -----------------------------------------------------------
if ask_pressed:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Thinking over your Excel data..."):
            resp = answer_chatty_openai(df=df, question=question)

        st.session_state["last_raw_result"] = resp.get("raw_result")
        st.session_state["last_answer"] = resp.get("answer_text", "")
        st.session_state["follow_up"] = resp.get("follow_up", "")

# -----------------------------------------------------------
# ANSWER DISPLAY
# -----------------------------------------------------------
answer_text = st.session_state.get("last_answer", "")

if answer_text:
    st.markdown(
        '<div class="answer-card">'
        '<div class="answer-header">✅ Answer</div>'
        f'<div class="answer-body">{answer_text}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    follow_up = st.session_state.get("follow_up", "")
    if follow_up:
        st.markdown('<div class="followup-label">Suggested follow-up</div>', unsafe_allow_html=True)
        fu_col1, fu_col2 = st.columns([4, 1.2])
        with fu_col1:
            st.markdown(f'<div class="followup-text">➜ *{follow_up}*</div>', unsafe_allow_html=True)
        with fu_col2:
            st.button(
                "Use this follow-up",
                key="use_follow_up_btn",
                on_click=use_follow_up,
                help="Copy this follow-up into the question box above.",
            )

    raw_result = st.session_state.get("last_raw_result", None)
    if raw_result is not None:
        with st.expander("See raw result"):
            if isinstance(raw_result, (pd.DataFrame, pd.Series)):
                st.dataframe(raw_result)
            else:
                st.write(raw_result)
