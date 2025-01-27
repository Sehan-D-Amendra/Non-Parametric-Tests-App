import pandas as pd
import streamlit as st
from scipy.stats import (
    wilcoxon, mannwhitneyu, kruskal, friedmanchisquare, spearmanr, kendalltau, ks_2samp
)
from statsmodels.sandbox.stats.runs import runstest_1samp
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.proportion import binom_test


# Function to suggest tests based on column types
def suggest_tests(data, col1, col2=None):
    suggestions = []
    if col1 and col2:
        suggestions.extend([
            "Kolmogorov-Smirnov Test",
            "Mann-Whitney U Test",
            "Wilcoxon Signed-Rank Test",
            "Spearman's Rank Correlation",
            "Kendall's Tau",
        ])
    elif col1:
        suggestions.extend([
            "Sign Test",
            "Runs Test (Wald-Wolfowitz)",
        ])
    if len(data[col1].unique()) > 2:
        suggestions.append("Kruskal-Wallis Test")
        if col2:
            suggestions.append("Friedman Test")
    return suggestions

# Streamlit app
st.title("Non-Parametric Statistical Tests App")

# Upload dataset
uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.write("Dataset Preview:")
    st.dataframe(data.head())

    # Select numeric columns
    numeric_columns = data.select_dtypes(include=["float", "int"]).columns.tolist()
    col1 = st.selectbox("Select the primary column for analysis", numeric_columns)
    col2 = st.selectbox("Select the secondary column (optional)", ["None"] + numeric_columns)
    col2 = None if col2 == "None" else col2

    # Recommend tests
    st.subheader("Suggested Tests")
    suggested_tests = suggest_tests(data, col1, col2)
    st.write("**Based on your column selection, the following tests are recommended:**")
    st.write(", ".join(suggested_tests))

    # Hypothesis input
    st.subheader("Define Hypotheses")
    null_hypothesis = st.text_input("Null Hypothesis (H0)", "Enter your null hypothesis here.")
    alt_hypothesis = st.text_input("Alternative Hypothesis (H1)", "Enter your alternative hypothesis here.")

    # Perform selected test
    test = st.selectbox("Select a test to perform", suggested_tests)

    if st.button("Run Test"):
        result = None
        p_value = None

        if test == "Kolmogorov-Smirnov Test":
            stat, p_value = ks_2samp(data[col1], data[col2])

        elif test == "Mann-Whitney U Test":
            stat, p_value = mannwhitneyu(data[col1], data[col2])

        elif test == "Wilcoxon Signed-Rank Test":
            stat, p_value = wilcoxon(data[col1], data[col2])

        

        elif test == "Sign Test":
            # Automatically calculate the median of col1 as mu0
            mu0 = data[col1].median()
            st.write(f"Automatically calculated median (mu0): {mu0}")

            # Perform the Sign Test
            differences = data[col1] - mu0
            positive_count = (differences > 0).sum()
            negative_count = (differences < 0).sum()
            total_count = positive_count + negative_count  # Count of non-zero differences

            stat = positive_count  # Number of positive differences
            p_value = binom_test(positive_count, total_count, p=0.5, alternative='two-sided')

            # Display results
            st.write(f"**Test Statistic (Positive Count):** {stat}")
            st.write(f"**p-value:** {p_value}")




        elif test == "Kruskal-Wallis Test":
            grouped_data = [group[col1].values for _, group in data.groupby(col2)]
            stat, p_value = kruskal(*grouped_data)

        elif test == "Friedman Test":
            stat, p_value = friedmanchisquare(*[data[col].values for col in numeric_columns[:3]])

        elif test == "Spearman's Rank Correlation":
            stat, p_value = spearmanr(data[col1], data[col2])

        elif test == "Kendall's Tau":
            stat, p_value = kendalltau(data[col1], data[col2])

        elif test == "Runs Test (Wald-Wolfowitz)":
            stat, p_value = runstest_1samp(data[col1], correction=True)

        # Display Results
        st.subheader("Test Results")
        st.write(f"**Test Statistic:** {stat}")
        st.write(f"**p-value:** {p_value}")

        alpha = 0.05
        if p_value < alpha:
            st.write("**Conclusion:** Reject the null hypothesis (H0).")
        else:
            st.write("**Conclusion:** Fail to reject the null hypothesis (H0).")

    # Visualizations
    st.subheader("Visualizations")
    if st.checkbox("Show Boxplot"):
        fig, ax = plt.subplots()
        if col2:
            sns.boxplot(data=data, x=col2, y=col1, ax=ax)
        else:
            sns.boxplot(data=data, y=col1, ax=ax)
        st.pyplot(fig)

    if st.checkbox("Show Scatterplot"):
        if col2:
            fig, ax = plt.subplots()
            sns.scatterplot(x=data[col1], y=data[col2], ax=ax)
            st.pyplot(fig)

    if st.checkbox("Show Pairplot"):
        fig = sns.pairplot(data[numeric_columns])
        st.pyplot(fig)
