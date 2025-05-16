import streamlit as st
from modules.utils import save_branch_data, load_branch_data

def admin_panel(branch_data):
    st.subheader("🛠️ Admin Panel")
    
    # Add Branch Section
    st.markdown("### ➕ Add New Branch")
    branch_code = st.text_input("Branch Code", max_chars=10)
    branch_name = st.text_input("Branch Name")

    if st.button("Add Branch"):
        if branch_code and branch_name:
            response = save_branch_data(branch_code, branch_name)
            if hasattr(response, "data"):
                st.success(f"✅ Branch '{branch_name}' added.")
                # Refresh session state with latest data
                st.session_state.branch_data = load_branch_data()
            else:
                st.error("❌ Failed to add branch.")
        else:
            st.warning("⚠️ Please enter both code and name.")
