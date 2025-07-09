import streamlit as st
import altair as alt
import plotly.express as px
import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Authenticate
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

st.set_page_config(page_title="USEP School of Law Dashboard", layout="wide")

# Track active tab
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Custom CSS
st.markdown("""
    <style>
        /* Sidebar container background */
        section[data-testid="stSidebar"] {
            background-color: #551012 !important;
        }

        /* Remove padding */
        section[data-testid="stSidebar"] > div:first-child {
            padding: 2rem 1rem;
        }

        /* Sidebar title */
        .menu-title {
            color: white;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        /* Base menu tab style */
        .menu-tab {
            background-color: #6c1a1a;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            margin-bottom: 10px;
            font-weight: 500;
            cursor: pointer;
            display: block;
            text-align: left;
            border: none;
            transition: background-color 0.2s ease;
        }

        /* Hover effect */
        .menu-tab:hover {
            background-color: #822020;
        }

        /* Active tab style */
        .menu-tab-active {
            background-color: #992525 !important;
            border-left: 5px solid #ffcccb;
        }

        /* Optional: Click/press effect using :active */
        .menu-tab:active {
            background-color: #a12d2d;
        }
    </style>
""", unsafe_allow_html=True)

# At the top of your file (after other CSS)
st.markdown("""
        <style>
        .metric-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
            margin-bottom: 10px;
        }
        .metric-title {
            font-size: 18px;
            color: #888;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #551012;
        }
        .metric-change {
            font-size: 14px;
        }
        </style>
""", unsafe_allow_html=True)



