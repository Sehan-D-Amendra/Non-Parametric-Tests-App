import streamlit as st
import pandas as pd

# Title of the app
st.title("Data Cleaning App")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Read the file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Show the dataset
    st.write("### Dataset Preview")
    st.write(df)

    # Show key features of the dataset
    st.write("### Key Features")
    st.write(f"Number of Rows: {df.shape[0]}")
    st.write(f"Number of Columns: {df.shape[1]}")
    st.write("Columns and Data Types:")
    st.write(df.dtypes)

    # Handle Missing Values
    if st.checkbox("Handle Missing Values"):
        st.write("### Handle Missing Values")
        option = st.selectbox(
            "Choose an option:",
            ["Remove rows with missing values", "Fill missing values"]
        )

        if option == "Remove rows with missing values":
            df = df.dropna()
        else:
            fill_value = st.text_input("Enter value to fill missing data (e.g., 0, mean, median):")
            if fill_value == "mean":
                df = df.fillna(df.mean())
            elif fill_value == "median":
                df = df.fillna(df.median())
            else:
                df = df.fillna(fill_value)

        st.write("Updated Dataset:")
        st.write(df)

    # Remove Duplicates
    if st.checkbox("Remove Duplicates"):
        st.write("### Remove Duplicates")
        df = df.drop_duplicates()
        st.write("Updated Dataset:")
        st.write(df)

    # Rename Columns
    if st.checkbox("Rename Columns"):
        st.write("### Rename Columns")
        old_name = st.selectbox("Select column to rename:", df.columns)
        new_name = st.text_input("Enter new column name:")
        if st.button("Rename"):
            df = df.rename(columns={old_name: new_name})
            st.write("Updated Dataset:")
            st.write(df)

    # Filter Data
    if st.checkbox("Filter Data"):
        st.write("### Filter Data")
        column = st.selectbox("Select column to filter:", df.columns)
        filter_value = st.text_input(f"Enter value to filter by in column '{column}':")
        if st.button("Apply Filter"):
            df = df[df[column] == filter_value]
            st.write("Updated Dataset:")
            st.write(df)

    # Download Cleaned Data
    if st.button("Download Cleaned Data"):
        st.write("### Download Cleaned Data")
        file_format = st.selectbox("Choose file format:", ["CSV", "Excel"])
        if file_format == "CSV":
            df.to_csv("cleaned_data.csv", index=False)
            st.download_button(
                label="Download CSV",
                data=open("cleaned_data.csv", "rb").read(),
                file_name="cleaned_data.csv",
                mime="text/csv"
            )
        else:
            df.to_excel("cleaned_data.xlsx", index=False)
            st.download_button(
                label="Download Excel",
                data=open("cleaned_data.xlsx", "rb").read(),
                file_name="cleaned_data.xlsx",
                mime="application/vnd.ms-excel"
            )