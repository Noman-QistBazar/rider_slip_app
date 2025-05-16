import os
import streamlit as st
from datetime import datetime
from modules.utils import (
    file_hash, save_image_and_hash, is_duplicate_image,
    calculate_commission, generate_weeks, IMAGE_ROOT
)
from supabase_client import supabase  # Your Supabase client instance

REQUESTS_TABLE = "requests"
SLIPS_TABLE = "slips"

def save_request(request_data):
    response = supabase.table(REQUESTS_TABLE).insert(request_data).execute()
    if response.status_code == 201:
        st.success("Change request submitted.")
    else:
        st.error("Failed to submit request.")

def save_slip_entry(entry):
    response = supabase.table(SLIPS_TABLE).insert(entry).execute()
    if response.status_code == 201:
        return True
    else:
        st.error("Failed to save slip entry.")
        return False

def branch_panel(branch_code, branch_name, riders):
    week_options = generate_weeks()
    week_labels = [f"{s.date()} to {e.date()}" for s, e in week_options]
    selected_label = st.selectbox("Select Week", week_labels)

    if 'slip_entries' not in st.session_state:
        st.session_state.slip_entries = []

    st.markdown("### ➕ Add Rider Slips")

    slip_type = st.radio("Slip Type", ["Cash Slip", "Online Slip"])

    with st.form("rider_form", clear_on_submit=True):
        rider_name = st.selectbox("Select Rider", riders)
        slip_qty = st.number_input("Slip Quantity", min_value=1)
        manager_name = st.text_input("Your Name")
        txn_id = st.text_input("Transaction ID" if slip_type == "Online Slip" else "Serial Number")
        slip_img = st.file_uploader("Upload Slip Image", type=["jpg", "jpeg", "png", "pdf"])

        if st.form_submit_button("Add to List"):
            if not txn_id:
                st.error("Transaction ID is required.")
            elif slip_img is None:
                st.warning("Slip image is required.")
            else:
                folder = os.path.join(IMAGE_ROOT, branch_code, rider_name)
                hash_val = file_hash(slip_img)
                if is_duplicate_image(hash_val, folder):
                    st.error("Duplicate image detected.")
                else:
                    filename = f"{int(datetime.now().timestamp())}_{slip_img.name}"
                    save_image_and_hash(slip_img, folder, filename)

                    st.session_state.slip_entries.append({
                        "Rider Name": rider_name,
                        "Slip Type": slip_type,
                        "Slip Quantity": slip_qty,
                        "Transaction ID": txn_id,
                        "Image Path": filename,
                        "Submitted By": manager_name,
                        "Branch Code": branch_code,
                        "Week": selected_label,
                        "Commission": calculate_commission(slip_qty, slip_type),
                        "Submitted At": datetime.now().isoformat()
                    })
                    st.success("Entry added.")

    if st.session_state.slip_entries:
        st.markdown("### 📋 Preview Entries")
        st.dataframe(st.session_state.slip_entries)

        if st.button("✅ Submit All Entries"):
            errors = 0
            for entry in st.session_state.slip_entries:
                if not save_slip_entry(entry):
                    errors += 1
            if errors == 0:
                st.success("All entries submitted successfully.")
                st.session_state.slip_entries = []
            else:
                st.error(f"{errors} entries failed to save.")

        st.markdown("---")
        st.markdown("### Submit Change Request")
        desc = st.text_area("Describe your requested changes")
        if st.button("Submit Change Request"):
            if desc and manager_name:
                request_data = {
                    "Request Type": "Change",
                    "Branch Code": branch_code,
                    "Requested By": manager_name,
                    "Description": desc,
                    "Timestamp": datetime.now().isoformat(),
                    "Status": "Pending"
                }
                save_request(request_data)
            else:
                st.warning("Please enter your name and describe the change.")
