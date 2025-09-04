"""
DeepCode - AI Research Engine

Enhanced Streamlit Web Interface with Authentication and Multi-LLM Support
"""

import os
import sys
import streamlit as st

# Disable .pyc file generation
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Add parent directory to path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Initialize database on first run
@st.cache_resource
def initialize_database():
    """Initialize database tables and super admin"""
    try:
        from utils.database import init_database_tables
        init_database_tables()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")
        return False


def main():
    """
    Main function - Enhanced Streamlit application entry
    
    Now supports:
    - User authentication with TOTP
    - Multi-LLM provider support
    - Clean UI with modern design
    - Admin panel for configuration
    """
    # Initialize database
    if not initialize_database():
        st.error("❌ Database initialization failed. Please check your configuration.")
        st.stop()
    
    # Set page config for new multi-page structure
    st.set_page_config(
        page_title="DeepCode - AI Research Engine",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Welcome message
    st.success("🎉 DeepCode has been enhanced with user authentication and multi-LLM support!")
    st.info("👈 Use the sidebar navigation or click the buttons below to explore the new features.")
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Go to Homepage", type="primary", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
    
    with col2:
        if st.button("🔑 Login", type="secondary", use_container_width=True):
            st.switch_page("pages/6_🔑_Login.py")
    
    with col3:
        if st.button("📝 Register", type="secondary", use_container_width=True):
            st.switch_page("pages/7_📝_Register.py")
    
    with col4:
        if st.button("📚 Information", type="secondary", use_container_width=True):
            st.switch_page("pages/2_📚_Information.py")
    
    st.markdown("---")
    
    # New features overview
    st.header("🆕 New Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔐 User Authentication")
        st.write("- Email/password registration")
        st.write("- Two-factor authentication (TOTP)")
        st.write("- Secure session management")
        st.write("- Personal API key storage")
        
        st.subheader("🤖 Multi-LLM Support")
        st.write("- OpenAI (GPT-4, GPT-3.5)")
        st.write("- Anthropic (Claude 3)")
        st.write("- DeepSeek (Coder models)")
        st.write("- Google Gemini")
    
    with col2:
        st.subheader("⚙️ Admin Features")
        st.write("- User management")
        st.write("- LLM configuration")
        st.write("- Model-to-task assignment")
        st.write("- System analytics")
        
        st.subheader("🌐 Additional Providers")
        st.write("- OpenRouter (various models)")
        st.write("- Qwen (multilingual)")
        st.write("- Grok (real-time data)")
        st.write("- Brave Search integration")
    
    st.markdown("---")
    
    # Super admin info
    st.info("""
    **Super Admin Account**: jerome@rotz.host has been automatically created with super admin privileges.
    
    Default password: `ChangeMe123!` (Please change on first login)
    
    The super admin can:
    - Promote users to admin status
    - Configure LLM providers and models
    - Manage system settings
    - View system analytics
    """)
    
    # System status
    st.subheader("📊 System Status")
    
    # Check database connection
    try:
        from utils.database import get_db_session
        with get_db_session() as session:
            from database.models import User
            user_count = session.query(User).count()
            st.success(f"✅ Database connected - {user_count} users registered")
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
    
    # Check providers
    try:
        from providers.provider_factory import LLMProviderFactory
        provider_count = len(LLMProviderFactory.get_available_providers())
        st.success(f"✅ LLM providers ready - {provider_count} providers available")
        
        # Show available providers
        providers = LLMProviderFactory.get_available_providers()
        st.write("Available providers:", ", ".join(providers))
        
    except Exception as e:
        st.error(f"❌ Provider initialization failed: {str(e)}")


if __name__ == "__main__":
    main()
