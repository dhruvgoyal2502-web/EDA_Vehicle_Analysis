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
