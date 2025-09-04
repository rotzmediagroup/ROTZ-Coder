"""
DeepCode - Login Page
"""

import streamlit as st
import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auth.authentication import authenticate_user, check_authentication
from utils.database import get_db_session

# Page config
st.set_page_config(
    page_title="DeepCode - Login",
    page_icon="🔑",
    layout="centered"
)

# Custom CSS for login page
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background gradient */
    .stApp > div:first-child {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Login container */
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 2rem auto;
        text-align: center;
    }
    
    .login-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #6B7280;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #E5E7EB !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stButton > button {
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 2px solid #E5E7EB !important;
        color: #374151 !important;
    }
    
    /* Links */
    .login-links {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
    
    .login-links a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    
    .login-links a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check if already authenticated
    user = check_authentication()
    if user:
        st.success(f"Already logged in as {user['email']}")
        if st.button("🏠 Go to Homepage"):
            st.switch_page("pages/1_🏠_Home.py")
        return
    
    # Login container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-title">🔑 Sign In</div>
    <div class="login-subtitle">Welcome back to DeepCode</div>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email",
            key="login_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        # TOTP field (initially hidden)
        totp_code = st.text_input(
            "Two-Factor Code (if enabled)",
            placeholder="6-digit code from your authenticator app",
            max_chars=6,
            key="totp_code",
            help="Leave empty if you haven't set up 2FA yet"
        )
        
        submitted = st.form_submit_button("🚀 Sign In", type="primary")
        
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Authenticating..."):
                    with get_db_session() as session:
                        result = authenticate_user(session, email, password, totp_code)
                        
                        if result is None:
                            st.error("Invalid email or password")
                        elif result.get("requires_totp", False):
                            st.warning("Please enter your 2FA code and try again")
                            st.info("Check your authenticator app for the 6-digit code")
                        else:
                            # Successful authentication
                            st.session_state.user = result
                            st.success(f"Welcome back, {result['full_name'] or result['email']}!")
                            st.balloons()
                            
                            # Redirect to home
                            st.switch_page("pages/1_🏠_Home.py")
    
    # Navigation links
    st.markdown("""
    <div class="login-links">
        <p>Don't have an account? <a href="?page=Register">Sign up here</a></p>
        <p><a href="?page=Home">← Back to Homepage</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Create Account", type="secondary"):
            st.switch_page("pages/7_📝_Register.py")
    
    with col2:
        if st.button("🏠 Back to Home", type="secondary"):
            st.switch_page("pages/1_🏠_Home.py")
    
    # Demo credentials info (for development/demo purposes)
    if st.checkbox("Show Demo Credentials", key="show_demo"):
        st.info("""
        **Demo Super Admin Account:**
        - Email: jerome@rotz.host
        - Password: ChangeMe123! (if account exists)
        
        Note: You'll need to set up 2FA on first login.
        """)

if __name__ == "__main__":
    main()