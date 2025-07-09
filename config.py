from pathlib import Path
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

# -------------------------------
# Google Sheets Configuration
# -------------------------------

SPREADSHEET_NAME = "School of Law Data"

# Sheet index mapping for easier access
SHEET_INDEXES = {
    "enrollment": 0,
    "graduation": 1,
    "cohort": 2
}

# Required OAuth scopes for Google Sheets and Drive access
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets", 
    "https://www.googleapis.com/auth/drive"
]

# -------------------------------
# Authenticate and Return gspread Client
# -------------------------------

def get_gspread_client():
    """
    Initializes and returns an authenticated gspread client
    using credentials from Streamlit secrets.
    """
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"], 
        scopes=SCOPES
    )
    return gspread.authorize(creds)