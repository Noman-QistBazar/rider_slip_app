import streamlit as st
import pandas as pd
import os
from modules.google_sync import save_to_google_sheets
from modules.utils import DATA_FILE, REQUESTS_FILE
from modules.utils import save_branch_data


def admin_panel(branch_data):
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Manage Data", "👤 Branches", "🚴 Riders", "📨 Requests"])

    with tab1:
        st.header("📥 Manage Excel Data")
        if st.button("Download All Data"):
            with pd.ExcelFile(DATA_FILE) as xls:
                combined = pd.concat(pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names)
            st.download_button("Download Merged Excel", combined.to_csv(index=False), file_name="all_branch_data.csv")
        
        if st.button("Sync to Google Sheets"):
            save_to_google_sheets()
            st.success("Synced to Google Sheets.")

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
                    save_branch_data(branch_data)  # ✅ Save to file
                    st.success(f"Added branch {new_name} ({new_code})")
                    st.rerun()  # ✅ Refresh UI after change
            else:
                st.error("Enter both code and name.")

        st.markdown("### Existing Branches")
        # Iterate over a copy to avoid 'dictionary changed size' error
        for code in list(branch_data.keys()):
            name, _ = branch_data[code]
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{code}: {name}")
            with col2:
                if st.button(f"Remove {code}", key=f"remove_{code}"):
                    del branch_data[code]
                    save_branch_data(branch_data)  # ✅ this saves the updated dict to file
                    st.success(f"Removed {name}")
                    st.rerun()  # refresh the UI


        # Show removal success message on next run
        if "branch_removed" in st.session_state:
            st.success(f"Removed {st.session_state['branch_removed']}")
            del st.session_state["branch_removed"]


    with tab3:
        st.header("🚴 Manage Field Officer")
        branch_select = st.selectbox("Select Branch", list(branch_data.keys()))
        if branch_select:
            riders = branch_data[branch_select][1]
            new_rider = st.text_input("Add Field Officer")
            if st.button("Add Field Officer"):
                if new_rider and new_rider not in riders:
                    riders.append(new_rider)
                    st.success(f"Add Field Officer {new_rider} to {branch_select}")

            st.markdown("### Existing Field Officer")
            for rider in riders[:]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(rider)
                with col2:
                    if st.button("Remove", key=f"Field Officer_{rider}"):
                        riders.remove(rider)
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
