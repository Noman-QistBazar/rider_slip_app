import streamlit as st
import pandas as pd
import os
from modules.utils import load_branch_data, save_branch_data, REQUESTS_FILE
from modules.google_sync import save_to_google_sheets  # You can remove this import if not used anymore

def admin_panel(branch_data):
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Manage Data", "👤 Branches", "🚴 Field Officer", "📨 Requests"])

    with tab1:
        st.header("📥 Manage Supabase Data")

        if st.button("Refresh Branch Data"):
            st.session_state.branch_data = load_branch_data()
            st.success("Branch data refreshed from Supabase.")

        if st.button("Export All Branches to CSV"):
            branch_data = st.session_state.get("branch_data", {})
            if branch_data:
                df = pd.DataFrame([
                    {"Branch Code": code, "Branch Name": name}
                    for code, (name, _) in branch_data.items()
                ])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Branches CSV",
                    data=csv,
                    file_name="branches.csv",
                    mime="text/csv"
                )
            else:
                st.info("No branch data available. Refresh first.")

    with tab2:
        st.header("👤 Manage Branches")
        new_code = st.text_input("New Branch Code")
        new_name = st.text_input("New Branch Name")

        if st.button("Add Branch"):
            if new_code and new_name:
                if new_code in branch_data:
                    st.error("Branch code already exists.")
                else:
                    branch_data[new_code] = (new_name, [])
                    save_branch_data(new_code, new_name)  # Save new branch to Supabase
                    st.success(f"Added branch {new_name} ({new_code})")
                    st.experimental_rerun()  # Refresh UI after change
            else:
                st.error("Enter both code and name.")

        st.markdown("### Existing Branches")
        for code in list(branch_data.keys()):
            name, _ = branch_data[code]
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{code}: {name}")
            with col2:
                if st.button(f"Remove {code}", key=f"remove_{code}"):
                    # Remove branch from Supabase
                    from supabase_client import supabase
                    res = supabase.table("branches").delete().eq("branch_code", code).execute()
                    if res.error:
                        st.error(f"Failed to remove branch {code}")
                    else:
                        del branch_data[code]
                        st.success(f"Removed {name}")
                        st.experimental_rerun()

    with tab3:
        st.header("🚴 Manage Field Officer")
        branch_select = st.selectbox("Select Branch", list(branch_data.keys()))
        if branch_select:
            riders = branch_data[branch_select][1]
            new_rider = st.text_input("Add Field Officer")
            if st.button("Add Field Officer"):
                if new_rider and new_rider not in riders:
                    riders.append(new_rider)
                    # Save riders back in your storage (you need to implement saving riders to Supabase)
                    st.success(f"Added Field Officer {new_rider} to {branch_select}")

            st.markdown("### Existing Field Officer")
            for rider in riders[:]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(rider)
                with col2:
                    if st.button("Remove", key=f"Field Officer_{rider}"):
                        riders.remove(rider)
                        # Save updated riders list to Supabase here
                        st.success(f"Removed Field Officer {rider}")

    with tab4:
        st.header("📨 Change Requests")
        if os.path.exists(REQUESTS_FILE):
            df = pd.read_csv(REQUESTS_FILE)
            if not df.empty:
                status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Resolved"])
                if status_filter != "All":
                    df = df[df["Status"] == status_filter]

                for i, row in df.iterrows():
                    with st.expander(f"{row['Timestamp']} - {row['Requested By']} ({row['Branch Code']})"):
                        st.write(f"**Type**: {row['Request Type']}")
                        st.write(f"**Description**: {row['Description']}")
                        new_status = st.selectbox("Update Status", ["Pending", "Resolved"], index=0, key=f"status_{i}")
                        if st.button("Save Status", key=f"save_{i}"):
                            full_df = pd.read_csv(REQUESTS_FILE)
                            full_df.loc[i, "Status"] = new_status
                            full_df.to_csv(REQUESTS_FILE, index=False)
                            st.success("Status updated.")
            else:
                st.info("No requests found.")
        else:
            st.warning("No requests file available.")
