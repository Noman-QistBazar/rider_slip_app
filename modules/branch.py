import streamlit as st
from supabase_client import get_supabase
from modules.utils import (
    calculate_commission,
    generate_week_ranges,
    save_uploaded_image,
    validate_transaction_id
)
from datetime import datetime
import pandas as pd

def show_branch_panel():
    """Display the branch manager interface"""
    st.title("Branch Slip Submission")
    branch_code = st.session_state.branch_code
    
    # Get branch details
    supabase = get_supabase()
    branch_data = supabase.table('branches').select('name, riders').eq('code', branch_code).execute().data[0]
    branch_name = branch_data['name']
    riders = branch_data['riders'] or []
    
    if not riders:
        st.warning("No riders assigned to this branch. Please contact admin.")
        return
    
    # Week selection
    week_options = generate_week_ranges()
    selected_week = st.selectbox(
        "Select Week",
        options=[week[0] for week in week_options],
        index=0
    )
    
    # Initialize session state for slip entries
    if 'slip_entries' not in st.session_state:
        st.session_state.slip_entries = []
    
    # Slip submission form
    with st.form("slip_form"):
        st.subheader("Add New Slip")
        col1, col2 = st.columns(2)
        
        with col1:
            rider_name = st.selectbox("Rider", options=riders)
            slip_type = st.radio("Slip Type", ["Cash Slip", "Online Slip"])
            slip_qty = st.number_input("Quantity", min_value=1, value=1)
        
        with col2:
            transaction_label = "Transaction ID" if slip_type == "Online Slip" else "Serial Number"
            transaction_id = st.text_input(transaction_label)
            manager_name = st.text_input("Manager Name")
            slip_image = st.file_uploader("Slip Image", type=["jpg", "jpeg", "png", "pdf"])
        
        submitted = st.form_submit_button("Add Slip")
        
        if submitted:
            if not validate_transaction_id(slip_type, transaction_id):
                st.error(f"Please enter a valid {transaction_label}")
            elif not slip_image:
                st.error("Please upload slip image")
            else:
                try:
                    image_path = save_uploaded_image(slip_image, branch_code, rider_name)
                    commission = calculate_commission(slip_type, slip_qty)
                    
                    new_entry = {
                        "rider_name": rider_name,
                        "slip_type": slip_type,
                        "quantity": slip_qty,
                        "transaction_id": transaction_id,
                        "manager_name": manager_name,
                        "image_path": image_path,
                        "week": selected_week,
                        "branch_code": branch_code,
                        "commission": commission,
                        "submitted_at": datetime.now().isoformat(),
                        "status": "pending"
                    }
                    
                    st.session_state.slip_entries.append(new_entry)
                    st.success("Slip added successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Display current entries
    if st.session_state.slip_entries:
        st.subheader("Current Slips")
        df = pd.DataFrame(st.session_state.slip_entries)
        st.dataframe(df[['rider_name', 'slip_type', 'quantity', 'commission']])
        
        # Submit all button
        if st.button("Submit All Slips"):
            try:
                supabase.table('slips').insert(st.session_state.slip_entries).execute()
                st.session_state.slip_entries = []
                st.success("All slips submitted successfully!")
            except Exception as e:
                st.error(f"Submission failed: {str(e)}")
    
    # Change request form
    st.subheader("Change Request")
    with st.form("change_request"):
        request_description = st.text_area("Describe the changes needed")
        submit_request = st.form_submit_button("Submit Request")
        
        if submit_request and request_description:
            request_data = {
                "branch_code": branch_code,
                "description": request_description,
                "status": "pending",
                "requested_at": datetime.now().isoformat(),
                "requested_by": manager_name or "Unknown"
            }
            
            try:
                supabase.table('change_requests').insert(request_data).execute()
                st.success("Change request submitted!")
            except Exception as e:
                st.error(f"Failed to submit request: {str(e)}")
