import streamlit as st
from supabase_client import get_supabase
import pandas as pd
from datetime import datetime

def show_admin_panel():
    """Display the admin management interface"""
    st.title("Admin Dashboard")
    supabase = get_supabase()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Branches", 
        "Riders", 
        "Slip Submissions", 
        "Change Requests"
    ])
    
    with tab1:
        st.subheader("Manage Branches")
        
        # Add new branch
        with st.expander("Add New Branch"):
            with st.form("add_branch"):
                branch_code = st.text_input("Branch Code")
                branch_name = st.text_input("Branch Name")
                submit = st.form_submit_button("Add Branch")
                
                if submit:
                    if not branch_code or not branch_name:
                        st.error("Both code and name are required")
                    else:
                        try:
                            supabase.table('branches').insert({
                                "code": branch_code,
                                "name": branch_name,
                                "riders": []
                            }).execute()
                            st.success("Branch added successfully!")
                        except Exception as e:
                            st.error(f"Failed to add branch: {str(e)}")
        
        # View/edit branches
        branches = supabase.table('branches').select("*").execute().data
        if branches:
            st.write("### Existing Branches")
            for branch in branches:
                with st.expander(f"{branch['code']} - {branch['name']}"):
                    st.write(f"Riders: {', '.join(branch['riders']) if branch['riders'] else 'None'}")
                    if st.button(f"Delete {branch['code']}", key=f"del_{branch['code']}"):
                        try:
                            supabase.table('branches').delete().eq('code', branch['code']).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete: {str(e)}")
    
    with tab2:
        st.subheader("Manage Riders")
        
        # Add rider to branch
        with st.expander("Add Rider to Branch"):
            if branches:
                branch_code = st.selectbox(
                    "Select Branch",
                    options=[b['code'] for b in branches]
                )
                rider_name = st.text_input("Rider Name")
                add_rider = st.button("Add Rider")
                
                if add_rider and rider_name:
                    branch = next(b for b in branches if b['code'] == branch_code)
                    updated_riders = branch['riders'] + [rider_name] if branch['riders'] else [rider_name]
                    
                    try:
                        supabase.table('branches').update({
                            "riders": updated_riders
                        }).eq('code', branch_code).execute()
                        st.success("Rider added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add rider: {str(e)}")
        
        # View all riders
        st.write("### All Riders by Branch")
        for branch in branches:
            if branch['riders']:
                st.write(f"**{branch['code']} - {branch['name']}**")
                for rider in branch['riders']:
                    st.write(f"- {rider}")
    
    with tab3:
        st.subheader("Slip Submissions")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            branch_filter = st.selectbox(
                "Filter by Branch",
                options=["All"] + [b['code'] for b in branches]
            )
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All", "pending", "approved", "rejected"]
            )
        
        # Get filtered slips
        query = supabase.table('slips').select("*")
        if branch_filter != "All":
            query = query.eq('branch_code', branch_filter)
        if status_filter != "All":
            query = query.eq('status', status_filter)
        
        slips = query.execute().data
        
        if slips:
            df = pd.DataFrame(slips)
            st.dataframe(df[['branch_code', 'rider_name', 'slip_type', 'quantity', 'commission', 'status']])
            
            # Export button
            if st.button("Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name="slip_submissions.csv",
                    mime="text/csv"
                )
        else:
            st.info("No slip submissions found")
    
    with tab4:
        st.subheader("Change Requests")
        requests = supabase.table('change_requests').select("*").execute().data
        
        if requests:
            for req in requests:
                with st.expander(f"{req['branch_code']} - {req['status']}"):
                    st.write(f"**Requested by:** {req['requested_by']}")
                    st.write(f"**Date:** {req['requested_at']}")
                    st.write(f"**Description:** {req['description']}")
                    
                    # Status update
                    new_status = st.selectbox(
                        "Update Status",
                        options=["pending", "approved", "rejected"],
                        index=["pending", "approved", "rejected"].index(req['status']),
                        key=f"status_{req['id']}"
                    )
                    
                    if st.button("Update", key=f"update_{req['id']}"):
                        try:
                            supabase.table('change_requests').update({
                                "status": new_status
                            }).eq('id', req['id']).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {str(e)}")
        else:
            st.info("No change requests found")
