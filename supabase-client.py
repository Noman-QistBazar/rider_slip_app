from supabase import create_client, Client
from datetime import datetime
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_branch_data():
    """
    Load branch data from Supabase 'branches' table.
    Returns a dictionary: {branch_code: (branch_name, riders_list)}
    Assumes you have a 'branches' table with columns:
        branch_code (text), branch_name (text), riders (json/text array)
    """
    response = supabase.table("branches").select("*").execute()
    if response.error:
        raise Exception(f"Failed to load branch data: {response.error.message}")
    data = response.data
    branch_data = {}
    for item in data:
        branch_code = item["branch_code"]
        branch_name = item["branch_name"]
        riders = item.get("riders", [])  # List of rider names
        branch_data[branch_code] = (branch_name, riders)
    return branch_data

def save_branch_data(branch_data):
    """
    Save the branch_data dict back to Supabase.
    This example replaces all data in 'branches' table.
    """
    # For simplicity, delete all existing rows and insert new ones
    supabase.table("branches").delete().neq("branch_code", "").execute()
    for branch_code, (branch_name, riders) in branch_data.items():
        record = {
            "branch_code": branch_code,
            "branch_name": branch_name,
            "riders": riders
        }
        supabase.table("branches").insert(record).execute()

def add_slip_record(branch_code, rider_name, slip_type, amount, transaction_id, image_url):
    """
    Insert a slip record into 'rider_slip_data' table.
    The 'Date' column will be set to current datetime.
    """
    record = {
        "Date": datetime.utcnow().isoformat(),
        "branch": branch_code,
        "rider_name": rider_name,
        "slip_type": slip_type,
        "amount": amount,
        "transaction_id": transaction_id,
        "image_url": image_url
    }
    response = supabase.table("rider_slip_data").insert(record).execute()
    if response.error:
        raise Exception(f"Failed to insert slip record: {response.error.message}")
    return response.data

def check_duplicate_transaction(transaction_id):
    """
    Check if the transaction_id already exists in 'rider_slip_data'.
    Returns True if duplicate exists, else False.
    """
    if not transaction_id:
        return False
    response = supabase.table("rider_slip_data").select("transaction_id").eq("transaction_id", transaction_id).execute()
    if response.error:
        raise Exception(f"Failed to check transaction ID: {response.error.message}")
    return len(response.data) > 0

