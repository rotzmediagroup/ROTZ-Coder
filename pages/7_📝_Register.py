"""
DeepCode - Registration Page
"""

import streamlit as st
import os
import sys
import re

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auth.authentication import register_user, check_authentication
from utils.database import get_db_session

# Page config
st.set_page_config(
    page_title="DeepCode - Register",
    page_icon="📝",
    layout="centered"
)

# Custom CSS (similar to login page)
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
    
    /* Register container */
    .register-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        max-width: 450px;
        margin: 2rem auto;
        text-align: center;
    }
    
    .register-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .register-subtitle {
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
    
    /* Password requirements */
    .password-requirements {
        text-align: left;
        margin: 1rem 0;
        padding: 1rem;
        background: #F3F4F6;
        border-radius: 10px;
        font-size: 0.9rem;
    }
    
    .password-requirements ul {
        margin: 0.5rem 0;
        padding-left: 1.2rem;
    }
    
    .password-requirements li {
        margin: 0.2rem 0;
        color: #6B7280;
    }
    
    .password-requirements li.valid {
        color: #10B981;
    }
    
    .password-requirements li.invalid {
        color: #EF4444;
    }
    
    /* Links */
    .register-links {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
    
    .register-links a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    
    .register-links a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    requirements = {
        'length': len(password) >= 8,
        'uppercase': any(c.isupper() for c in password),
        'lowercase': any(c.islower() for c in password),
        'number': any(c.isdigit() for c in password),
        'special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    }
    return requirements

def main():
    # Check if already authenticated
    user = check_authentication()
    if user:
        st.success(f"Already logged in as {user['email']}")
        if st.button("🏠 Go to Homepage"):
            st.switch_page("pages/1_🏠_Home.py")
        return
    
    # Register container
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="register-title">📝 Sign Up</div>
    <div class="register-subtitle">Join the DeepCode community</div>
    """, unsafe_allow_html=True)
    
    # Registration form
    with st.form("register_form"):
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="register_name"
        )
        
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email",
            key="register_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password",
            key="register_password"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password",
            key="confirm_password"
        )
        
        # Show password requirements
        if password:
            requirements = validate_password(password)
            
            st.markdown('<div class="password-requirements">', unsafe_allow_html=True)
            st.markdown("**Password Requirements:**")
            
            req_html = "<ul>"
            req_html += f"<li class=\"{'valid' if requirements['length'] else 'invalid'}\">At least 8 characters</li>"
            req_html += f"<li class=\"{'valid' if requirements['uppercase'] else 'invalid'}\">One uppercase letter</li>"
            req_html += f"<li class=\"{'valid' if requirements['lowercase'] else 'invalid'}\">One lowercase letter</li>"
            req_html += f"<li class=\"{'valid' if requirements['number'] else 'invalid'}\">One number</li>"
            req_html += f"<li class=\"{'valid' if requirements['special'] else 'invalid'}\">One special character</li>"
            req_html += "</ul>"
            
            st.markdown(req_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Terms agreement
        terms_agreed = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            key="terms_checkbox"
        )
        
        submitted = st.form_submit_button("🚀 Create Account", type="primary")
        
        if submitted:
            # Validation
            errors = []
            
            if not full_name or len(full_name.strip()) < 2:
                errors.append("Please enter a valid full name")
            
            if not email or not validate_email(email):
                errors.append("Please enter a valid email address")
            
            if not password:
                errors.append("Please enter a password")
            else:
                requirements = validate_password(password)
                if not all(requirements.values()):
                    errors.append("Password does not meet all requirements")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if not terms_agreed:
                errors.append("Please agree to the Terms of Service")
            
            # Show errors
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Attempt registration
                with st.spinner("Creating your account..."):
                    with get_db_session() as session:
                        result = register_user(session, email, password, full_name.strip())
                        
                        if result is None:
                            st.error("An account with this email already exists")
                        else:
                            st.success("🎉 Account created successfully!")
                            st.info("Please proceed to login and set up two-factor authentication")
                            
                            # Show special message for jerome@rotz.host
                            if email == "jerome@rotz.host":
                                st.success("🎖️ You've been automatically granted super admin privileges!")
                            
                            # Auto-redirect to login after a moment
                            if st.button("🔑 Go to Login", type="primary"):
                                st.switch_page("pages/6_🔑_Login.py")
    
    # Navigation links
    st.markdown("""
    <div class="register-links">
        <p>Already have an account? <a href="?page=Login">Sign in here</a></p>
        <p><a href="?page=Home">← Back to Homepage</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔑 Sign In", type="secondary"):
            st.switch_page("pages/6_🔑_Login.py")
    
    with col2:
        if st.button("🏠 Back to Home", type="secondary"):
            st.switch_page("pages/1_🏠_Home.py")
    
    # Privacy notice
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; margin-top: 2rem;">
        <p>🔒 Your data is encrypted and secure</p>
        <p>🛡️ Two-factor authentication required for enhanced security</p>
        <p>🔐 API keys are encrypted and stored securely</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()