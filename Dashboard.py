#(The main entry point and sidebar layout)
import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(
    page_title="Vehicle Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)
import style
style.inject_custom_css()

# ====================== DATA LOADING ======================
@st.cache_data
def load_data():
    file_path = 'synthetic_vehicle_dataset.csv'
    if not os.path.exists(file_path):
        st.error(f"Dataset not found at {file_path}. Please check the file path.")
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

df = load_data()

if df.empty:
    st.stop()

# ====================== SIDEBAR ======================
st.sidebar.title("Control Panel")
st.sidebar.markdown("Use these filters to instantly update the data across all pages in the dashboard.")

with st.sidebar.expander("ℹ️ About this Dashboard"):
    st.markdown("This dashboard provides an in-depth analytical view of **Vehicle Parts Billing Data**. Navigate through the pages on the left to uncover trends, outliers, and relationships.")

st.sidebar.markdown("---")
st.sidebar.subheader("Data Filters")

min_date = df['Billing_Date'].min().date()
max_date = df['Billing_Date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

selected_materials = st.sidebar.multiselect(
    "Filter Materials", 
    options=sorted(df['Material_ID'].unique()),
    default=[]
)

selected_customers = st.sidebar.multiselect(
    "Filter Customers", 
    options=sorted(df['Customer_ID'].unique()),
    default=[]
)

st.sidebar.markdown("---")
zoom_level = st.sidebar.slider("Chart Zoom Level (%)", min_value=50, max_value=200, value=100, step=10)
st.session_state['zoom_level'] = zoom_level / 100.0

# Store selected filters in session state so pages can access them
st.session_state['date_range'] = date_range
st.session_state['selected_materials'] = selected_materials
st.session_state['selected_customers'] = selected_customers

# ====================== FILTER DATA FOR GLOBAL DISPLAY ======================
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['Billing_Date'].dt.date >= start_date) & (df['Billing_Date'].dt.date <= end_date)
else:
    mask = df['Billing_Date'].dt.date == date_range[0]

if selected_materials:
    mask &= df['Material_ID'].isin(selected_materials)
if selected_customers:
    mask &= df['Customer_ID'].isin(selected_customers)

filtered_df = df[mask]
st.session_state['filtered_df'] = filtered_df

# ====================== MAIN PAGE ======================
st.title("🚗 Vehicle Parts Billing Dashboard")
st.markdown("""
Welcome to the Vehicle Parts Billing Dashboard. This application provides insights into 
billing quantities, customer behavior, and operational patterns. Use the sidebar to filter 
data, and navigate through the pages on the left for detailed visual analysis.
""")

st.subheader("Key Performance Indicators (Filtered)")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Records", f"{len(filtered_df):,}")
col2.metric("Total Quantity", f"{filtered_df['Billing_Quantity'].sum():,}")
col3.metric("Unique Customers", f"{filtered_df['Customer_ID'].nunique():,}")
col4.metric("Unique Materials", f"{filtered_df['Material_ID'].nunique():,}")
col5.metric("Avg Quantity/Transaction", f"{filtered_df['Billing_Quantity'].mean():.2f}")

st.divider()

# Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("<h3 style='color: #FF4B4B;'>📈 Billing Quantity Over Time</h3>", unsafe_allow_html=True)
    if not filtered_df.empty:
        daily_qty = filtered_df.groupby('Billing_Date')['Billing_Quantity'].sum().reset_index()
        fig_time = px.line(daily_qty, x='Billing_Date', y='Billing_Quantity', 
                           title='Daily Total Billing Quantity', markers=True)
        fig_time.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with col_chart2:
    st.markdown("<h3 style='color: #FF4B4B;'>📦 Top Materials by Volume</h3>", unsafe_allow_html=True)
    if not filtered_df.empty:
        mat_qty = filtered_df.groupby('Material_ID')['Billing_Quantity'].sum().nlargest(10).reset_index()
        fig_mat = px.bar(mat_qty, x='Material_ID', y='Billing_Quantity', 
                         title='Top 10 Materials', text_auto=True, color_discrete_sequence=['#1f77b4'])
        fig_mat.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
        st.plotly_chart(fig_mat, use_container_width=True)
    else:
        st.info("No data available.")

col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.markdown("<h3 style='color: #FF4B4B;'>🏆 Top Customers by Volume</h3>", unsafe_allow_html=True)
    if not filtered_df.empty:
        cust_qty = filtered_df.groupby('Customer_ID')['Billing_Quantity'].sum().nlargest(10).reset_index()
        fig_cust = px.bar(cust_qty, x='Customer_ID', y='Billing_Quantity', 
                          title='Top 10 Customers', text_auto=True, color_discrete_sequence=['#2ca02c'])
        fig_cust.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
        st.plotly_chart(fig_cust, use_container_width=True)
    else:
        st.info("No data available.")

with col_chart4:
    st.markdown("<h3 style='color: #FF4B4B;'>📅 Weekday vs Weekend Volume</h3>", unsafe_allow_html=True)
    if not filtered_df.empty:
        filtered_df['DayType'] = filtered_df['Billing_Date'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
        day_qty = filtered_df.groupby('DayType')['Billing_Quantity'].sum().reset_index()
        fig_day = px.pie(day_qty, names='DayType', values='Billing_Quantity', 
                         title='Quantity by Day Type', hole=0.4, color_discrete_sequence=['#00d2ff', '#FF4B4B'])
        fig_day.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
        st.plotly_chart(fig_day, use_container_width=True)
    else:
        st.info("No data available.")

st.markdown("---")
st.caption("Data is synced across all pages. Please use the sidebar to navigate for more detailed analysis.")
