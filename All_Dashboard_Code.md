# Complete Dashboard Source Code


### style.py
`python

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
``n

### utils.py
`python

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
``n

### Dashboard.py
`python

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
``n

### interactive_dashboard.py
`python

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
``n

### pages\1_??_Time_&_Trend_Analysis.py
`python

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Time & Trend Analysis", page_icon="📈", layout="wide")

import style
import utils
style.inject_custom_css()

df = utils.get_filtered_data()
if df.empty:
    st.warning("Please load data from the main Dashboard page first or check your data source.")
    st.stop()

zoom = st.session_state.get('zoom_level', 1.0)

st.title("📈 Time & Trend Analysis")

if df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# 1. Monthly Quantity vs Order Count
st.subheader("Monthly Volume & Frequency")
monthly_qty = df.groupby('YearMonth')['Billing_Quantity'].sum()
monthly_cnt = df.groupby('YearMonth')['Billing_Quantity'].count()

fig_monthly = go.Figure()
fig_monthly.add_trace(go.Bar(
    x=monthly_qty.index, y=monthly_qty.values, 
    name="Total Quantity", marker_color="#1f77b4"
))
fig_monthly.add_trace(go.Scatter(
    x=monthly_cnt.index, y=monthly_cnt.values, 
    name="Order Count", mode='lines+markers', line=dict(color="red"),
    yaxis="y2"
))
fig_monthly.update_layout(
    title="Monthly Quantity vs Order Count",
    yaxis=dict(title="Total Quantity"),
    yaxis2=dict(title="Order Count", overlaying="y", side="right"),
    hovermode="x unified",
    margin=dict(l=10, r=10, t=40, b=10),
    height=int(400 * zoom)
)
st.plotly_chart(fig_monthly, use_container_width=True)

# 2. Weekday vs Weekend and Day of Week Pattern
col1, col2 = st.columns(2)

with col1:
    st.subheader("Weekday vs Weekend")
    day_type = df.groupby('DayType')['Billing_Quantity'].sum().reset_index()
    fig_day_type = px.bar(
        day_type, x='DayType', y='Billing_Quantity', 
        color='DayType', title='Total Billing Quantity by Day Type',
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    fig_day_type.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(350 * zoom))
    st.plotly_chart(fig_day_type, use_container_width=True)

with col2:
    st.subheader("Day of Week Pattern")
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow = df.groupby('DayOfWeek')['Billing_Quantity'].sum().reindex(days_order).reset_index()
    fig_dow = px.bar(
        dow, x='DayOfWeek', y='Billing_Quantity', 
        title='Billing by Day of Week',
        color_discrete_sequence=['#2ca02c']
    )
    fig_dow.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(350 * zoom))
    st.plotly_chart(fig_dow, use_container_width=True)

# 3. Month-over-Month Growth
st.subheader("Month-over-Month Growth Rate (%)")
mom_growth = monthly_qty.pct_change() * 100
mom_df = mom_growth.reset_index().rename(columns={'Billing_Quantity': 'Growth_Percent'}).dropna()
mom_df['Color'] = mom_df['Growth_Percent'].apply(lambda x: 'Positive' if x >= 0 else 'Negative')

fig_mom = px.bar(
    mom_df, x='YearMonth', y='Growth_Percent', color='Color',
    color_discrete_map={'Positive': 'green', 'Negative': 'red'},
    title="Month-over-Month Growth Rate"
)
fig_mom.add_hline(y=0, line_dash="dash", line_color="black")
fig_mom.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(350 * zoom))
st.plotly_chart(fig_mom, use_container_width=True)

# 4. Trend for Top 5 Materials Over Time
st.subheader("Monthly Trend - Top Materials")
top_n = st.slider("Select number of top materials to track", min_value=3, max_value=10, value=5)
top_materials = df.groupby('Material_ID')['Billing_Quantity'].sum().nlargest(top_n).index.tolist()

df_top = df[df['Material_ID'].isin(top_materials)]
monthly_mat = df_top.groupby(['YearMonth', 'Material_ID'])['Billing_Quantity'].sum().reset_index()

fig_trend = px.line(
    monthly_mat, x='YearMonth', y='Billing_Quantity', color='Material_ID',
    markers=True, title=f"Trend for Top {top_n} Materials Over Time"
)
fig_trend.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(400 * zoom))
st.plotly_chart(fig_trend, use_container_width=True)
``n

### pages\2_??_Distributions_&_Outliers.py
`python

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(page_title="Distributions & Outliers", page_icon="📊", layout="wide")

