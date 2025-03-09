import streamlit as st

def arabic_support_custom():
    """
    Add Arabic right-to-left support for the Streamlit application.
    This function injects custom CSS to properly display Arabic text.
    """
    st.markdown(
    """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Readex+Pro:wght@160..700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@610&display=swap');    /* Main page direction */
    .main, .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Readex Pro', sans-serif;
    }
        
    /* Data tables */
    .dataframe {
        direction: rtl;
        text-align: right;
    }
    
    /* Streamlit specific components */
    .stSelectbox, .stTextInput, .stButton, .stExpander {
        direction: rtl;
        text-align: right;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        direction: rtl;
        text-align: right !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-family: 'Readex Pro', sans-serif;
    }
    
    /* Apply to all text elements */
    * {
        font-family: 'Readex Pro', sans-serif;
        
        
    }
    </style>
    """,
    unsafe_allow_html=True,
    )
