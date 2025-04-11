# %% 
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Filtered Chart Viewer", layout="centered")
st.title("📊 Filtered Chart Viewer")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
chart_type = st.selectbox("Select chart type", ["Line", "Bar", "Area", "Scatter", "Histogram"])

if uploaded_file:
    try:
        # Load data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.success("CSV file uploaded successfully!")
        else:
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            sheet_name = st.selectbox("Select sheet", sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            st.success(f"Sheet '{sheet_name}' loaded successfully!")

        if df.shape[1] < 2:
            st.error("The file must have at least two columns.")
        else:
            # Convert columns that look like dates
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass

            st.subheader("🧰 Optional Filters")
            filterable_cols = df.select_dtypes(include=["object", "category", "datetime64[ns]"]).columns.tolist()

            for col in filterable_cols:
                unique_vals = df[col].dropna().unique()
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    min_date, max_date = df[col].min(), df[col].max()
                    date_range = st.date_input(f"Filter by {col}", [min_date, max_date])
                    if isinstance(date_range, list) and len(date_range) == 2:
                        df = df[(df[col] >= pd.to_datetime(date_range[0])) & (df[col] <= pd.to_datetime(date_range[1]))]
                else:
                    selected = st.multiselect(f"Filter by {col}", options=sorted(unique_vals), default=sorted(unique_vals))
                    df = df[df[col].isin(selected)]

            # Column selection
            st.subheader("📌 Choose Columns to Plot")
            col_options = df.columns.tolist()
            x_col = st.selectbox("X-axis", col_options, index=0)

            if chart_type in ["Histogram"]:
                y_col = st.selectbox("Data column", col_options, index=1)
            else:
                y_col = st.selectbox("Y-axis", col_options, index=1)

            # Plot
            fig, ax = plt.subplots()

            if chart_type == "Line":
                ax.plot(df[x_col], df[y_col], marker='o')
            elif chart_type == "Bar":
                ax.bar(df[x_col], df[y_col])
            elif chart_type == "Area":
                ax.fill_between(df[x_col], df[y_col], alpha=0.5)
            elif chart_type == "Scatter":
                ax.scatter(df[x_col], df[y_col])
            elif chart_type == "Histogram":
                ax.hist(df[y_col], bins=20, alpha=0.7)

            ax.set_title(f"{chart_type} Chart")
            if chart_type != "Histogram":
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
            else:
                ax.set_xlabel(y_col)
                ax.set_ylabel("Frequency")

            ax.grid(True)
            st.pyplot(fig)

            # Download
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("📥 Download Chart as PNG", data=buf.getvalue(), file_name="chart.png", mime="image/png")

            # Data preview
            st.subheader("📋 Filtered Data Preview")
            st.dataframe(df[[x_col, y_col]] if chart_type != "Histogram" else df[[y_col]])

    except Exception as e:
        st.error(f"An error occurred: {e}")