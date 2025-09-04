"""
DeepCode - User Profile & API Key Management
"""

import streamlit as st
import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auth.authentication import require_authentication, logout, setup_user_totp, generate_totp_secret, generate_totp_qr_code
from auth.encryption import store_user_api_key, get_user_api_key, delete_user_api_key, mask_api_key, validate_api_key_format
from utils.database import get_db_session, get_user_research_tasks
from database.models import User

# Page config
st.set_page_config(
    page_title="DeepCode - Profile",
    page_icon="👤",
    layout="wide"
)

def main():
    # Require authentication
    user = require_authentication()
    
    st.title("👤 User Profile")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Home", type="secondary"):
            st.switch_page("pages/1_🏠_Home.py")
    with col2:
        if st.button("📚 Information", type="secondary"):
            st.switch_page("pages/2_📚_Information.py")
    with col3:
        if st.button("🚪 Logout", type="secondary"):
            logout()
            st.rerun()
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 API Keys", "📊 Usage History", "🔒 Security", "⚙️ Settings"])
    
    with tab1:
        api_keys_section(user)
    
    with tab2:
        usage_history_section(user)
    
    with tab3:
        security_section(user)
    
    with tab4:
        settings_section(user)


def api_keys_section(user):
    """API Keys management section"""
    st.header("🔑 API Key Management")
    
    st.info("""
    🔐 **Secure Storage**: All API keys are encrypted using industry-standard encryption.
    🔄 **Personal Use**: These keys are only used for your research tasks.
    🚫 **Private**: Your keys are never shared with other users or stored in logs.
    """)
    
    # Supported providers
    providers = {
        "openai": {
            "name": "OpenAI",
            "icon": "🤖",
            "description": "GPT-4, GPT-3.5 Turbo models for code generation and analysis",
            "help_url": "https://platform.openai.com/api-keys"
        },
        "anthropic": {
            "name": "Anthropic",
            "icon": "🧠",
            "description": "Claude 3 models for document analysis and reasoning",
            "help_url": "https://console.anthropic.com/settings/keys"
        },
        "brave": {
            "name": "Brave Search",
            "icon": "🔍",
            "description": "Web search integration for real-time information",
            "help_url": "https://api.search.brave.com/app/keys"
        },
        "deepseek": {
            "name": "DeepSeek",
            "icon": "🚀",
            "description": "DeepSeek Coder models optimized for programming tasks",
            "help_url": "https://platform.deepseek.com/api_keys"
        },
        "gemini": {
            "name": "Google Gemini",
            "icon": "💎",
            "description": "Gemini Pro models with multimodal capabilities",
            "help_url": "https://makersuite.google.com/app/apikey"
        },
        "openrouter": {
            "name": "OpenRouter",
            "icon": "🌐",
            "description": "Access to various open-source models",
            "help_url": "https://openrouter.ai/keys"
        },
        "qwen": {
            "name": "Qwen",
            "icon": "🇨🇳",
            "description": "Alibaba's Qwen models for multilingual processing",
            "help_url": "https://dashscope.aliyun.com/api-key"
        },
        "grok": {
            "name": "Grok (xAI)",
            "icon": "⚡",
            "description": "Grok models with real-time information access",
            "help_url": "https://console.x.ai/settings/api-keys"
        }
    }
    
    # Display current API keys
    with get_db_session() as session:
        for provider_id, provider_info in providers.items():
            with st.expander(f"{provider_info['icon']} {provider_info['name']}", expanded=False):
                
                # Check if user has this API key
                existing_key = get_user_api_key(session, user['user_id'], provider_id)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**{provider_info['description']}**")
                    
                    if existing_key:
                        st.success(f"✅ API key configured: {mask_api_key(existing_key)}")
                        
                        if st.button(f"🗑️ Remove {provider_info['name']} Key", 
                                   key=f"remove_{provider_id}"):
                            if delete_user_api_key(session, user['user_id'], provider_id):
                                st.success(f"API key for {provider_info['name']} removed successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to remove API key.")
                    else:
                        st.warning("⚠️ No API key configured")
                        
                        # Add new API key
                        new_key = st.text_input(
                            f"Enter {provider_info['name']} API Key:",
                            type="password",
                            key=f"new_key_{provider_id}",
                            placeholder=f"Enter your {provider_info['name']} API key..."
                        )
                        
                        if st.button(f"💾 Save {provider_info['name']} Key", 
                                   key=f"save_{provider_id}"):
                            if new_key:
                                if validate_api_key_format(new_key, provider_id):
                                    if store_user_api_key(session, user['user_id'], provider_id, new_key):
                                        st.success(f"API key for {provider_info['name']} saved successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to save API key.")
                                else:
                                    st.error(f"Invalid API key format for {provider_info['name']}.")
                            else:
                                st.error("Please enter an API key.")
                
                with col2:
                    st.markdown(f"[Get API Key →]({provider_info['help_url']})")