import style
import utils
style.inject_custom_css()

df = utils.get_filtered_data()
if df.empty:
    st.warning("Please load data from the main Dashboard page first or check your data source.")
    st.stop()

zoom = st.session_state.get('zoom_level', 1.0)

st.title("📊 Distributions & Outliers")

if df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# 1. Billing Quantity Distribution & Box Plot
st.subheader("Billing Quantity Distribution")
col1, col2 = st.columns([3, 2])

with col1:
    fig_hist = px.histogram(
        df, x="Billing_Quantity", nbins=50, 
        marginal="box", # Adds a box plot on top
        title="Billing Quantity Histogram",
        color_discrete_sequence=['#1f77b4']
    )
    fig_hist.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(400 * zoom))
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_box = px.box(
        df, y="Billing_Quantity", 
        title="Billing Quantity Box Plot (Outliers)",
        color_discrete_sequence=['#ff7f0e']
    )
    fig_box.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(400 * zoom))
    st.plotly_chart(fig_box, use_container_width=True)

# 2. Outlier Detection
st.subheader("Outlier Analysis")
Q1 = df['Billing_Quantity'].quantile(0.25)
Q3 = df['Billing_Quantity'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df['Billing_Quantity'] < lower_bound) | (df['Billing_Quantity'] > upper_bound)]
outlier_pct = len(outliers) / len(df) * 100

st.info(f"""
**Outlier Metrics:**
- **Lower Bound:** {lower_bound:.2f}
- **Upper Bound:** {upper_bound:.2f}
- **Total Outliers:** {len(outliers):,} ({outlier_pct:.2f}% of total data)
""")

if not outliers.empty:
    with st.expander("View Outlier Data"):
        st.dataframe(outliers.sort_values(by='Billing_Quantity', ascending=False), use_container_width=True)

# 3. Statistical Summary
st.subheader("Statistical Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean", f"{df['Billing_Quantity'].mean():.2f}")
c2.metric("Median", f"{df['Billing_Quantity'].median():.2f}")
c3.metric("Skewness", f"{df['Billing_Quantity'].skew():.4f}", help=">0: Right-skewed, <0: Left-skewed")
c4.metric("Kurtosis", f"{df['Billing_Quantity'].kurt():.4f}", help=">3: Heavy-tailed, <3: Light-tailed")
``n

### pages\3_??_Categorical_Analysis.py
`python

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Categorical Analysis", page_icon="🏆", layout="wide")

import style
import utils
style.inject_custom_css()

df = utils.get_filtered_data()
if df.empty:
    st.warning("Please load data from the main Dashboard page first or check your data source.")
    st.stop()

zoom = st.session_state.get('zoom_level', 1.0)

st.title("🏆 Categorical Analysis & Top Performers")

if df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# Interactive Slider for Top N
top_n = st.slider("Select Top N items to display", min_value=5, max_value=50, value=20)

# 1. Top Customers and Materials
st.subheader(f"Top {top_n} Performers")
col1, col2 = st.columns(2)

with col1:
    top_cust = df.groupby('Customer_ID')['Billing_Quantity'].sum().nlargest(top_n).reset_index()
    fig_cust = px.bar(
        top_cust, x='Customer_ID', y='Billing_Quantity', 
        title=f"Top {top_n} Customers by Volume",
        color='Billing_Quantity', color_continuous_scale='Blues'
    )
    fig_cust.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(400 * zoom))
    st.plotly_chart(fig_cust, use_container_width=True)

with col2:
    top_mat = df.groupby('Material_ID')['Billing_Quantity'].sum().nlargest(top_n).reset_index()
    fig_mat = px.bar(
        top_mat, x='Material_ID', y='Billing_Quantity', 
        title=f"Top {top_n} Materials by Volume",
        color='Billing_Quantity', color_continuous_scale='Greens'
    )
    fig_mat.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(400 * zoom))
    st.plotly_chart(fig_mat, use_container_width=True)

# 2. Pareto Analysis (80/20 Rule)
st.subheader("Pareto Analysis - Customer Contribution (80/20 Rule)")
cust_sorted = df.groupby('Customer_ID')['Billing_Quantity'].sum().sort_values(ascending=False)
cust_cumulative = (cust_sorted.cumsum() / cust_sorted.sum() * 100)

fig_pareto = go.Figure()
fig_pareto.add_trace(go.Scatter(
    x=list(range(len(cust_cumulative))), 
    y=cust_cumulative.values,
    mode='lines', name='Cumulative %', line=dict(color="darkblue", width=2)
))
fig_pareto.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% Threshold")
fig_pareto.update_layout(
    title="Cumulative Customer Contribution to Total Billing Quantity",
    xaxis_title="Number of Customers (Ranked)",
    yaxis_title="Cumulative %",
    hovermode="x unified",
    margin=dict(l=10, r=10, t=40, b=10),
    height=int(350 * zoom)
)
st.plotly_chart(fig_pareto, use_container_width=True)

# Business insight
cutoff = (cust_cumulative <= 80).sum()
st.success(f"**Insight:** The top **{cutoff:,}** customers contribute 80% of the total billing quantity.")

# 3. Order Frequency Distribution
st.subheader("Order Frequency per Customer")
order_counts = df.groupby('Customer_ID')['Billing_Quantity'].count().reset_index()
fig_freq = px.histogram(
    order_counts, x="Billing_Quantity", nbins=50,
    title="Distribution of Order Frequency per Customer",
    labels={'Billing_Quantity': 'Number of Orders'},
    color_discrete_sequence=['purple']
)
fig_freq.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(350 * zoom))
st.plotly_chart(fig_freq, use_container_width=True)
``n

### pages\4_??_Relationships_&_Heatmaps.py
`python

