import streamlit as st
import time
import pandas as pd
from config import get_gspread_client, SPREADSHEET_NAME, SHEET_INDEXES

# -------------------------------
# Main Upload Data Page
# -------------------------------
def show():
    # ---------------------------------------
    # Authentication
    # ---------------------------------------
    if "upload_auth" not in st.session_state:
        st.session_state.upload_auth = False

    # Get secret key from secrets.toml
    required_key = st.secrets["auth"]["secret_key"]

    if not st.session_state.upload_auth:
        # Apply custom style for centering
        st.markdown("""
            <style>
                .centered-box {
                    display: flex;
                    justify-content: center;
                    margin-top: 4rem;
                }
                .stTextInput>div>input {
                    text-align: center;
                }
            </style>
        """, unsafe_allow_html=True)

        # --- Auth UI ---
        with st.container():
            cols = st.columns([1, 2, 1])  # Empty - Center - Empty
            with cols[1]:
                st.markdown("### 🔐 Enter Access Key")
                with st.form("auth_form"):
                    input_key = st.text_input("Secret Key", type="password")
                    submit = st.form_submit_button("Submit")
                    if submit:
                        if input_key == required_key:
                            st.session_state.upload_auth = True
                            st.success("✅ Access granted.")
                            st.rerun()
                        else:
                            st.error("❌ Invalid key. Please try again.")
        return  # Don't continue if not authorized
    
    # ---------------------------------------
    # Page Setup
    # ---------------------------------------
    st.set_page_config(layout="wide")
    st.title("🗃️ Data")

    # -------- Styles (including overlay) --------
    st.markdown("""
        <style>
        /* Main layout adjustments */
        div[data-baseweb="tab-panel"] [data-testid="stVerticalBlockBorderWrapper"] {
            margin-top: -0.75rem !important;
            margin-bottom: -0.75rem !important;
        }
        div[data-baseweb="tab-panel"] [data-testid="stElementContainer"] {
            padding-top: -0.1rem !important;
            padding-bottom: -0.1rem !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        div[data-baseweb="tab-panel"] .stColumn {
            padding-left: -0.25rem !important;
            padding-right: -0.25rem !important;
        }
        div[data-baseweb="tab-panel"] [data-testid="stButton"] {
            margin-top: 1rem !important;
        }

        /* Fullscreen overlay */
        #overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.9));
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 2rem;
            color: #111111; /* deep blackish text */
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------
    # Load Google Sheets Data
    # ---------------------------------------
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

    if "show_success" not in st.session_state:
        st.session_state.show_success = False
    if "submitting" not in st.session_state:
        st.session_state.submitting = False

    # ---------------------------------------
    # Render Editable Tables
    # ---------------------------------------
    def render_table(label, key):
        st.markdown(f"### {label}")
        df = st.session_state.form_data[key].copy()

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
                    st.session_state.form_data[key] = df.drop(i).reset_index(drop=True)
                    st.rerun()

            edited_rows.append(row_data)

        st.session_state.form_data[key] = pd.DataFrame(edited_rows)

        if st.button(f"➕ Add Row to {label}", key=f"add_row_{key}"):
            new_row = {col: "0" for col in df.columns}
            if "Year" in new_row:
                try:
                    new_row["Year"] = str(int(df["Year"].iloc[-1]) + 1)
                except:
                    new_row["Year"] = ""
            df.loc[len(df)] = new_row
            st.session_state.form_data[key] = df
            st.rerun()

    # ---------------------------------------
    # Render Tabbed Forms
    # ---------------------------------------
    tab_titles = {
        "enrollment": "Enrollment Data",
        "graduation": "Graduation Rate",
        "cohort": "Cohort Survival Rate"
    }

    tabs = st.tabs(list(tab_titles.values()))
    for idx, sheet_key in enumerate(tab_titles):
        with tabs[idx]:
            render_table(tab_titles[sheet_key], sheet_key)

    # ---------------------------------------
    # Submit Button & Save Logic
    # ---------------------------------------
    _, _, col = st.columns([6, 1, 1])
    with col:
        if st.button("✅ Submit All", use_container_width=True):
            st.session_state.submitting = True
            st.rerun()

    # Show overlay if submitting
    if st.session_state.submitting:
        st.markdown("<div id='overlay'>Saving data...</div>", unsafe_allow_html=True)
        try:
            client = get_gspread_client()
            wb = client.open(SPREADSHEET_NAME)

            for sheet_key in tab_titles:
                df = st.session_state.form_data[sheet_key]
                if "Year" in df.columns:
                    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
                    df = df.sort_values("Year", na_position="last").reset_index(drop=True)
                    st.session_state.form_data[sheet_key] = df

                ws = wb.get_worksheet(SHEET_INDEXES[sheet_key])
                ws.clear()
                ws.update("A1", [df.columns.tolist()] + df.astype(str).values.tolist())

            st.session_state.submitting = False
            st.session_state.show_success = True
            st.rerun()
        except Exception as e:
            st.session_state.submitting = False
            st.error(f"❌ Failed to save data: {e}")

    # ---------------------------------------
    # Submission Success Message
    # ---------------------------------------
    if st.session_state.show_success:
        st.success("✅ Successfully submitted data!")
        st.session_state.show_success = False
