import streamlit as st
import pandas as pd
from config import get_gspread_client, SPREADSHEET_NAME, SHEET_INDEXES

def show():

    st.markdown("""
        <style>
        /* Make rows tighter only inside tab content */
        div[data-baseweb="tab-panel"] [data-testid="stVerticalBlockBorderWrapper"] {
            margin-top: -0.75rem !important;
            margin-bottom: -0.75rem !important;
        }

        /* Remove excess padding inside form containers */
        div[data-baseweb="tab-panel"] [data-testid="stElementContainer"] {
            padding-top: -0.1rem !important;
            padding-bottom: -0.1rem !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        /* Optional: shrink horizontal space between columns */
        div[data-baseweb="tab-panel"] .stColumn {
            padding-left: -0.25rem !important;
            padding-right: -0.25rem !important;
        }
                
        /* Add margin ABOVE the Add Row button container */
        div[data-baseweb="tab-panel"] [data-testid="stButton"] {
            margin-top: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.set_page_config(layout="wide")
    st.title("📤 Upload Data")

    @st.cache_resource(show_spinner="Loading spreadsheet...")
    def load_all_data():
        client = get_gspread_client()
        workbook = client.open(SPREADSHEET_NAME)

        def fetch_df(sheet_key, default):
            try:
                records = workbook.get_worksheet(SHEET_INDEXES[sheet_key]).get_all_records()
                return pd.DataFrame(records) if records else default
            except:
                return default

        return {
            "enrollment": fetch_df("enrollment", pd.DataFrame(columns=["Year", "First Year", "Second Year", "Third Year", "Fourth Year"])),
            "graduation": fetch_df("graduation", pd.DataFrame(columns=["Year", "No. Graduating Students", "No. Graduates who graduated on time"])),
            "cohort": fetch_df("cohort", pd.DataFrame(columns=["Year", "Cohort Enrollment", "Cohort Graduates"]))
        }

    if "form_data" not in st.session_state:
        st.session_state.form_data = load_all_data()

    # Track pending actions
    if "pending_add" not in st.session_state:
        st.session_state.pending_add = None
    if "pending_remove" not in st.session_state:
        st.session_state.pending_remove = None

    def render_table(label, key):
        st.markdown(f"### {label}")
        df = st.session_state.form_data[key]

        edited_rows = []
        for i, row in df.iterrows():
            cols = st.columns(len(row) + 1, gap="small")
            row_data = {}

            for j, (col_name, cell) in enumerate(row.items()):
                input_key = f"{key}_{i}_{j}"
                with cols[j]:
                    value = st.text_input(
                        label=col_name if i == 0 else "",
                        value=str(cell).rstrip("0").rstrip(".") if isinstance(cell, float) else str(cell),
                        key=input_key
                    )
                    row_data[col_name] = value.strip()

            with cols[-1]:
                st.markdown("<div style='padding-top: 0em; text-align: center;'>", unsafe_allow_html=True)
                if st.button("➖", key=f"remove_{key}_{i}"):
                    st.session_state.pending_remove = (key, i)
                    st.rerun()
            edited_rows.append(row_data)


        st.session_state.form_data[key] = pd.DataFrame(edited_rows)

        # Handle remove
        if st.session_state.pending_remove and st.session_state.pending_remove[0] == key:
            _, i = st.session_state.pending_remove
            df = st.session_state.form_data[key]
            if i < len(df):
                df = df.drop(i).reset_index(drop=True)
                st.session_state.form_data[key] = df
            st.session_state.pending_remove = None
            st.rerun()

        # Handle add
        if st.session_state.pending_add == key:
            df = st.session_state.form_data[key]
            new_row = {col: "0" for col in df.columns}
            if "Year" in new_row:
                try:
                    new_row["Year"] = str(int(df["Year"].iloc[-1]) + 1)
                except:
                    new_row["Year"] = ""
            df.loc[len(df)] = new_row
            st.session_state.form_data[key] = df
            st.session_state.pending_add = None
            st.rerun()

        # Add row button
        if st.button(f"➕ Add Row to {label}", key=f"add_row_{key}"):
            st.session_state.pending_add = key
            st.rerun()

    # Tabs for all categories
    tab_titles = {
        "enrollment": "Enrollment Data",
        "graduation": "Graduation Rate",
        "cohort": "Cohort Survival Rate"
    }

    tabs = st.tabs(list(tab_titles.values()))
    for idx, sheet_key in enumerate(tab_titles):
        with tabs[idx]:
            render_table(tab_titles[sheet_key], sheet_key)

    # Submit Button
    _, _, col = st.columns([6, 1, 1])
    with col:
        if st.button("✅ Submit All", use_container_width=True):
            try:
                client = get_gspread_client()
                wb = client.open(SPREADSHEET_NAME)

                for sheet_key in tab_titles:
                    df = st.session_state.form_data[sheet_key]
                    ws = wb.get_worksheet(SHEET_INDEXES[sheet_key])
                    ws.clear()
                    ws.update("A1", [df.columns.tolist()] + df.astype(str).values.tolist())

                st.success("✅ Data successfully written to Google Sheets.")
            except Exception as e:
                st.error(f"❌ Failed to save data: {e}")