def usage_history_section(user):
    """Usage history section"""
    st.header("📊 Usage History")
    
    with get_db_session() as session:
        tasks = get_user_research_tasks(user['user_id'], limit=20)
    
    if not tasks:
        st.info("No research tasks found. Start by using the main prompt on the homepage!")
        return
    
    st.write(f"Showing your last {len(tasks)} research tasks:")
    
    for task in tasks:
        with st.expander(
            f"{'✅' if task.status == 'completed' else '⏳' if task.status == 'processing' else '❌' if task.status == 'failed' else '⏸️'} "
            f"{task.task_type or 'Research Task'} - {task.created_at.strftime('%Y-%m-%d %H:%M')}"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Status:** {task.status.title()}")
                st.write(f"**Type:** {task.task_type or 'General'}")
                st.write(f"**Input Type:** {task.input_type or 'Text'}")
                if task.processing_time:
                    st.write(f"**Processing Time:** {task.processing_time:.2f}s")
                if task.tokens_used:
                    st.write(f"**Tokens Used:** {task.tokens_used:,}")
            
            with col2:
                if task.input_data:
                    st.write("**Input:**")
                    input_preview = task.input_data[:200] + "..." if len(task.input_data) > 200 else task.input_data
                    st.text(input_preview)
                
                if task.error_message:
                    st.error(f"Error: {task.error_message}")
            
            if task.result and task.status == 'completed':
                st.write("**Result:**")
                st.json(task.result)


def security_section(user):
    """Security settings section"""
    st.header("🔒 Security Settings")
    
    # TOTP Status
    with get_db_session() as session:
        db_user = session.query(User).filter_by(id=user['user_id']).first()
        has_totp = bool(db_user.totp_secret)
    
    st.subheader("🔐 Two-Factor Authentication (2FA)")
    
    if has_totp:
        st.success("✅ Two-factor authentication is enabled")
        
        if st.button("🔄 Regenerate 2FA", type="secondary"):
            st.session_state.show_totp_setup = True
            st.rerun()
    else:
        st.warning("⚠️ Two-factor authentication is not enabled")
        
        if st.button("🛡️ Enable 2FA", type="primary"):
            st.session_state.show_totp_setup = True
            st.rerun()
    
    # TOTP Setup
    if st.session_state.get('show_totp_setup', False):
        st.markdown("---")
        st.subheader("📱 Set Up Two-Factor Authentication")
        
        # Generate new secret
        if 'totp_secret' not in st.session_state:
            st.session_state.totp_secret = generate_totp_secret()
        
        # Show QR code
        qr_code = generate_totp_qr_code(user['email'], st.session_state.totp_secret)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**1. Scan this QR code with your authenticator app:**")
            st.markdown(f'<img src="data:image/png;base64,{qr_code}" style="max-width: 300px;">', 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown("**2. Enter the 6-digit code from your app:**")
            totp_code = st.text_input("TOTP Code", max_chars=6, key="totp_setup_code")
            
            col2a, col2b = st.columns(2)
            
            with col2a:
                if st.button("✅ Verify & Enable", type="primary"):
                    if totp_code and len(totp_code) == 6:
                        with get_db_session() as session:
                            if setup_user_totp(session, user['user_id'], totp_code, st.session_state.totp_secret):
                                st.success("🎉 Two-factor authentication enabled successfully!")
                                del st.session_state.totp_secret
                                del st.session_state.show_totp_setup
                                st.rerun()
                            else:
                                st.error("Invalid TOTP code. Please try again.")
                    else:
                        st.error("Please enter a 6-digit code.")
            
            with col2b:
                if st.button("❌ Cancel", type="secondary"):
                    del st.session_state.totp_secret
                    del st.session_state.show_totp_setup
                    st.rerun()
    
    # Account Information
    st.markdown("---")
    st.subheader("👤 Account Information")
    
    with get_db_session() as session:
        db_user = session.query(User).filter_by(id=user['user_id']).first()
        
        st.write(f"**Email:** {db_user.email}")
        st.write(f"**Full Name:** {db_user.full_name}")
        st.write(f"**Account Type:** {'Super Admin' if db_user.is_super_admin else 'Admin' if db_user.is_admin else 'User'}")
        st.write(f"**Member Since:** {db_user.created_at.strftime('%Y-%m-%d')}")


def settings_section(user):
    """General settings section"""
    st.header("⚙️ General Settings")
    
    # Theme settings (if needed in future)
    st.subheader("🎨 Appearance")
    st.info("Theme customization will be available in a future update.")
    
    # Notification settings
    st.subheader("🔔 Notifications")
    st.info("Notification preferences will be available in a future update.")
    
    # Export data
    st.subheader("📥 Data Export")
    
    if st.button("📄 Export My Data", type="secondary"):
        st.info("Data export functionality will be available in a future update.")
    
    # Account deletion
    st.subheader("⚠️ Danger Zone")
    
    if st.button("🗑️ Delete Account", type="secondary"):
        st.error("Account deletion is not yet implemented. Please contact support if needed.")


if __name__ == "__main__":
    main()