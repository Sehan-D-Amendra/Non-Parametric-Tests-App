import pandas as pd
import streamlit as st
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from tempfile import NamedTemporaryFile

# Function for visualization
def generate_visualizations(data, col1, col2, selected_plots):
    visualizations = []
    
    if "Boxplot" in selected_plots:
        fig, ax = plt.subplots()
        sns.boxplot(data=data, x=col2, y=col1, ax=ax)
        visualizations.append(fig)
    
    if "Violin Plot" in selected_plots:
        fig, ax = plt.subplots()
        sns.violinplot(data=data, x=col2, y=col1, ax=ax)
        visualizations.append(fig)
    
    if "Distribution Plot" in selected_plots:
        fig, ax = plt.subplots()
        sns.histplot(data[col1], kde=True, ax=ax)
        if col2:
            sns.histplot(data[col2], kde=True, ax=ax, color="orange")
        visualizations.append(fig)
    
    return visualizations

# Streamlit app setup
st.title("Wilcoxon Signed-Rank Test with Visualization")

# File upload and data handling
uploaded_file = st.file_uploader("Upload Dataset", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    
    numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()
    
    col1 = st.selectbox("Select First Numeric Column", numeric_cols)
    col2 = st.selectbox("Select Second Numeric Column", numeric_cols)
    
    # Hypothesis input
    with st.expander("Hypothesis Setup"):
        null_hyp = st.text_input("Null Hypothesis (H0)", "No significant difference exists between paired samples.")
        alt_hyp = st.text_input("Alternative Hypothesis (H1)", "A significant difference exists between paired samples.")
    
    # Visualization options
    with st.expander("Visualization Options"):
        plot_options = ["Boxplot", "Violin Plot", "Distribution Plot"]
        selected_plots = st.multiselect("Select Visualizations", plot_options, default=plot_options[:2])
    
    # Run test
    if st.button("Run Wilcoxon Test"):
        try:
            stat, p_value = wilcoxon(data[col1], data[col2])
            
            st.subheader("Test Results")
            st.write(f"**Test Statistic:** {stat}")
            st.write(f"**p-value:** {p_value}")
            st.write(f"**Conclusion:** {'Reject H0' if p_value < 0.05 else 'Fail to reject H0'}")
            
            # Generate visualizations
            figs = generate_visualizations(data, col1, col2, selected_plots)
            for fig in figs:
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Error performing test: {str(e)}")
