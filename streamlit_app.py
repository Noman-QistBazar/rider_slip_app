import streamlit as st
import os
from dotenv import load_dotenv
from modules.admin import admin_panel
from modules.branch import branch_panel
from modules.utils import ensure_valid_excel
from modules.utils import load_branch_data, save_branch_data

load_dotenv()
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

if "branch_data" not in st.session_state:
    st.session_state.branch_data = load_branch_data()

branch_data = st.session_state.branch_data

if 'branch_data' not in st.session_state:
    st.session_state.branch_data = load_branch_data()
    save_branch_data(st.session_state.branch_data)



branch_data = st.session_state.branch_data
ensure_valid_excel()

st.set_page_config("Slip Entry", layout="centered")
st.title("📦 Recovery Commission Slip Submission")




branch_code = st.text_input("Enter Branch Code")

if branch_code == ADMIN_SECRET:
    st.success("🔐 Admin access granted.")
    admin_panel(branch_data)
elif branch_code in branch_data:
    branch_name, riders = branch_data[branch_code]
    st.success(f"Branch identified: {branch_name}")
    branch_panel(branch_code, branch_name, riders)
else:
    st.error("❌ Invalid branch code.")
