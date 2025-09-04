"""
DeepCode - Admin Panel
"""

import streamlit as st
import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auth.authentication import require_admin, require_super_admin
from utils.database import (
    get_db_session, get_all_users, update_user_admin_status,
    get_llm_configurations, save_llm_configuration, delete_llm_configuration
)
from database.models import User, LLMConfiguration, ResearchTask, UserApiKey

# Page config
st.set_page_config(
    page_title="DeepCode - Admin Panel",
    page_icon="⚙️",
    layout="wide"
)

def main():
    # Require admin authentication
    user = require_admin()
    
    st.title("⚙️ Admin Panel")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Home", type="secondary"):
            st.switch_page("pages/1_🏠_Home.py")
    with col2:
        if st.button("👤 Profile", type="secondary"):
            st.switch_page("pages/3_👤_Profile.py")
    with col3:
        if st.button("📚 Information", type="secondary"):
            st.switch_page("pages/2_📚_Information.py")
    
    st.markdown("---")
    
    # Show different tabs based on user privileges
    if user.get('is_super_admin', False):
        tabs = st.tabs(["👥 Users", "🤖 LLM Config", "📊 Analytics", "⚙️ System"])
        
        with tabs[0]:
            user_management_section(user)
        with tabs[1]:
            llm_configuration_section(user)
        with tabs[2]:
            analytics_section(user)
        with tabs[3]:
            system_settings_section(user)
    else:
        tabs = st.tabs(["🤖 LLM Config", "📊 Analytics"])
        
        with tabs[0]:
            llm_configuration_section(user)
        with tabs[1]:
            analytics_section(user)


