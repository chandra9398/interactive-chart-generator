import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import re

# Set default data folder
DATA_FOLDER = os.path.join(os.getcwd(), "data")

# App Header
st.title("Interactive Chart Generator with Matplotlib and Seaborn")
st.markdown("Upload your dataset and generate interactive charts using Matplotlib and Seaborn.")

# File uploader with default folder browsing
uploaded_file = st.file_uploader("Choose a CSV or Excel file from the 'data' folder:", type=["csv", "xlsx"], key="file_uploader")

# User input for chart customization
st.subheader("Custom Query for Chart Generation")
custom_query = st.text_input("Describe the chart you want (e.g., 'Bar chart of Sales vs Year'):")

if uploaded_file:
    try:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        df = pd.read_csv(uploaded_file) if file_ext == 'csv' else pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()
    
    if df.empty:
        st.error("The uploaded file is empty. Please provide a valid dataset.")
        st.stop()

    # Show dataset preview
    st.subheader("Dataset Preview")
    st.dataframe(df)

    # Try to infer chart type and columns from the query
    inferred_chart = "Bar Chart"
    inferred_x, inferred_y = None, None
    
    if custom_query:
        query_lower = custom_query.lower()
        
        if "bar chart" in query_lower:
            inferred_chart = "Bar Chart"
        elif "line chart" in query_lower:
            inferred_chart = "Line Chart"
        elif "scatter plot" in query_lower:
            inferred_chart = "Scatter Plot"
        elif "histogram" in query_lower:
            inferred_chart = "Histogram"
        elif "count plot" in query_lower:
            inferred_chart = "Count Plot"
        
        columns = df.columns.tolist()
        matches = re.findall(r'\b(' + '|'.join(columns) + r')\b', custom_query, re.IGNORECASE)
        
        if len(matches) >= 1:
            inferred_x = matches[0]
        if len(matches) >= 2:
            inferred_y = matches[1]
    
    # Column selection
    st.subheader("Select Columns")
    x_col = st.selectbox("X-axis Column", df.columns, index=df.columns.get_loc(inferred_x) if inferred_x in df.columns else 0)
    y_col = st.selectbox("Y-axis Column", df.columns, index=df.columns.get_loc(inferred_y) if inferred_y in df.columns else 0)
    
    # Chart type selection
    st.subheader("Choose Chart Type")
    chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Count Plot"], index=["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Count Plot"].index(inferred_chart) if inferred_chart else 0)
    
    # Auto-generate chart when query is entered
    if custom_query or st.button("Create Chart"):
        if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot"] and not pd.api.types.is_numeric_dtype(df[y_col]):
            st.error(f"'{y_col}' must be numeric for {chart_type}.")
        elif chart_type == "Histogram" and not pd.api.types.is_numeric_dtype(df[x_col]):
            st.error(f"'{x_col}' must be numeric for a histogram.")
        else:
            sns.set(style="darkgrid")
            fig, ax = plt.subplots(figsize=(10, 5))

            if chart_type == "Bar Chart":
                sns.barplot(x=df[x_col], y=df[y_col], ax=ax)
            elif chart_type == "Line Chart":
                sns.lineplot(x=df[x_col], y=df[y_col], ax=ax)
            elif chart_type == "Scatter Plot":
                sns.scatterplot(x=df[x_col], y=df[y_col], ax=ax)
            elif chart_type == "Histogram":
                sns.histplot(df[x_col], kde=True, ax=ax)
            elif chart_type == "Count Plot":
                sns.countplot(x=df[x_col], ax=ax)

            plt.xticks(rotation=45)
            fig.tight_layout()
            st.pyplot(fig)

            # Download chart
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format="png")
            img_buf.seek(0)
            st.download_button("Download Chart", data=img_buf, file_name="chart.png", mime="image/png")
    
    # Dataset download option
    st.subheader("Download Dataset")
    format_option = st.selectbox("Select format", ["CSV", "Excel"])
    if format_option == "CSV":
        csv_data = df.to_csv(index=False)
        st.download_button("Download CSV", data=csv_data, file_name="dataset.csv", mime="text/csv")
    else:
        excel_data = df.to_excel(index=False)
        st.download_button("Download Excel", data=excel_data, file_name="dataset.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
