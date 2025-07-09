# -------------------------------
# Imports
# -------------------------------
import pandas as pd
import streamlit as st

# -------------------------------
# KPI Computation Functions
# -------------------------------

def compute_dropout(df):
    """Compute drop-out rate between year levels based on enrollment data."""
    dropout_data = []
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")  # Ensure 'Year' is numeric

    for i in range(1, len(df)):
        if pd.isna(df.loc[i - 1, "Year"]) or pd.isna(df.loc[i, "Year"]):
            continue

        year = int(df.loc[i, "Year"])
        prev_row = df.loc[i - 1]
        current_row = df.loc[i]

        dropped_total = 0
        enrolled_total = 0

        # Define transitions to track drop-out
        transitions = [
            ("First Year", "Second Year"),
            ("Second Year", "Third Year"),
            ("Third Year", "Fourth Year")
        ]

        for prev_level, next_level in transitions:
            enrolled = pd.to_numeric(prev_row[prev_level], errors="coerce")
            advanced = pd.to_numeric(current_row[next_level], errors="coerce")

            if pd.notna(enrolled) and enrolled > 0 and pd.notna(advanced):
                dropped = enrolled - advanced
                dropped_total += dropped
                enrolled_total += enrolled

        dropout_rate = (dropped_total / enrolled_total) * 100 if enrolled_total > 0 else 0
        dropout_data.append({"Year": year, "Drop-out Rate": dropout_rate})

    return pd.DataFrame(dropout_data)


def compute_graduation_rate(grad_df):
    """Add a 'Graduation Rate (%)' column to graduation data."""
    grad_df = grad_df.copy()
    grad_df.columns = grad_df.columns.str.strip()
    grad_df["Year"] = grad_df["Year"].astype(str)

    grad_df["Graduation Rate (%)"] = grad_df.apply(
        lambda row: (row["No. Graduates who graduated on time"] / row["No. Graduating Students"] * 100)
        if row["No. Graduating Students"] > 0 else 0,
        axis=1
    )

    return grad_df


def compute_cohort_survival_rate(cohort_df):
    """Add a 'Cohort Survival Rate' column to cohort data."""
    cohort_df = cohort_df.copy()
    cohort_df.columns = cohort_df.columns.str.strip()
    cohort_df["Year"] = cohort_df["Year"].astype(str)

    cohort_df["Cohort Survival Rate"] = cohort_df.apply(
        lambda row: (
            row["Cohort Enrollment"] /
            row["Cohort Graduates"] * 100
        ) if row["Cohort Graduates"] > 0 else 0,
        axis=1
    )

    return cohort_df


def compute_total_enrollment(year, df):
    """Compute total enrollment for a given year or across all years."""
    year_cols = ["First Year", "Second Year", "Third Year", "Fourth Year"]
    df["Year"] = df["Year"].astype(str)  # Ensure year is a string for comparison

    filtered_df = df if year == "All Years" else df[df["Year"] == str(year)]

    total_first = filtered_df["First Year"].sum()
    total_second = filtered_df["Second Year"].sum()
    total_third = filtered_df["Third Year"].sum()
    total_fourth = filtered_df["Fourth Year"].sum()

    total = total_first + total_second + total_third + total_fourth
    return int(total)

# -------------------------------
# KPI Cards Renderer
# -------------------------------

