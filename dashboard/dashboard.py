# -------------------------------
# Imports
# -------------------------------
import streamlit as st
import pandas as pd
import altair as alt

from config import get_gspread_client, SPREADSHEET_NAME, SHEET_INDEXES
from utils.metrics import (
    compute_dropout,
    compute_graduation_rate,
    compute_cohort_survival_rate,
    show_kpi_cards
)

# -------------------------------
# Main Dashboard Page Function
# -------------------------------
def show():

    # -------------------------------
    # Load Data from Google Sheets
    # -------------------------------
    client = get_gspread_client()
    workbook = client.open(SPREADSHEET_NAME)

    sheet1 = workbook.get_worksheet(SHEET_INDEXES["enrollment"])
    sheet2 = workbook.get_worksheet(SHEET_INDEXES["graduation"])
    sheet3 = workbook.get_worksheet(SHEET_INDEXES["cohort"])

    enroll_df = pd.DataFrame(sheet1.get_all_records())
    grad_df_raw = pd.DataFrame(sheet2.get_all_records())
    cohort_df_raw = pd.DataFrame(sheet3.get_all_records())

    # Clean column headers and format
    enroll_df.columns = enroll_df.columns.str.strip()
    enroll_df["Year"] = enroll_df["Year"].astype(str)

    # -------------------------------
    # Year Selection Dropdown
    # -------------------------------
    year_options = ["All Years"] + [y for y in enroll_df["Year"].unique() if y != "Total"]

    col1, col2, col3 = st.columns([6, 2, 0.1])  # Adjust layout
    with col2:
        selected_year = st.selectbox("📅 Select Year", year_options) 

    st.subheader("📊 Program Summary")

    # -------------------------------
    # Compute Metrics
    # -------------------------------
    grad_df = compute_graduation_rate(grad_df_raw)
    cohort_df = compute_cohort_survival_rate(cohort_df_raw)
    dropout_df = compute_dropout(enroll_df)

    # -------------------------------
    # Display KPI Cards
    # -------------------------------
    show_kpi_cards(selected_year, enroll_df, grad_df, cohort_df, dropout_df)

    # -------------------------------
    # Graphical Insights
    # -------------------------------
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([6, 1.5])
    with col_left:
        st.subheader("📈 Graphical Insights")
    with col_right:
        st.markdown("<div style='padding-top: 0.65rem;'>", unsafe_allow_html=True)
        show_labels = st.toggle("Show Values", key="show_labels", help="Toggle to display graph values")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # ===== Enrollment Bar Chart =====
    col1, col2 = st.columns(2)
    with col1:
        df_plot = enroll_df.copy()

        if selected_year != "All Years":
            df_plot = df_plot[df_plot["Year"] == selected_year]
        else:
            total_row = {
                "Year": "Total",
                "First Year": df_plot["First Year"].sum(),
                "Second Year": df_plot["Second Year"].sum(),
                "Third Year": df_plot["Third Year"].sum(),
                "Fourth Year": df_plot["Fourth Year"].sum()
            }
            df_plot = pd.concat([df_plot, pd.DataFrame([total_row])], ignore_index=True)

        df_melted = df_plot.melt(id_vars="Year", var_name="Level", value_name="Count")
        level_order = ["First Year", "Second Year", "Third Year", "Fourth Year"]

        bar = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X('Year:N', title='Year'),
            y=alt.Y('Count:Q', title='Enrollment'),
            color=alt.Color('Level:N', sort=level_order),
            xOffset=alt.XOffset('Level:N', sort=level_order),
            tooltip=["Year", "Level", "Count"]
        )

        if show_labels:
            labels = alt.Chart(df_melted).mark_text(
                dy=-10,
                color='black',
                fontSize=11
            ).encode(
                x=alt.X('Year:N'),
                y='Count:Q',
                text='Count:Q',
                detail='Level:N'
            )
            chart = (bar + labels)
        else:
            chart = bar

        chart = chart.properties(
            title="🎓 Enrollment by Year Level",
            height=400
        )

        st.altair_chart(chart, use_container_width=True)

    # ===== Graduation Rate Line Chart =====
    with col2:
        grad_plot = grad_df.copy()
        if selected_year != "All Years":
            grad_plot = grad_plot[grad_plot["Year"] == selected_year]

        line = alt.Chart(grad_plot).mark_line(point=True, color="#551012").encode(
            x=alt.X("Year:N"),
            y=alt.Y("Graduation Rate (%):Q", scale=alt.Scale(domain=[0, 100])),
            tooltip=["Year", alt.Tooltip("Graduation Rate (%)", format=".1f")]
        )

        if show_labels:
            grad_labels = alt.Chart(grad_plot).mark_text(
                align="left", dy=-10, fontSize=11
            ).encode(
                x="Year:N",
                y="Graduation Rate (%):Q",
                text=alt.Text("Graduation Rate (%):Q", format=".1f")
            )
            line = line + grad_labels

        line = line.properties(
            title="🎓 Graduation Rate",
            height=400
        )

        st.altair_chart(line, use_container_width=True)

    # ===== Cohort Survival Rate Line Chart =====
    col3, col4 = st.columns(2)
    with col3:
        survival_plot = cohort_df.copy()
        if selected_year != "All Years":
            survival_plot = survival_plot[survival_plot["Year"] == selected_year]

        survival_line = alt.Chart(survival_plot).mark_line(point=True).encode(
            x="Year:N",
            y=alt.Y("Cohort Survival Rate:Q", title="Survival Rate (%)"),
            tooltip=["Year", alt.Tooltip("Cohort Survival Rate", format=".1f")]
        )

        if show_labels:
            survival_labels = alt.Chart(survival_plot).mark_text(
                align="left", dy=-10, fontSize=11
            ).encode(
                x="Year:N",
                y="Cohort Survival Rate:Q",
                text=alt.Text("Cohort Survival Rate:Q", format=".1f")
            )
            survival_line = survival_line + survival_labels

        survival_line = survival_line.properties(
            title="📈 Cohort Survival Rate",
            height=400
        )

        st.altair_chart(survival_line, use_container_width=True)

    # ===== Drop-out Rate Line Chart =====
    with col4:
        dropout_plot = dropout_df.copy()
        if selected_year != "All Years":
            dropout_plot = dropout_plot[dropout_plot["Year"] == int(selected_year)]

        dropout_line = alt.Chart(dropout_plot).mark_line(point=True, color="#990000").encode(
            x="Year:O",
            y=alt.Y("Drop-out Rate:Q", title="Drop-out Rate (%)"),
            tooltip=["Year", alt.Tooltip("Drop-out Rate", format=".2f")]
        )

        if show_labels:
            dropout_labels = alt.Chart(dropout_plot).mark_text(
                align="left", dy=-10, fontSize=11
            ).encode(
                x="Year:O",
                y="Drop-out Rate:Q",
                text=alt.Text("Drop-out Rate:Q", format=".2f")
            )
            dropout_line = dropout_line + dropout_labels

        dropout_line = dropout_line.properties(
            title="📉 Drop-out Rate",
            height=400
        )

        st.altair_chart(dropout_line, use_container_width=True)
