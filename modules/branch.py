import os
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.utils import (
    file_hash, save_image_and_hash, is_duplicate_image,
    calculate_commission, generate_weeks, DATA_FILE, backup_data
)

REQUESTS_FILE = "data/requests.csv"
IMAGE_ROOT = "images/slip_images"

def save_request(request_data):
    request_df = pd.DataFrame([request_data])
    if os.path.exists(REQUESTS_FILE):
        existing = pd.read_csv(REQUESTS_FILE)
        request_df = pd.concat([existing, request_df], ignore_index=True)
    request_df.to_csv(REQUESTS_FILE, index=False)

def branch_panel(branch_code, branch_name, riders):
    week_options = generate_weeks()
    week_labels = [f"{s.date()} to {e.date()}" for s, e in week_options]
    selected_label = st.selectbox("Select Week", week_labels)
    selected_start, selected_end = week_options[week_labels.index(selected_label)]

    if 'slip_entries' not in st.session_state:
        st.session_state.slip_entries = []

    st.markdown("### ➕ Add Rider Slips")

    # ✅ Move radio outside the form to allow real-time changes
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
            elif slip_img:
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
                        "Commission": calculate_commission(slip_qty, slip_type)
                    })
                    st.success("Entry added.")
            else:
                st.warning("Slip image is required.")

    if st.session_state.slip_entries:
        st.markdown("### 📋 Preview Entries")
        df = pd.DataFrame(st.session_state.slip_entries)
        st.dataframe(df)

        if st.button("✅ Submit All Entries"):
            with pd.ExcelWriter(DATA_FILE, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                if branch_name in writer.book.sheetnames:
                    old_df = pd.read_excel(DATA_FILE, sheet_name=branch_name)
                    df = pd.concat([old_df, df], ignore_index=True)
                df.to_excel(writer, sheet_name=branch_name, index=False)
            backup_data()
            st.session_state.slip_entries = []
            st.success("Entries submitted.")

        if st.button("Submit Change Request"):
            desc = st.text_area("Describe your requested changes")
            if desc and manager_name:
                save_request({
                    "Request Type": "Change",
                    "Branch Code": branch_code,
                    "Requested By": manager_name,
                    "Description": desc,
                    "Timestamp": datetime.now().isoformat(),
                    "Status": "Pending"
                })
                st.success("Change request submitted.")
            else:
                st.warning("Please enter your name and describe the change.")
