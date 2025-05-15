import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from modules.utils import DATA_FILE

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials/google-credentials.json", scope)
    return gspread.authorize(creds)

def save_to_google_sheets():
    client = get_gsheet_client()
    spreadsheet = client.open("Rider Slip Data")  # Your actual Google Sheet name

    all_data = pd.read_excel(DATA_FILE, sheet_name=None)
    for sheet_name, df in all_data.items():
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
        
        set_with_dataframe(worksheet, df)
