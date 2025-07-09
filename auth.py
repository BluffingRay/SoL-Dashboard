import gspread
from oauth2client.service_account import ServiceAccountCredentials

def init_auth():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("assets/credentials.json", scope)
    client = gspread.authorize(creds)
    return client