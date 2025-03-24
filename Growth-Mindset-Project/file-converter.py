import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from sklearn.impute import SimpleImputer

# Streamlit UI Setup
st.set_page_config(page_title="Smart File Converter", layout="wide")
st.title("📂 Smart File Converter & Data Cleaner")
st.write("Upload CSV or Excel files to convert them and enhance data quality.")

# File Upload
files = st.file_uploader("Upload CSV or Excel Files", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1].lower()
        df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)

        st.subheader(f"📄 Preview: {file.name}")
        st.dataframe(df.head())

        # Show Summary Statistics
        if st.checkbox(f"Show Summary - {file.name}"):
            st.write(df.describe())

        # Remove Duplicates
        if st.checkbox(f"Remove Duplicates - {file.name}"):
            df = df.drop_duplicates()
            st.success("✅ Duplicates Removed.")
            st.dataframe(df.head())

        # Fill Missing Values (Numerical Columns Only)
        num_cols = df.select_dtypes(include=["number"]).columns
        if not num_cols.empty and st.checkbox(f"Fill Missing Values - {file.name}"):
            imputer = SimpleImputer(strategy="mean")
            df[num_cols] = imputer.fit_transform(df[num_cols])
            st.success("✅ Missing values filled with mean.")
            st.dataframe(df.head())

        # Show Correlation Heatmap
        if not num_cols.empty and st.checkbox(f"Show Correlation Heatmap - {file.name}"):
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            st.pyplot(fig)

        # Column Selection
        selected_columns = st.multiselect(f"Select Columns for {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]
        st.dataframe(df.head())

        # Chart Visualization (if numeric data exists)
        if not df.select_dtypes(include="number").empty and st.checkbox(f"Show Chart - {file.name}"):
            st.bar_chart(df.select_dtypes(include="number").iloc[:, :2])

        # File Conversion
        format_choice = st.radio(f"Convert {file.name} to", ["CSV", "Excel"], key=file.name)

        if st.button(f"Download {file.name} as {format_choice}"):
            output = BytesIO()
            new_ext = "csv" if format_choice == "CSV" else "xlsx"
            new_name = f"{file.name.rsplit('.', 1)[0]}.{new_ext}"

            if format_choice == "CSV":
                df.to_csv(output, index=False)
                mime = "text/csv"
            else:
                df.to_excel(output, index=False, engine="openpyxl")
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            output.seek(0)
            st.download_button(label=f"⬇️ Download {new_name}", data=output, file_name=new_name, mime=mime)

        st.success("✅ Process Completed.")