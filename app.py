import pandas as pd
import streamlit as st
from scipy.stats import (
    wilcoxon, mannwhitneyu, kruskal, friedmanchisquare, spearmanr, kendalltau, ks_2samp
)
from statsmodels.sandbox.stats.runs import runstest_1samp
from statsmodels.stats.proportion import binom_test
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from tempfile import NamedTemporaryFile
import base64

# Enhanced test suggestion function
def suggest_tests(data, col1, col2=None):
    suggestions = []
    
    if col2:
        # Check if paired data (same number of observations)
        is_paired = len(data[col1]) == len(data[col2])
        
        # Two-sample tests
        suggestions.extend(["Mann-Whitney U Test", "Kolmogorov-Smirnov Test"])
        
        if is_paired:
            suggestions.append("Wilcoxon Signed-Rank Test")
        
        # Correlation tests
        if pd.api.types.is_numeric_dtype(data[col2]):
            suggestions.extend(["Spearman's Rank Correlation", "Kendall's Tau"])
        
        # Multiple groups detection
        if len(data[col2].unique()) > 2:
            if pd.api.types.is_numeric_dtype(data[col2]):
                suggestions.append("Kruskal-Wallis Test")
            else:
                suggestions.append("Friedman Test")
    else:
        # One-sample tests
        suggestions.extend(["Sign Test", "Runs Test (Wald-Wolfowitz)"])
    
    return suggestions

# PDF Generation function
def create_pdf_report(test_results, visualizations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add test results
    pdf.cell(200, 10, txt="Statistical Test Report", ln=1, align="C")
    pdf.ln(10)
    
    for section, content in test_results.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=section, ln=1)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=str(content))
        pdf.ln(5)
    
    # Add visualizations
    if visualizations:
        pdf.add_page()
        pdf.cell(200, 10, txt="Visualizations", ln=1, align="C")
        for idx, img_path in enumerate(visualizations):
            pdf.image(img_path, x=10, y=20 + (idx * 60), w=180)
    
    return pdf.output(dest="S").encode("latin1")

# Enhanced visualization section
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
    
    if "Scatterplot" in selected_plots and col2:
        fig, ax = plt.subplots()
        sns.scatterplot(x=data[col1], y=data[col2], ax=ax)
        visualizations.append(fig)
    
    return visualizations

# Streamlit app
st.title("Enhanced Non-Parametric Statistical Analysis App")

# File upload and data handling
uploaded_file = st.file_uploader("Upload Dataset", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    
    numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()
    
    col1 = st.selectbox("Select Primary Column", numeric_cols)
    col2 = st.selectbox("Select Secondary Column (optional)", ["None"] + numeric_cols)
    col2 = None if col2 == "None" else col2
    
    # Test suggestions
    suggested_tests = suggest_tests(data, col1, col2)
    selected_test = st.selectbox("Select Statistical Test", suggested_tests)
    
    # Hypothesis input
    with st.expander("Hypothesis Setup"):
        null_hyp = st.text_input("Null Hypothesis (H0)", "No significant difference exists")
        alt_hyp = st.text_input("Alternative Hypothesis (H1)", "A significant difference exists")
    
    # Visualization options
    with st.expander("Visualization Options"):
        plot_options = ["Boxplot", "Violin Plot", "Distribution Plot", "Scatterplot"]
        selected_plots = st.multiselect("Select Visualizations", plot_options, default=plot_options[:2])
    
    # Run analysis
    if st.button("Run Full Analysis"):
        # Initialize variables
        stat = None
        p_value = None
        
        # Perform the selected test
        try:
            if selected_test == "Mann-Whitney U Test":
                stat, p_value = mannwhitneyu(data[col1], data[col2])
            
            elif selected_test == "Wilcoxon Signed-Rank Test":
                stat, p_value = wilcoxon(data[col1], data[col2])
            
            elif selected_test == "Kruskal-Wallis Test":
                grouped_data = [group[col1].values for _, group in data.groupby(col2)]
                stat, p_value = kruskal(*grouped_data)
            
            elif selected_test == "Sign Test":
                mu0 = data[col1].median()
                differences = data[col1] - mu0
                positive_count = (differences > 0).sum()
                negative_count = (differences < 0).sum()
                total_count = positive_count + negative_count
                stat = positive_count
                p_value = binom_test(positive_count, total_count, p=0.5, alternative='two-sided')
            
            elif selected_test == "Runs Test (Wald-Wolfowitz)":
                stat, p_value = runstest_1samp(data[col1], correction=True)
            
            elif selected_test == "Kolmogorov-Smirnov Test":
                stat, p_value = ks_2samp(data[col1], data[col2])
            
            elif selected_test == "Spearman's Rank Correlation":
                stat, p_value = spearmanr(data[col1], data[col2])
            
            elif selected_test == "Kendall's Tau":
                stat, p_value = kendalltau(data[col1], data[col2])
            
            elif selected_test == "Friedman Test":
                stat, p_value = friedmanchisquare(*[data[col].values for col in numeric_cols[:3]])
            
            else:
                st.error("Selected test not implemented yet.")
                st.stop()
        
        except Exception as e:
            st.error(f"Error performing test: {str(e)}")
            st.stop()

        # Display results
        st.subheader("Test Results")
        st.write(f"**Test Statistic:** {stat}")
        st.write(f"**p-value:** {p_value}")
        st.write(f"**Conclusion:** {'Reject H0' if p_value < 0.05 else 'Fail to reject H0'}")

        # Generate visualizations
        figs = generate_visualizations(data, col1, col2, selected_plots)
        for fig in figs:
            st.pyplot(fig)

        # Prepare PDF report
        with st.spinner("Generating Report..."):
            test_results = {
                "Test Performed": selected_test,
                "Null Hypothesis": null_hyp,
                "Alternative Hypothesis": alt_hyp,
                "Test Results": f"Statistic: {stat}\nP-value: {p_value}",
                "Conclusion": "Reject H0" if p_value < 0.05 else "Fail to reject H0"
            }
            
            # Save visualizations temporarily
            img_paths = []
            for idx, fig in enumerate(figs):
                with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    fig.savefig(tmpfile.name, bbox_inches="tight")
                    img_paths.append(tmpfile.name)
                plt.close(fig)
            
            # Create PDF
            pdf_bytes = create_pdf_report(test_results, img_paths)
            
            # Offer download
            st.download_button(
                label="Download Full Report",
                data=pdf_bytes,
                file_name="statistical_report.pdf",
                mime="application/pdf"
            )