def show_kpi_cards(selected_year, enroll_df, grad_df, cohort_df, dropout_df):
    """Render the four KPI metric cards on the dashboard."""
    col1, col2, col3, col4 = st.columns(4)

    # === Total Enrollment ===
    with col1:
        df = enroll_df.copy()

        if selected_year in ["Total", "All Years"]:
            current_total = df.iloc[:, 1:].sum().sum()
            change_text = "Overall Total"
            change_color = "#888"
        else:
            current_year_data = df[df["Year"] == selected_year]
            current_total = current_year_data.iloc[:, 1:].sum(axis=1).values[0] if not current_year_data.empty else 0

            previous_year = str(int(selected_year) - 1)
            previous_data = df[df["Year"] == previous_year]
            previous_total = previous_data.iloc[:, 1:].sum(axis=1).values[0] if not previous_data.empty else 0

            delta = current_total - previous_total
            if delta > 0:
                change_text = f"▲ +{delta} since {previous_year}"
                change_color = "green"
            elif delta < 0:
                change_text = f"▼ {delta} since {previous_year}"
                change_color = "red"
            else:
                change_text = f"No change from {previous_year}"
                change_color = "#888"

        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Enrollment</div>
                <div class="metric-value">{int(current_total)}</div>
                <div class="metric-change" style="color: {change_color};">{change_text}</div>
            </div>
        """, unsafe_allow_html=True)

    # === Graduation Rate ===
    with col2:
        if selected_year in ["Total", "All Years"]:
            total_graduates = grad_df["No. Graduates who graduated on time"].sum()
            total_graduating = grad_df["No. Graduating Students"].sum()
            grad_rate = (total_graduates / total_graduating) * 100 if total_graduating > 0 else 0
            change_text = "Overall Rate"
            change_color = "#888"
        else:
            grad_filtered = grad_df[grad_df["Year"] == selected_year]
            grad_rate = 0
            if not grad_filtered.empty:
                row = grad_filtered.iloc[0]
                if row["No. Graduating Students"] > 0:
                    grad_rate = (row["No. Graduates who graduated on time"] / row["No. Graduating Students"]) * 100

            prev_year = str(int(selected_year) - 1)
            prev_row = grad_df[grad_df["Year"] == prev_year]
            if not prev_row.empty:
                prev = prev_row.iloc[0]
                if prev["No. Graduating Students"] > 0:
                    prev_rate = (prev["No. Graduates who graduated on time"] / prev["No. Graduating Students"]) * 100
                    delta = grad_rate - prev_rate
                    if delta > 0:
                        change_text = f"▲ +{delta:.1f}% since {prev_year}"
                        change_color = "green"
                    elif delta < 0:
                        change_text = f"▼ {delta:.1f}% since {prev_year}"
                        change_color = "red"
                    else:
                        change_text = f"No change from {prev_year}"
                        change_color = "#888"
                else:
                    change_text = f"No data for {prev_year}"
                    change_color = "#888"
            else:
                change_text = f"No data for {prev_year}"
                change_color = "#888"

        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Graduation Rate</div>
                <div class="metric-value">{grad_rate:.1f}%</div>
                <div class="metric-change" style="color: {change_color};">{change_text}</div>
            </div>
        """, unsafe_allow_html=True)

    # === Cohort Survival Rate ===
    with col3:
        if selected_year in ["Total", "All Years"]:
            total_cohort = cohort_df["Cohort Enrollment"].sum()
            total_graduates = cohort_df["Cohort Graduates"].sum()
            survival_rate = (total_graduates / total_cohort) * 100 if total_cohort > 0 else 0
            change_text = "Overall Rate"
            change_color = "#888"
        else:
            cohort_filtered = cohort_df[cohort_df["Year"] == selected_year]
            survival_rate = 0
            if not cohort_filtered.empty:
                row = cohort_filtered.iloc[0]
                if row["Cohort Enrollment"] > 0:
                    survival_rate = (
                        row["Cohort Graduates"] /
                        row["Cohort Enrollment"]
                    ) * 100

            prev_year = str(int(selected_year) - 1)
            prev_row = cohort_df[cohort_df["Year"] == prev_year]
            if not prev_row.empty:
                prev = prev_row.iloc[0]
                if prev["Cohort Enrollment"] > 0:
                    prev_rate = (
                        prev["Cohort Graduates"] /
                        prev["Cohort Enrollment"]
                    ) * 100
                    delta = survival_rate - prev_rate
                    if delta > 0:
                        change_text = f"▲ +{delta:.1f}% since {prev_year}"
                        change_color = "green"
                    elif delta < 0:
                        change_text = f"▼ {delta:.1f}% since {prev_year}"
                        change_color = "red"
                    else:
                        change_text = f"No change from {prev_year}"
                        change_color = "#888"
                else:
                    change_text = f"No data for {prev_year}"
                    change_color = "#888"
            else:
                change_text = f"No data for {prev_year}"
                change_color = "#888"

        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Cohort Survival Rate</div>
                <div class="metric-value">{survival_rate:.1f}%</div>
                <div class="metric-change" style="color: {change_color};">{change_text}</div>
            </div>
        """, unsafe_allow_html=True)

    # === Drop-out Rate ===
    with col4:
        if selected_year in ["Total", "All Years"]:
            overall_dropout = dropout_df["Drop-out Rate"].mean()
            change_text = "Overall Avg"
            change_color = "#888"
        else:
            row = dropout_df[dropout_df["Year"] == int(selected_year)]
            current_rate = row["Drop-out Rate"].values[0] if not row.empty else 0

            prev_row = dropout_df[dropout_df["Year"] == int(selected_year) - 1]
            prev_rate = prev_row["Drop-out Rate"].values[0] if not prev_row.empty else 0

            delta = current_rate - prev_rate
            if delta > 0:
                change_text = f"▲ +{delta:.1f}% since {int(selected_year) - 1}"
                change_color = "red"
            elif delta < 0:
                change_text = f"▼ {delta:.1f}% since {int(selected_year) - 1}"
                change_color = "green"
            else:
                change_text = f"No change from {int(selected_year) - 1}"
                change_color = "#888"

            overall_dropout = current_rate

        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Drop-out Rate</div>
                <div class="metric-value">{overall_dropout:.2f}%</div>
                <div class="metric-change" style="color: {change_color};">{change_text}</div>
            </div>
        """, unsafe_allow_html=True)
