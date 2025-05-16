### 📁 File: modules/utils.py
from supabase_client import supabase

# Load branch data from Supabase
def load_branch_data():
    response = supabase.table("branches").select("*").execute()
    if hasattr(response, "data") and response.data:
        return {row["branch_code"]: (row["branch_name"], []) for row in response.data}
    return {}

# Save branch data to Supabase (inserts one new branch)
def save_branch_data(branch_code, branch_name):
    data = {"branch_code": branch_code, "branch_name": branch_name}
    response = supabase.table("branches").insert(data).execute()
    return response

# Ensure valid Excel (not needed anymore with Supabase, but kept for compatibility)
def ensure_valid_excel():
    pass
