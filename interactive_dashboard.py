import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config for wider layout and custom title
st.set_page_config(page_title="Vehicle Dashboard", layout="wide")

import style
style.inject_custom_css()

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(r'C:\Users\dhruv\Downloads\synthetic_vehicle_dataset.csv')
        df['Billing_Date'] = pd.to_datetime(df['Billing_Date'], dayfirst=True)
        df['Billing_Quantity'] = df['Billing_Quantity'].astype(float).round(0).astype(int)
        df['Material_ID'] = df['Material_ID'].astype(str)
        df['Customer_ID'] = df['Customer_ID'].astype(str)
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data to display. Please check the dataset path.")
    st.stop()

# Sidebar Control Panel
st.sidebar.markdown("<h2 style='color: #00d2ff; text-align: center;'>Control Panel</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Date Filter
min_date = df['Billing_Date'].min().date()
max_date = df['Billing_Date'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Material Filter
materials = ['All'] + list(df['Material_ID'].unique())
selected_material = st.sidebar.multiselect("Select Material ID", materials, default='All')

# Customer Filter
customers = ['All'] + list(df['Customer_ID'].unique())
selected_customer = st.sidebar.multiselect("Select Customer ID", customers, default='All')


# Filter Data
mask = (df['Billing_Date'].dt.date >= start_date) & (df['Billing_Date'].dt.date <= end_date)
filtered_df = df.loc[mask]

if 'All' not in selected_material:
    filtered_df = filtered_df[filtered_df['Material_ID'].isin(selected_material)]

if 'All' not in selected_customer:
    filtered_df = filtered_df[filtered_df['Customer_ID'].isin(selected_customer)]


# Main Dashboard
st.markdown("<h1 style='color: #FF4B4B; border-bottom: 2px solid #1f77b4; padding-bottom: 10px;'>Vehicle Dashboard</h1>", unsafe_allow_html=True)

# Summary Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Records", len(filtered_df))
with col2:
    st.metric("Total Billing Quantity", f"{filtered_df['Billing_Quantity'].sum():,}")
with col3:
    st.metric("Unique Materials", filtered_df['Material_ID'].nunique())
with col4:
    st.metric("Unique Customers", filtered_df['Customer_ID'].nunique())

st.markdown("---")

# Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("<h3 style='color: #FF4B4B;'>Billing Quantity Over Time</h3>", unsafe_allow_html=True)
    if not filtered_df.empty:
        daily_qty = filtered_df.groupby('Billing_Date')['Billing_Quantity'].sum().reset_index()
        fig_time = px.line(daily_qty, x='Billing_Date', y='Billing_Quantity', 
                           title='Daily Total Billing Quantity', markers=True)
        fig_time.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with col_chart2:
    st.markdown("<h3 style='color: #FF4B4B;'>Top Materials by Volume</h3>", unsafe_allow_html=True)
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
    st.markdown("<h3 style='color: #FF4B4B;'>Top Customers by Volume</h3>", unsafe_allow_html=True)
    if not filtered_df.empty:
        cust_qty = filtered_df.groupby('Customer_ID')['Billing_Quantity'].sum().nlargest(10).reset_index()
        fig_cust = px.bar(cust_qty, x='Customer_ID', y='Billing_Quantity', 
                          title='Top 10 Customers', text_auto=True, color_discrete_sequence=['#2ca02c'])
        fig_cust.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
        st.plotly_chart(fig_cust, use_container_width=True)
    else:
        st.info("No data available.")

with col_chart4:
    st.markdown("<h3 style='color: #FF4B4B;'>Weekday vs Weekend Volume</h3>", unsafe_allow_html=True)
    if not filtered_df.empty:
        filtered_df['DayType'] = filtered_df['Billing_Date'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
        day_qty = filtered_df.groupby('DayType')['Billing_Quantity'].sum().reset_index()
        fig_day = px.pie(day_qty, names='DayType', values='Billing_Quantity', 
                         title='Quantity by Day Type', hole=0.4, color_discrete_sequence=['#00d2ff', '#FF4B4B'])
        fig_day.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
        st.plotly_chart(fig_day, use_container_width=True)
    else:
        st.info("No data available.")
