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
