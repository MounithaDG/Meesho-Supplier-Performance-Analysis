
import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Meesho Supplier Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
df = pd.read_csv("data/supplier_summary.csv")

# Dashboard title
st.title("Meesho Supplier Performance Dashboard")
st.write("Analysis Period: April 2025 – September 2026")

st.divider()

# Supplier classification
df["Status"] = df["OTIF"].apply(
    lambda x: "Meets Target" if x >= 85 else "At Risk"
)

# KPI calculations
avg_otif = df["OTIF"].mean()
at_risk = (df["OTIF"] < 85).sum()
total_suppliers = df["Supplier ID"].nunique()

# KPI cards
st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("Average OTIF", f"{avg_otif:.2f}%")
col2.metric("Total Suppliers", total_suppliers)
col3.metric("At-Risk Suppliers", at_risk)

st.divider()

# Supplier OTIF chart
st.subheader("1. Supplier OTIF Performance")

fig1 = px.bar(
    df,
    x="Supplier ID",
    y="OTIF",
    color="Status",
    text="OTIF",
    title="Supplier-wise OTIF (%)"
)

fig1.add_hline(
    y=85,
    line_dash="dash",
    annotation_text="85% Target"
)

st.plotly_chart(fig1, use_container_width=True)

# Defect rate chart
st.subheader("2. Supplier Defect Rate")

fig2 = px.bar(
    df,
    x="Supplier ID",
    y="Defect Rate",
    text="Defect Rate",
    title="Supplier-wise Defect Rate (%)"
)

st.plotly_chart(fig2, use_container_width=True)

# Lead-time chart
st.subheader("3. Average Lead Time")

fig3 = px.bar(
    df,
    x="Supplier ID",
    y="Average Lead Time",
    title="Supplier-wise Average Lead Time"
)

st.plotly_chart(fig3, use_container_width=True)

# Supplier table
st.subheader("4. Supplier Performance Details")

st.dataframe(df.fillna("Not supplied"), use_container_width=True)
# Recommendations
st.subheader("5. Supplier Improvement Recommendations")

st.markdown("""
- **S003:** Focus on delivery delays, defect reduction and lead-time consistency.
- **S005:** Improve delivery reliability and strengthen quality checks.
- **All suppliers:** Monitor OTIF regularly against the 85% target.
""")

st.caption("Meesho Supplier Performance Analysis")