# HEADER
st.markdown("""
    <div style='
        background-color: #990000;
        padding: 30px 50px 20px 50px;
        text-align: center;
        border-bottom: 5px solid #660000;
    '>
        <h1 style='color: white; margin-bottom: 5px;'>UNIVERSITY OF SOUTHEASTERN PHILIPPINES</h1>
        <h3 style='color: white; margin-top: 0;'>School of Law</h3>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .card-container {
            background-color: #f8f8f8;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-top: 20px;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)


# 📚 Sidebar Title
st.sidebar.markdown("<div class='menu-title'>📚 Dashy</div>", unsafe_allow_html=True)

# Simulate tab-style menu without reload
def tab(label, key):
    is_active = st.session_state.page == key
    button_style = "menu-tab menu-tab-active" if is_active else "menu-tab"
    clicked = st.sidebar.button(f"{label}", key=f"btn-{key}", use_container_width=True)
    if clicked:
        st.session_state.page = key


# Sidebar tabs
tab("🏠 Dashboard", "Dashboard")
tab("📤 Upload Data", "Upload")
tab("ℹ️ About", "About")


# Load your sheet
workbook = client.open("School of Law Data")
sheet1 = workbook.sheet1  # Sheet1 for enrollment
sheet2 = workbook.get_worksheet(1)  # Sheet2 for graduation data
sheet3 = workbook.get_worksheet(2)

data = sheet1.get_all_records()
df = pd.DataFrame(data)

df.columns = df.columns.str.strip()
df["Year"] = df["Year"].astype(str)

# Add total row at the end
total_row = {
    "Year": "Total",
    "First Year": df["First Year"].sum(),
    "Second Year": df["Second Year"].sum(),
    "Third Year": df["Third Year"].sum(),
    "Fourth Year": df["Fourth Year"].sum()
}
df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

# Sidebar filter with an extra "All Years" option
year_options = ["All Years"] + df["Year"].astype(str).tolist()

# Graduation data

grad_data = sheet2.get_all_records()
grad_df = pd.DataFrame(grad_data)

# Strip column names and convert Year to string
grad_df.columns = grad_df.columns.str.strip()
grad_df["Year"] = grad_df["Year"].astype(str)

# Compute graduation rate
grad_df["Graduation Rate (%)"] = grad_df.apply(
    lambda row: (row["No. Graduates who graduated on time"] / row["No. Graduating Students"] * 100)
    if row["No. Graduating Students"] > 0 else 0,
    axis=1
)

# Cohort Survival Rate

cohort_sheet = sheet3.get_all_records()
cohort_df = pd.DataFrame(cohort_sheet)

# Ensure columns are clean
cohort_df.columns = cohort_df.columns.str.strip()
cohort_df["Year"] = cohort_df["Year"].astype(str)  # For easier matching

# Drop-out Rate (based on Sheet 1)

# Calculate Drop-out Rate
dropout_data = []

# Convert Year column to int for comparison
df["Year"] = df["Year"].apply(lambda x: int(x) if str(x).isdigit() else x)

for i in range(1, len(df)):
    if not isinstance(df.loc[i - 1, "Year"], int) or not isinstance(df.loc[i, "Year"], int):
        continue  # Skip "Total" or invalid rows

    year = df.loc[i, "Year"]

    prev_row = df.loc[i - 1]
    current_row = df.loc[i]

    dropped_total = 0
    enrolled_total = 0

    # Track transitions (1st -> 2nd, 2nd -> 3rd, etc.)
    transitions = [("First Year", "Second Year"), ("Second Year", "Third Year"), ("Third Year", "Fourth Year")]

    for prev_level, next_level in transitions:
        enrolled = prev_row[prev_level]
        advanced = current_row[next_level]

        if enrolled > 0:
            dropped = enrolled - advanced
            dropped_total += dropped
            enrolled_total += enrolled

    if enrolled_total > 0:
        dropout_rate = (dropped_total / enrolled_total) * 100
    else:
        dropout_rate = 0

    dropout_data.append({"Year": year, "Drop-out Rate": dropout_rate})

dropout_df = pd.DataFrame(dropout_data)

# Show page content
if st.session_state.page == "Dashboard":

    # Right-aligned small selectbox using HTML + Streamlit columns
    col1, col2, col3 = st.columns([6, 2, 0.1])  # Use flexible spacing
    with col2:
        st.markdown("###")  # spacing
        selected_year = st.selectbox("📅 Select Year to View", year_options)

        # Filter logic
        if selected_year == "All Years":
            filtered_df = df
        else:
            filtered_df = df[df["Year"].astype(str) == selected_year]

    st.subheader("📊 Program Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        
        # === Handle Total or specific year ===
        if selected_year in ["Total", "All Years"]:
            current_total = df.iloc[:, 1:].sum().sum()
            change_text = "Overall Total"
            change_color = "#888"
        else:
            current_year_data = df[df["Year"] == selected_year]
            current_total = current_year_data.iloc[:, 1:].sum(axis=1).values[0] if not current_year_data.empty else 0

            # Get previous year
            previous_year = str(int(selected_year) - 1)
            previous_data = df[df["Year"] == previous_year]
            previous_total = previous_data.iloc[:, 1:].sum(axis=1).values[0] if not previous_data.empty else 0

            # Compute difference
            delta = current_total - previous_total
            if delta > 0:
                change_text = f"🔺 +{delta} since {previous_year}"
                change_color = "green"
            elif delta < 0:
                change_text = f"🔻 {delta} since {previous_year}"
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

    with col2:
     # === Handle Total or specific year ===
        if selected_year in ["Total", "All Years"]:
            grad_filtered = grad_df.copy()

            # Compute total graduation rate
            total_graduates = grad_filtered["No. Graduates who graduated on time"].sum()
            total_graduating = grad_filtered["No. Graduating Students"].sum()
            if total_graduating > 0:
                grad_rate = (total_graduates / total_graduating) * 100
            else:
                grad_rate = 0

            change_text = "Overall Rate"
            change_color = "#888"
        else:
            grad_filtered = grad_df[grad_df["Year"] == selected_year]
            grad_rate = 0
            if not grad_filtered.empty:
                current_row = grad_filtered.iloc[0]
                if current_row["No. Graduating Students"] > 0:
                    grad_rate = (current_row["No. Graduates who graduated on time"] / current_row["No. Graduating Students"]) * 100

            # Get previous year
            prev_year = str(int(selected_year) - 1)
            prev_row = grad_df[grad_df["Year"] == prev_year]

            if not prev_row.empty:
                prev_row = prev_row.iloc[0]
                if prev_row["No. Graduating Students"] > 0:
                    prev_rate = (prev_row["No. Graduates who graduated on time"] / prev_row["No. Graduating Students"]) * 100
                    delta = grad_rate - prev_rate
                    if delta > 0:
                        change_text = f"🔺 +{delta:.1f}% since {prev_year}"
                        change_color = "green"
                    elif delta < 0:
                        change_text = f"🔻 {delta:.1f}% since {prev_year}"
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

        # === Show KPI card ===
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Graduation Rate</div>
                <div class="metric-value">{grad_rate:.1f}%</div>
                <div class="metric-change" style="color: {change_color};">{change_text}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:

        if selected_year in ["Total", "All Years"]:
            cohort_filtered = cohort_df.copy()

            total_cohort = cohort_filtered["Total first year cohort enrollment (4 years back for UG, 1 year back for G)"].sum()
            total_graduates = cohort_filtered["No. of Graduates who graduated from the first year cohort"].sum()

            if total_cohort > 0:
                survival_rate = (total_graduates / total_cohort) * 100
            else:
                survival_rate = 0

            change_text = "Overall Rate"
            change_color = "#888"
        else:
            cohort_filtered = cohort_df[cohort_df["Year"] == selected_year]
            survival_rate = 0
            if not cohort_filtered.empty:
                current_row = cohort_filtered.iloc[0]
                if current_row["Total first year cohort enrollment (4 years back for UG, 1 year back for G)"] > 0:
                    survival_rate = (
                        current_row["No. of Graduates who graduated from the first year cohort"]
                        / current_row["Total first year cohort enrollment (4 years back for UG, 1 year back for G)"]
                    ) * 100

            # Previous year comparison
            prev_year = str(int(selected_year) - 1)
            prev_row = cohort_df[cohort_df["Year"] == prev_year]
            if not prev_row.empty:
                prev_row = prev_row.iloc[0]
                if prev_row["Total first year cohort enrollment (4 years back for UG, 1 year back for G)"] > 0:
                    prev_rate = (
                        prev_row["No. of Graduates who graduated from the first year cohort"]
                        / prev_row["Total first year cohort enrollment (4 years back for UG, 1 year back for G)"]
                    ) * 100
                    delta = survival_rate - prev_rate
                    if delta > 0:
                        change_text = f"🔺 +{delta:.1f}% since {prev_year}"
                        change_color = "green"
                    elif delta < 0:
                        change_text = f"🔻 {delta:.1f}% since {prev_year}"
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

        # === Show KPI card ===
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Cohort Survival Rate</div>
                <div class="metric-value">{survival_rate:.1f}%</div>
                <div class="metric-change" style="color: {change_color};">{change_text}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:

        if selected_year in ["Total", "All Years"]:
            overall_dropout = dropout_df["Drop-out Rate"].mean()
            change_text = "Overall Avg"
            change_color = "#888"
        else:
            row = dropout_df[dropout_df["Year"] == int(selected_year)]
            current_rate = row["Drop-out Rate"].values[0] if not row.empty else 0

            # Previous year
            prev_row = dropout_df[dropout_df["Year"] == int(selected_year) - 1]
            prev_rate = prev_row["Drop-out Rate"].values[0] if not prev_row.empty else 0

            delta = current_rate - prev_rate
            if delta > 0:
                change_text = f"🔺 +{delta:.1f}% since {int(selected_year) - 1}"
                change_color = "red"
            elif delta < 0:
                change_text = f"🔻 {delta:.1f}% since {int(selected_year) - 1}"
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
            
    st.subheader("Graphs")

    # Create 2 columns
    col1, col2 = st.columns(2)

    with col1:

        # Melt data for chart
        df_melted = filtered_df.melt(id_vars="Year", var_name="Level", value_name="Count")
        level_order = ["First Year", "Second Year", "Third Year", "Fourth Year"]

        # Grouped bar chart with offsets (works for 1 year or many)
        chart_enroll = alt.Chart(df_melted).mark_bar().encode(
                x=alt.X('Year:N', title="Year"),
                y=alt.Y('Count:Q', title="Enrollment"),
                color=alt.Color('Level:N', sort=level_order, title="Year Level"),
                xOffset=alt.XOffset('Level:N', sort=level_order),
                tooltip=['Year', 'Level', 'Count']
            ).properties(
                title=f"🎓 Enrollment by Year Level{' for ' + selected_year if selected_year != 'All Years' else ''}",
                width=700,
                height=400
        )

        st.altair_chart(chart_enroll, use_container_width=True)

    with col2:

        grad_line = alt.Chart(grad_filtered).mark_line(point=True, color="#551012").encode(
        x=alt.X("Year:N", title="Year", sort=grad_df["Year"].tolist()),
        y=alt.Y("Graduation Rate (%):Q", title="Graduation Rate (%)", scale=alt.Scale(domain=[0, 100])),
        tooltip=["Year", alt.Tooltip("Graduation Rate (%)", format=".1f")]
            ).properties(
                width=700,
                height=400,
                title=f"🎓 Graduation Rate {'for ' + selected_year if selected_year != 'All Years' else ''}"
        )

        # Add text labels above points
        labels = alt.Chart(grad_filtered).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=12
                ).encode(
                    x="Year:N",
                    y="Graduation Rate (%):Q",
                    text=alt.Text("Graduation Rate (%):Q", format=".1f")
        )

        st.altair_chart(grad_line + labels, use_container_width=True)


    # Create 2 columns
    col3, col4 = st.columns(2)

    with col3:

        if selected_year in ["Total", "All Years"]:
            chart_df = cohort_df.copy()
        else:
            chart_df = cohort_df[cohort_df["Year"] == selected_year]

        # Compute the Cohort Survival Rate per row
        chart_df["Cohort Survival Rate"] = chart_df.apply(
            lambda row: (row["No. of Graduates who graduated from the first year cohort"] /
                        row["Total first year cohort enrollment (4 years back for UG, 1 year back for G)"] * 100)
            if row["Total first year cohort enrollment (4 years back for UG, 1 year back for G)"] > 0 else 0,
            axis=1
        )

        # Ensure Year is string for plotting
        chart_df["Year"] = chart_df["Year"].astype(str)

        # Altair line chart
        survival_chart = alt.Chart(chart_df).mark_line(point=True).encode(
                x=alt.X("Year:N", title="Year"),
                y=alt.Y("Cohort Survival Rate:Q", title="Survival Rate (%)"),
                tooltip=["Year", alt.Tooltip("Cohort Survival Rate", format=".1f")]
            ).properties(
                title=f"📈 Cohort Survival Rate{' for ' + selected_year if selected_year != 'All Years' else ''}",
                width=700,
                height=400
        )

        st.altair_chart(survival_chart, use_container_width=True)

    with col4:

        if selected_year in ["Total", "All Years"]:
            dropout_filtered = dropout_df
        else:
            dropout_filtered = dropout_df[dropout_df["Year"] == int(selected_year)]

        dropout_chart = alt.Chart(dropout_filtered).mark_line(point=True, color='#990000').encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Drop-out Rate:Q', title='Drop-out Rate (%)'),
            tooltip=['Year', alt.Tooltip('Drop-out Rate', format='.2f')]
        ).properties(
            title="📉 Yearly Drop-out Rate",
            width=700,
            height=400
        )

        st.altair_chart(dropout_chart, use_container_width=True)


elif st.session_state.page == "Upload":
    st.subheader("📤 Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.dataframe(df)

elif st.session_state.page == "About":
    st.subheader("ℹ️ About This App")
    st.markdown("This dashboard helps the School of Law monitor student data.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
