import streamlit as st
import pandas as pd
from utils.handle_missing import handle_missing_values
from utils.remove_duplicates import remove_duplicates
from utils.standardize_text import standardize_text
from utils.correct_inconsistent import correct_inconsistent_data
from utils.change_datatype import change_data_type
from utils.handle_format import handle_data_format
from utils.enforce_integrity import enforce_data_integrity
from utils.handle_numeric import handle_numeric_data

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
        if option == "Fill missing values":
            fill_option = st.selectbox(
                "Choose fill method:",
                ["Custom Value", "Mean", "Median", "Mode"]
            )
            if fill_option == "Custom Value":
                fill_value = st.text_input("Enter value to fill missing data:")
            else:
                fill_value = fill_option.lower()
        else:
            fill_value = None
        if st.button("Apply Missing Value Handling"):
            df = handle_missing_values(df, option, fill_value)
            st.write("Updated Dataset:")
            st.write(df)

    # Remove Duplicates
    if st.checkbox("Remove Duplicates"):
        st.write("### Remove Duplicates")
        if st.button("Remove Duplicates"):
            df = remove_duplicates(df)
            st.write("Updated Dataset:")
            st.write(df)

    # Standardize Text
    if st.checkbox("Standardize Text"):
        st.write("### Standardize Text")
        text_column = st.selectbox("Select text column to standardize:", df.columns)
        if st.button("Standardize"):
            df = standardize_text(df, text_column)
            st.write("Updated Dataset:")
            st.write(df)

    # Correct Inconsistent Data
    if st.checkbox("Correct Inconsistent Data"):
        st.write("### Correct Inconsistent Data")
        column = st.selectbox("Select column to correct:", df.columns)
        old_value = st.text_input("Enter the value to replace:")
        new_value = st.text_input("Enter the new value:")
        if st.button("Replace"):
            df = correct_inconsistent_data(df, column, old_value, new_value)
            st.write("Updated Dataset:")
            st.write(df)

    # Change Data Type
    if st.checkbox("Change Data Type"):
        st.write("### Change Data Type")
        column = st.selectbox("Select column to change data type:", df.columns)
        new_type = st.selectbox(
            "Select new data type:",
            ["String", "Integer", "Float", "Datetime"]
        )
        if st.button("Change"):
            df = change_data_type(df, column, new_type)
            st.write("Updated Dataset:")
            st.write(df)

    # Handle Data Format Issues
    if st.checkbox("Handle Data Format Issues"):
        st.write("### Handle Data Format Issues")
        column = st.selectbox("Select column to fix formatting:", df.columns)
        format_type = st.selectbox(
            "Select format type:",
            ["Date", "Phone Number"]
        )
        if format_type == "Date":
            date_format = st.text_input("Enter date format (e.g., YYYY-MM-DD):")
        if st.button("Fix Format"):
            df = handle_data_format(df, column, format_type, date_format if format_type == "Date" else None)
            st.write("Updated Dataset:")
            st.write(df)

    # Enforce Data Integrity
    if st.checkbox("Enforce Data Integrity"):
        st.write("### Enforce Data Integrity")
        column = st.selectbox("Select column to enforce rules:", df.columns)
        rule = st.selectbox(
            "Select rule:",
            ["Email Validation", "Numeric Range"]
        )
        if rule == "Numeric Range":
            min_value = st.number_input("Enter minimum value:")
            max_value = st.number_input("Enter maximum value:")
        if st.button("Apply Rule"):
            df = enforce_data_integrity(df, column, rule, min_value if rule == "Numeric Range" else None, max_value if rule == "Numeric Range" else None)
            st.write("Updated Dataset:")
            st.write(df)

    # Handle Numeric Data
    if st.checkbox("Handle Numeric Data"):
        st.write("### Handle Numeric Data")
        column = st.selectbox("Select numeric column:", df.select_dtypes(include=['number']).columns)
        operation = st.selectbox(
            "Select operation:",
            ["Scale", "Normalize", "Round"]
        )
        if operation == "Scale":
            scale_factor = st.number_input("Enter scale factor:")
        elif operation == "Round":
            decimals = st.number_input("Enter number of decimal places:", min_value=0, max_value=10, value=2)
        if st.button("Apply Operation"):
            df = handle_numeric_data(df, column, operation, scale_factor if operation == "Scale" else None, decimals if operation == "Round" else None)
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