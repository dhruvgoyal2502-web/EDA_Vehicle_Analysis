# (Handles the data loading and filtering)
import streamlit as st
import pandas as pd
import os

def inject_custom_css():
    st.markdown("""
    <style>
    /* Hide the top right menu and deploy button */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
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

@st.cache_data
def load_data():
    file_path = 'synthetic_vehicle_dataset.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    df['Billing_Date'] = pd.to_datetime(df['Billing_Date'], dayfirst=True)
    df['Billing_Quantity'] = df['Billing_Quantity'].astype(float).round(0).astype(int)
    df['Material_ID'] = df['Material_ID'].astype(str)
    df['Customer_ID'] = df['Customer_ID'].astype(str)
    
    # Precompute common time-based features
    df['YearMonth'] = df['Billing_Date'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['Billing_Date'].dt.day_name()
    df['Month'] = df['Billing_Date'].dt.month_name()
    df['Year'] = df['Billing_Date'].dt.year
    df['DayType'] = df['Billing_Date'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
    
    return df
def get_filtered_data():
    df = load_data()
    if df.empty:
        return df
        
    if 'date_range' in st.session_state and len(st.session_state['date_range']) == 2:
        start_date, end_date = st.session_state['date_range']
        mask = (df['Billing_Date'].dt.date >= start_date) & (df['Billing_Date'].dt.date <= end_date)
    elif 'date_range' in st.session_state and len(st.session_state['date_range']) == 1:
        mask = df['Billing_Date'].dt.date == st.session_state['date_range'][0]
    else:
        mask = pd.Series(True, index=df.index)
    if 'selected_materials' in st.session_state and st.session_state['selected_materials']:
        mask &= df['Material_ID'].isin(st.session_state['selected_materials'])
    if 'selected_customers' in st.session_state and st.session_state['selected_customers']:
        mask &= df['Customer_ID'].isin(st.session_state['selected_customers'])
    return df[mask]