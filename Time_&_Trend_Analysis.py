import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
st.set_page_config(page_title="Time & Trend Analysis", page_icon="📈", layout="wide")
import utils
df = utils.get_filtered_data()
if df.empty:
    st.warning("Please load data from the main Dashboard page first or check your data source.")
    st.stop()
zoom = st.session_state.get('zoom_level', 1.0)
st.title("Time & Trend Analysis")
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