import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Relationships & Heatmaps", page_icon="🔥", layout="wide")

import style
import utils
style.inject_custom_css()

df = utils.get_filtered_data()
if df.empty:
    st.warning("Please load data from the main Dashboard page first or check your data source.")
    st.stop()

zoom = st.session_state.get('zoom_level', 1.0)

st.title("🔥 Relationships & Heatmaps")

if df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# 1. Month vs Day of Week Heatmap
st.subheader("Billing Quantity: Month vs Day of Week")
pivot = df.groupby(['Month', 'DayOfWeek'])['Billing_Quantity'].sum().unstack()
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Filter existing columns and indexes to avoid KeyError
existing_days = [day for day in days_order if day in pivot.columns]
existing_months = [month for month in months_order if month in pivot.index]
pivot = pivot.loc[existing_months, existing_days]

fig_heatmap1 = px.imshow(
    pivot, 
    text_auto=False, 
    aspect="auto",
    title="Billing Quantity Heatmap — Month vs Day of Week",
    color_continuous_scale='YlOrRd'
)
fig_heatmap1.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(400 * zoom))
st.plotly_chart(fig_heatmap1, use_container_width=True)

# 2. Customer vs Material Heatmap
st.subheader("Customer × Material Relationship")
top_n = st.slider("Select Top N for Matrix", min_value=5, max_value=50, value=20)

top_custs = df.groupby('Customer_ID')['Billing_Quantity'].sum().nlargest(top_n).index
top_mats = df.groupby('Material_ID')['Billing_Quantity'].sum().nlargest(top_n).index

cross = df[df['Customer_ID'].isin(top_custs) & df['Material_ID'].isin(top_mats)]
pivot_cm = cross.pivot_table(index='Customer_ID', columns='Material_ID', values='Billing_Quantity', aggfunc='sum', fill_value=0)

fig_heatmap2 = px.imshow(
    pivot_cm, 
    text_auto=False, 
    aspect="auto",
    title=f"Customer × Material Heatmap (Top {top_n} each)",
    color_continuous_scale='Viridis'
)
fig_heatmap2.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(500 * zoom))
st.plotly_chart(fig_heatmap2, use_container_width=True)

# 3. Scatter Plot Relationship (Customer Aggregates)
st.subheader("Quantity vs Order Frequency per Customer")
customer_stats = df.groupby('Customer_ID').agg(
    total_quantity=('Billing_Quantity', 'sum'),
    order_count=('Billing_Quantity', 'count')
).reset_index()

fig_scatter = px.scatter(
    customer_stats, x='order_count', y='total_quantity', 
    hover_data=['Customer_ID'],
    title="Customer Relationship: Order Count vs Total Quantity",
    labels={'order_count': 'Number of Orders', 'total_quantity': 'Total Quantity'},
    color_discrete_sequence=['#1f77b4'],
    opacity=0.6
)
fig_scatter.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=int(400 * zoom))
st.plotly_chart(fig_scatter, use_container_width=True)
``n

