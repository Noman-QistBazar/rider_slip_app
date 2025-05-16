import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from modules.utils import DATA_FILE
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    creds_dict = st.secrets["service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)


# def get_gsheet_client():
#     creds_dict = st.secrets["service_account"]
#     creds = Credentials.from_service_account_info(creds_dict)
#     client = gspread.authorize(creds)
#     return client
# def get_gsheet_client():
#     scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#     creds = ServiceAccountCredentials.from_json_keyfile_name("credentials/google-credentials.json", scope)
#     return gspread.authorize(creds)

# Load branch data from sheet
def load_branch_data():
    gc = get_gspread_client()
    sheet = gc.open("BranchData").sheet1
    df = get_as_dataframe(sheet, evaluate_formulas=True).dropna(how='all')
    
    branch_data = {}
    for _, row in df.iterrows():
        if pd.notna(row["Branch Code"]) and pd.notna(row["Branch Name"]):
            code = str(row["Branch Code"])
            name = row["Branch Name"]
            riders = [r.strip() for r in str(row["Riders"]).split(",")] if pd.notna(row["Riders"]) else []
            branch_data[code] = (name, riders)
    return branch_data

# Save branch data to sheet
def save_branch_data(branch_data):
    gc = get_gspread_client()
    sheet = gc.open("BranchData").sheet1
    data = []

    for code, (name, riders) in branch_data.items():
        rider_str = ", ".join(riders)
        data.append([code, name, rider_str])

    df = pd.DataFrame(data, columns=["Branch Code", "Branch Name", "Riders"])
    sheet.clear()
    set_with_dataframe(sheet, df)
    
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
