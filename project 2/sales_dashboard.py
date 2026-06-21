import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Sales & Revenue Dashboard",
    layout="wide"
)

st.title("📊 Sales & Revenue Analysis Dashboard")

# File Upload
uploaded_file = st.file_uploader(
    "Upload Sales Data (CSV or Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file:

    # Read Data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Data Cleaning
    df.drop_duplicates(inplace=True)
    df.fillna(0, inplace=True)

    # Convert Date Column
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"])

    # Sidebar Filters
    st.sidebar.header("Filters")

    # Region Filter
    if "Region" in df.columns:
        regions = st.sidebar.multiselect(
            "Select Region",
            df["Region"].unique(),
            default=df["Region"].unique()
        )
        df = df[df["Region"].isin(regions)]

    # Category Filter
    if "Category" in df.columns:
        categories = st.sidebar.multiselect(
            "Select Category",
            df["Category"].unique(),
            default=df["Category"].unique()
        )
        df = df[df["Category"].isin(categories)]

    # Calculate Revenue if not available
    if "Revenue" not in df.columns:
        if "Quantity" in df.columns and "Unit Price" in df.columns:
            df["Revenue"] = df["Quantity"] * df["Unit Price"]

    # KPIs
    total_revenue = df["Revenue"].sum() if "Revenue" in df.columns else 0
    total_orders = len(df)
    avg_order = total_revenue / total_orders if total_orders > 0 else 0

    total_profit = (
        df["Profit"].sum()
        if "Profit" in df.columns else 0
    )

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}"
    )

    col2.metric(
        "Total Orders",
        total_orders
    )

    col3.metric(
        "Total Profit",
        f"${total_profit:,.2f}"
    )

    col4.metric(
        "Average Order Value",
        f"${avg_order:,.2f}"
    )

    st.divider()

    # Revenue Trend
    if "Order Date" in df.columns:
        revenue_trend = (
            df.groupby(
                df["Order Date"].dt.to_period("M")
            )["Revenue"]
            .sum()
            .reset_index()
        )

        revenue_trend["Order Date"] = (
            revenue_trend["Order Date"]
            .astype(str)
        )

        fig = px.line(
            revenue_trend,
            x="Order Date",
            y="Revenue",
            title="Monthly Revenue Trend",
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Top Products
    if "Product" in df.columns:
        product_sales = (
            df.groupby("Product")["Revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig = px.bar(
            product_sales,
            x="Revenue",
            y="Product",
            orientation="h",
            title="Top 10 Performing Products"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Sales by Region
    if "Region" in df.columns:
        region_sales = (
            df.groupby("Region")["Revenue"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            region_sales,
            names="Region",
            values="Revenue",
            title="Revenue by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Category Analysis
    if "Category" in df.columns:
        category_sales = (
            df.groupby("Category")["Revenue"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            category_sales,
            x="Category",
            y="Revenue",
            title="Revenue by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Display Raw Data
    with st.expander("View Dataset"):
        st.dataframe(df)

else:
    st.info("Please upload a CSV or Excel file to begin analysis.")