def user_management_section(user):
    """User management section (Super Admin only)"""
    st.header("👥 User Management")
    
    # Only super admins can access this
    if not user.get('is_super_admin', False):
        st.error("🔒 Super admin privileges required")
        return
    
    with get_db_session() as session:
        users = session.query(User).all()
    
    st.write(f"Total Users: {len(users)}")
    
    # User list
    for db_user in users:
        with st.expander(
            f"{'👑' if db_user.is_super_admin else '⚙️' if db_user.is_admin else '👤'} "
            f"{db_user.full_name or db_user.email}"
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Email:** {db_user.email}")
                st.write(f"**Name:** {db_user.full_name or 'Not set'}")
                st.write(f"**Joined:** {db_user.created_at.strftime('%Y-%m-%d')}")
            
            with col2:
                st.write(f"**Admin:** {'Yes' if db_user.is_admin else 'No'}")
                st.write(f"**Super Admin:** {'Yes' if db_user.is_super_admin else 'No'}")
                st.write(f"**2FA Enabled:** {'Yes' if db_user.totp_secret else 'No'}")
            
            with col3:
                # Admin status toggle (can't change super admin status)
                if db_user.email != "jerome@rotz.host":  # Can't modify super admin
                    if st.button(
                        f"{'Remove Admin' if db_user.is_admin else 'Make Admin'}",
                        key=f"toggle_admin_{db_user.id}",
                        type="secondary"
                    ):
                        if update_user_admin_status(db_user.id, not db_user.is_admin):
                            st.success(f"Updated admin status for {db_user.email}")
                            st.rerun()
                        else:
                            st.error("Failed to update admin status")
                else:
                    st.info("Super Admin (Permanent)")
            
            # Show user's API keys count
            with get_db_session() as session:
                api_key_count = session.query(UserApiKey).filter_by(
                    user_id=db_user.id, is_active=True
                ).count()
                
                task_count = session.query(ResearchTask).filter_by(
                    user_id=db_user.id
                ).count()
                
                st.write(f"**API Keys:** {api_key_count}")
                st.write(f"**Research Tasks:** {task_count}")


def llm_configuration_section(user):
    """LLM configuration section"""
    st.header("🤖 LLM Configuration")
    
    # Add new configuration
    with st.expander("➕ Add New LLM Configuration", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            provider = st.selectbox(
                "Provider",
                ["openai", "anthropic", "deepseek", "gemini", "openrouter", "qwen", "grok"],
                key="new_provider"
            )
            
            model_name = st.text_input(
                "Model Name",
                placeholder="e.g., gpt-4-turbo-preview",
                key="new_model"
            )
            
            task_type = st.selectbox(
                "Task Type",
                ["code_generation", "document_analysis", "code_review", "general_query", 
                 "multimodal_analysis", "multilingual_processing", "reasoning", "web_search"],
                key="new_task_type"
            )
        
        with col2:
            priority = st.number_input(
                "Priority (1=highest)",
                min_value=1,
                max_value=10,
                value=1,
                key="new_priority"
            )
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                key="new_temperature"
            )
            
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=8000,
                value=2000,
                key="new_max_tokens"
            )
        
        if st.button("💾 Save Configuration", type="primary"):
            parameters = {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if save_llm_configuration(
                provider, model_name, task_type, priority, parameters, user['user_id']
            ):
                st.success("Configuration saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save configuration")
    
    # Current configurations
    st.subheader("Current LLM Configurations")
    
    configs = get_llm_configurations()
    
    if not configs:
        st.info("No LLM configurations found. Add some above!")
        return
    
    # Group by task type
    task_types = {}
    for config in configs:
        if config.task_type not in task_types:
            task_types[config.task_type] = []
        task_types[config.task_type].append(config)
    
    for task_type, task_configs in task_types.items():
        with st.expander(f"📋 {task_type.replace('_', ' ').title()}", expanded=True):
            
            for config in task_configs:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{config.provider}** - {config.model_name}")
                
                with col2:
                    st.write(f"Priority: {config.priority}")
                    if config.parameters:
                        temp = config.parameters.get('temperature', 'N/A')
                        tokens = config.parameters.get('max_tokens', 'N/A')
                        st.write(f"Temp: {temp}, Tokens: {tokens}")
                
                with col3:
                    st.write("🟢 Active" if config.is_active else "🔴 Inactive")
                
                with col4:
                    if st.button(
                        "🗑️",
                        key=f"delete_{config.id}",
                        help="Delete configuration"
                    ):
                        if delete_llm_configuration(config.id):
                            st.success("Configuration deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete configuration")


def analytics_section(user):
    """System analytics section"""
    st.header("📊 System Analytics")
    
    with get_db_session() as session:
        # Basic stats
        total_users = session.query(User).count()
        admin_users = session.query(User).filter_by(is_admin=True).count()
        total_tasks = session.query(ResearchTask).count()
        completed_tasks = session.query(ResearchTask).filter_by(status='completed').count()
        active_api_keys = session.query(UserApiKey).filter_by(is_active=True).count()
        
        # Recent activity
        recent_tasks = session.query(ResearchTask).order_by(
            ResearchTask.created_at.desc()
        ).limit(10).all()
        
        recent_users = session.query(User).order_by(
            User.created_at.desc()
        ).limit(5).all()
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", total_users)
        st.metric("Admin Users", admin_users)
    
    with col2:
        st.metric("Total Tasks", total_tasks)
        st.metric("Completed Tasks", completed_tasks)
    
    with col3:
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
        st.metric("Active API Keys", active_api_keys)
    
    with col4:
        # Task distribution by status
        with get_db_session() as session:
            pending = session.query(ResearchTask).filter_by(status='pending').count()
            processing = session.query(ResearchTask).filter_by(status='processing').count()
            failed = session.query(ResearchTask).filter_by(status='failed').count()
        
        st.metric("Pending", pending)
        st.metric("Processing", processing)
        st.metric("Failed", failed)
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Tasks")
        for task in recent_tasks:
            status_icon = {
                'completed': '✅',
                'processing': '⏳',
                'failed': '❌',
                'pending': '⏸️'
            }.get(task.status, '❓')
            
            st.write(f"{status_icon} {task.task_type or 'General'} - {task.created_at.strftime('%m/%d %H:%M')}")
    
    with col2:
        st.subheader("Recent Users")
        for user_item in recent_users:
            st.write(f"👤 {user_item.full_name or user_item.email} - {user_item.created_at.strftime('%m/%d')}")


def system_settings_section(user):
    """System settings section (Super Admin only)"""
    st.header("⚙️ System Settings")
    
    if not user.get('is_super_admin', False):
        st.error("🔒 Super admin privileges required")
        return
    
    # Database settings
    st.subheader("🗄️ Database")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reinitialize Database", type="secondary"):
            st.warning("This will recreate all database tables. Existing data will be preserved.")
            if st.button("⚠️ Confirm Reinitialize", type="primary"):
                from utils.database import init_database_tables
                try:
                    init_database_tables()
                    st.success("Database reinitialized successfully!")
                except Exception as e:
                    st.error(f"Database reinitialization failed: {str(e)}")
    
    with col2:
        if st.button("📊 Database Stats", type="secondary"):
            with get_db_session() as session:
                stats = {
                    "Users": session.query(User).count(),
                    "API Keys": session.query(UserApiKey).count(),
                    "LLM Configs": session.query(LLMConfiguration).count(),
                    "Research Tasks": session.query(ResearchTask).count(),
                }
                
                for table, count in stats.items():
                    st.write(f"**{table}:** {count}")
    
    # System maintenance
    st.subheader("🛠️ Maintenance")
    
    if st.button("🧹 Clean Old Sessions", type="secondary"):
        st.info("Session cleanup functionality will be implemented in future updates.")
    
    if st.button("📋 Generate System Report", type="secondary"):
        st.info("System report functionality will be implemented in future updates.")
    
    # Environment info
    st.subheader("💻 Environment")
    
    import platform
    import sys
    
    st.write(f"**Python Version:** {sys.version}")
    st.write(f"**Platform:** {platform.system()} {platform.release()}")
    st.write(f"**Streamlit Version:** {st.__version__}")


if __name__ == "__main__":
    main()