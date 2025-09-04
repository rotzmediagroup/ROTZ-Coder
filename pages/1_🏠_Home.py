"""
DeepCode - Clean Homepage with Hero Section
"""

import streamlit as st
from auth.authentication import check_authentication, logout
from utils.database import get_db_session
import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Page config
st.set_page_config(
    page_title="DeepCode - AI Research Engine",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"  # Clean homepage
)

# Custom CSS for clean, modern design (lovable.dev inspired)
st.markdown("""
<style>
    /* Hide Streamlit branding and menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .stApp > div:first-child {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Hero section styling */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
        padding: 2rem;
        text-align: center;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #ffffff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 3rem;
        max-width: 600px;
        line-height: 1.6;
    }
    
    /* Prompt box styling */
    .prompt-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        max-width: 800px;
        width: 100%;
        margin: 0 auto;
    }
    
    .prompt-label {
        font-size: 1.2rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        text-align: left;
    }
    
    /* Navigation styling */
    .nav-container {
        position: absolute;
        top: 2rem;
        right: 2rem;
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .user-info {
        color: white;
        font-weight: 500;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        backdrop-filter: blur(10px);
    }
    
    .logout-btn {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 0.5rem 1.5rem !important;
        backdrop-filter: blur(10px);
    }
    
    .logout-btn:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Feature cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 4rem;
        max-width: 1200px;
        padding: 0 2rem;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.5;
    }
    
    /* Bottom links */
    .bottom-links {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 2rem;
    }
    
    .bottom-link {
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .bottom-link:hover {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        text-decoration: none;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .prompt-container {
            padding: 1.5rem;
            margin: 0 1rem;
        }
        
        .nav-container {
            position: relative;
            top: 1rem;
            right: auto;
            justify-content: center;
        }
        
        .bottom-links {
            flex-direction: column;
            align-items: center;
            gap: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check authentication
    user = check_authentication()
    
    # Navigation bar
    if user:
        st.markdown(f"""
        <div class="nav-container">
            <div class="user-info">
                👋 {user.get('full_name', user.get('email', 'User'))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button in sidebar
        with st.sidebar:
            if st.button("🚪 Logout", key="logout_btn", type="secondary"):
                logout()
                st.rerun()
    
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">🧬 DeepCode</h1>
        <p class="hero-subtitle">
            Revolutionary AI Research Engine • Transform papers into production-ready code • 
            Powered by multi-agent systems and cutting-edge language models
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Prompt Container
    st.markdown('<div class="prompt-container">', unsafe_allow_html=True)
    st.markdown('<div class="prompt-label">What would you like to research or build today?</div>', unsafe_allow_html=True)
    
    # Only show prompt interface if user is authenticated
    if user:
        # Main prompt input
        user_input = st.text_area(
            "",
            placeholder="Enter your research question, paste a research paper URL, or describe what you want to build...",
            height=120,
            key="main_prompt",
            label_visibility="collapsed"
        )
        
        # Input options
        col1, col2 = st.columns(2)
        with col1:
            file_upload = st.file_uploader(
                "Or upload a file",
                type=['pdf', 'txt', 'py', 'js', 'html', 'css', 'md'],
                label_visibility="visible"
            )
        
        with col2:
            url_input = st.text_input(
                "Or paste a URL",
                placeholder="https://arxiv.org/abs/...",
                label_visibility="visible"
            )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                if user_input or file_upload or url_input:
                    # Store the input in session state and redirect to processing
                    st.session_state.processing_input = {
                        'text': user_input,
                        'file': file_upload,
                        'url': url_input,
                        'user_id': user['user_id']
                    }
                    st.switch_page("pages/5_📊_Results.py")
                else:
                    st.warning("Please provide some input to process.")
        
        with col2:
            if st.button("📚 Learn More", type="secondary", use_container_width=True):
                st.switch_page("pages/2_📚_Information.py")
        
        with col3:
            if st.button("👤 My Profile", type="secondary", use_container_width=True):
                st.switch_page("pages/3_👤_Profile.py")
    
    else:
        # Not authenticated - show login prompt
        st.info("🔐 Please log in to start using DeepCode")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", type="primary", use_container_width=True):
                st.switch_page("pages/6_🔑_Login.py")
        
        with col2:
            if st.button("📝 Sign Up", type="secondary", use_container_width=True):
                st.switch_page("pages/7_📝_Register.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feature highlights (always visible)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Paper2Code</div>
            <div class="feature-description">
                Transform research papers into production-ready implementations with automated algorithm extraction
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">Text2Web</div>
            <div class="feature-description">
                Generate complete web applications from natural language descriptions using intelligent scaffolding
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Multi-Agent AI</div>
            <div class="feature-description">
                Powered by collaborative AI agents working together to solve complex programming challenges
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bottom navigation links
    st.markdown("""
    <div class="bottom-links">
        <a href="?page=Information" class="bottom-link">📚 Documentation</a>
        <a href="https://github.com/HKUDS/DeepCode" class="bottom-link" target="_blank">🔗 GitHub</a>
        <a href="?page=Profile" class="bottom-link">⚙️ Settings</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()