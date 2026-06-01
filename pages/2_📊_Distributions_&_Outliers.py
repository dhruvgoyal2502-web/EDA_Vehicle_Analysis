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
