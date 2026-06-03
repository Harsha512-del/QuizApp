import time
import streamlit as st


def start_timer(seconds=30):
    """
    Starts timer only once per question.
    """
    if "timer_start" not in st.session_state:
        st.session_state["timer_start"] = time.time()
        st.session_state["timer_limit"] = seconds


def remaining_seconds():
    """
    Returns remaining seconds.
    """
    if "timer_start" not in st.session_state:
        return 0

    elapsed = time.time() - st.session_state["timer_start"]
    limit = st.session_state.get("timer_limit", 30)

    return max(0, int(limit - elapsed))


def is_expired():
    """
    Returns True if timer finished.
    """
    return remaining_seconds() <= 0


def reset_timer():
    """
    Clears timer for next question.
    """
    st.session_state.pop("timer_start", None)
    st.session_state.pop("timer_limit", None)


def show_timer():
    """
    Displays timer without forcing reruns.
    """
    remaining = remaining_seconds()
    limit = st.session_state.get("timer_limit", 30)

    progress_value = remaining / limit if limit > 0 else 0

    st.progress(progress_value)

    col1, col2 = st.columns([4, 1])

    with col2:
        if remaining <= 5:
            st.error(f"{remaining}s")
        elif remaining <= 10:
            st.warning(f"{remaining}s")
        else:
            st.info(f"{remaining}s")

    return remaining