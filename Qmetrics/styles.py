def custom_css():
    """Inject custom CSS to hide Streamlit's branding and control elements."""
    return """
    <style>
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        background-color: #4CAF50; /* Green */
        border: none;
        color: white;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .css-1v0mbdj { 
        border-radius: 10px;
        background-color: #f7f7f7;
        padding: 1rem;
        }
    </style>
    """
