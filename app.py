"""
app.py — Point d'entrée. Lance : streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="malviz",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.switch_page("pages/1_Home.py")