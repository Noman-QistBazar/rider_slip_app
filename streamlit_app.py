import streamlit as st
from supabase import create_client, Client

# Read Supabase credentials from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_SECRET = st.secrets["ADMIN_SECRET"]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_branch_data():
    # Assuming you want to load from 'branches' table, not slips
    response = supabase.table("branches").select("*").execute()
    if response.error:
        raise Exception(f"Failed to load branch data: {response.error.message}")
    data = response.data
    branch_data = {}
    for item in data:
        branch_code = item["branch_code"]
        branch_name = item["branch_name"]
        riders = item.get("riders", [])
        branch_data[branch_code] = (branch_name, riders)
    return branch_data


# Helper to save branch data (if needed)
def save_branch_data(branch_data):
    # Implement as needed, e.g., upsert to Supabase
    pass

# Initialize session state for branch data
if "branch_data" not in st.session_state:
    branch_data = load_branch_data()
    st.session_state.branch_data = branch_data
else:
    branch_data = st.session_state.branch_data

# Streamlit page configuration
st.set_page_config(page_title="Slip Entry", layout="centered")
st.title("📦 Recovery Commission Slip Submission")

# Branch code input with improved UX
branch_code = st.text_input("Enter Branch Code", max_chars=10, help="Enter your 10-digit branch code or admin secret.")

if branch_code:
    if branch_code == ADMIN_SECRET:
        st.success("🔐 Admin access granted.")
        try:
            from modules.admin import admin_panel
            admin_panel(branch_data)
        except Exception as e:
            st.error(f"Admin panel error: {e}")
    elif branch_code in branch_data:
        branch_name, riders = branch_data[branch_code]
        st.success(f"Branch identified: {branch_name}")
        try:
            from modules.branch import branch_panel
            branch_panel(branch_code, branch_name, riders)
        except Exception as e:
            st.error(f"Branch panel error: {e}")
    else:
        st.error("❌ Invalid branch code. Please check and try again.")
else:
    st.info("Please enter your branch code to proceed.")
