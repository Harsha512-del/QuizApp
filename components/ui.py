import streamlit as st


def load_css():
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def hero(title, subtitle):
    st.markdown(f"""
    <div class="custom-card" style="text-align:center;">
        <h1>{title}</h1>
        <p style="font-size:18px;color:#cbd5e1;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def section_card(title):
    st.markdown(f"""
    <div class="custom-card">
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)