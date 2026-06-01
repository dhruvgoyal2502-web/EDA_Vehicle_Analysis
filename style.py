import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
    /* Hide the top right menu and deploy button */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    header {background-color: transparent !important;}
    
    /* Reduce top padding since header is hidden */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Style metric cards with borders, colors, and hover effects */
    [data-testid="stMetricValue"] {
        color: #00d2ff;
        font-size: 28px;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(255,255,255,0.15);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #00d2ff;
        box-shadow: 0 8px 25px rgba(0,210,255,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
