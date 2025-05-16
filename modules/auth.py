import streamlit as st
from supabase_client import get_supabase
import os
from dotenv import load_dotenv

load_dotenv()

def authenticate_user():
    """Handle user authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.branch_code = None
    
    if st.session_state.authenticated:
        return True
    
    with st.container():
        st.title("Login")
        login_tab, admin_tab = st.tabs(["Branch Login", "Admin Login"])
        
        with login_tab:
            branch_code = st.text_input("Branch Code", key="branch_code")
            submit = st.button("Login")
            
            if submit:
                supabase = get_supabase()
                result = supabase.table('branches').select('*').eq('code', branch_code).execute()
                if len(result.data) > 0:
                    st.session_state.authenticated = True
                    st.session_state.user_role = "branch_manager"
                    st.session_state.branch_code = branch_code
                    st.rerun()
                else:
                    st.error("Invalid branch code")
        
        with admin_tab:
            admin_secret = st.text_input("Admin Secret", type="password")
            submit_admin = st.button("Admin Login")
            
            if submit_admin and admin_secret == os.getenv("ADMIN_SECRET_KEY"):
                st.session_state.authenticated = True
                st.session_state.user_role = "admin"
                st.rerun()
            elif submit_admin:
                st.error("Invalid admin credentials")
    
    return False

def logout_button():
    """Display logout button if authenticated"""
    if st.session_state.get('authenticated', False):
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.branch_code = None
            st.rerun()
