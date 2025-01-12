# config.py
import streamlit as st

def configure_page():
    """Set up the page title and layout for the Streamlit app."""
    st.set_page_config(page_title="📈 Professional Trading Dashboard", layout="wide")

def inject_custom_css():
    """Inject custom CSS to modify the Streamlit UI appearance."""
    st.markdown(
        """
        <style>
        /* Sidebar background color */
        .css-1d391kg { background-color: #2C2C2C; }
        .css-1kyxreq.edgvbvh3 { color: #FFFFFF; }
        /* Main content background color */
        .css-18e3th9 { background-color: #F0F2F6; }
        ::-webkit-scrollbar { width: 12px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background: #888; border-radius: 6px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }
        /* Custom Font */
        @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue&display=swap');
        body, div, h1, h2, h3, h4, h5, h6, p, span, a {
            font-family: 'Helvetica Neue', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
