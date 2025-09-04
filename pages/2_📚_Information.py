"""
DeepCode - Information Page (Original Content)
"""

import streamlit as st
import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ui.components import display_header, display_features
from ui.styles import get_main_styles

# Page config
st.set_page_config(
    page_title="DeepCode - Information",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Apply original styles
    st.markdown(get_main_styles(), unsafe_allow_html=True)
    
    # Navigation
    st.markdown("## 📚 DeepCode Information & Documentation")
    
    # Back to home button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Back to Home", type="secondary", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
    
    st.markdown("---")
    
    # Original header and features display
    display_header()
    display_features()
    
    # Additional documentation sections
    st.markdown("---")
    
    # Getting Started section
    with st.expander("🚀 Getting Started", expanded=False):
        st.markdown("""
        ### Quick Start Guide
        
        1. **Register an Account**: Sign up with your email and password
        2. **Set Up 2FA**: Configure two-factor authentication for security
        3. **Add API Keys**: Configure your LLM provider API keys in your profile
        4. **Start Researching**: Use the main prompt to begin your research
        
        ### Supported Input Types
        - **Text**: Direct research questions or code requirements
        - **URLs**: Research paper URLs (arXiv, academic journals)
        - **Files**: PDF papers, code files, documentation
        
        ### Available Workflows
        - **Paper2Code**: Convert research papers to implementation
        - **Text2Web**: Generate web applications from descriptions
        - **Codebase Analysis**: Analyze and understand existing code
        """)
    
    # LLM Providers section
    with st.expander("🤖 Supported LLM Providers", expanded=False):
        st.markdown("""
        ### Integrated Providers
        
        **OpenAI**
        - GPT-4 Turbo, GPT-4, GPT-3.5 Turbo
        - Specialized for code generation and analysis
        
        **Anthropic**
        - Claude 3 Opus, Sonnet, Haiku
        - Excellent for document analysis and reasoning
        
        **DeepSeek**
        - DeepSeek Coder models
        - Optimized for coding tasks
        
        **Google Gemini**
        - Gemini Pro, Ultra
        - Multimodal analysis capabilities
        
        **OpenRouter**
        - Access to various open-source models
        - Cost-effective alternatives
        
        **Qwen (Alibaba)**
        - Multilingual processing
        - Strong performance on reasoning tasks
        
        **Grok (xAI)**
        - Real-time information access
        - Advanced reasoning capabilities
        
        **Brave Search**
        - Web search integration
        - Real-time information retrieval
        """)
    
    # Features & Capabilities
    with st.expander("⚡ Features & Capabilities", expanded=False):
        st.markdown("""
        ### Core Capabilities
        
        **Multi-Modal Analysis**
        - PDF document parsing and understanding
        - Image and diagram analysis
        - Code repository analysis
        - Web content extraction
        
        **Code Generation**
        - Algorithm implementation from papers
        - Web application scaffolding
        - API endpoint creation
        - Database schema design
        
        **Research Tools**
        - Academic paper analysis
        - Literature review synthesis
        - Citation extraction
        - Methodology implementation
        
        **Quality Assurance**
        - Automated testing generation
        - Code review and optimization
        - Security analysis
        - Performance benchmarking
        """)
    
    # Admin Features (if user is admin)
    from auth.authentication import check_authentication
    user = check_authentication()
    
    if user and user.get('is_admin', False):
        with st.expander("⚙️ Admin Features", expanded=False):
            st.markdown("""
            ### Administrative Capabilities
            
            **User Management**
            - Promote users to admin status
            - Monitor user activity
            - Manage API key usage
            
            **LLM Configuration**
            - Configure model-to-task assignments
            - Set priority levels for different models
            - Adjust model parameters
            - Monitor token usage
            
            **System Analytics**
            - Usage statistics and metrics
            - Performance monitoring
            - Error tracking and logging
            - Resource utilization
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👥 User Management", type="secondary"):
                    st.switch_page("pages/4_⚙️_Admin.py")
            with col2:
                if st.button("🤖 LLM Configuration", type="secondary"):
                    st.switch_page("pages/4_⚙️_Admin.py")
    
    # API Documentation
    with st.expander("📖 API & Integration", expanded=False):
        st.markdown("""
        ### Integration Options
        
        **REST API** (Coming Soon)
        - Programmatic access to all features
        - Webhook support for notifications
        - Batch processing capabilities
        
        **CLI Tool** (Available)
        - Command-line interface for automation
        - Scriptable research workflows
        - CI/CD integration support
        
        **Python SDK** (In Development)
        - Native Python integration
        - Jupyter notebook support
        - Async/await support
        """)
    
    # Support & Community
    with st.expander("🤝 Support & Community", expanded=False):
        st.markdown("""
        ### Getting Help
        
        **Documentation**
        - [GitHub Repository](https://github.com/HKUDS/DeepCode)
        - [API Documentation](https://deepcode-docs.example.com)
        - [Tutorial Videos](https://youtube.com/@deepcode)
        
        **Community**
        - [Discord Server](https://discord.gg/deepcode)
        - [GitHub Discussions](https://github.com/HKUDS/DeepCode/discussions)
        - [Stack Overflow](https://stackoverflow.com/questions/tagged/deepcode)
        
        **Contact**
        - Email: support@deepcode.ai
        - Issues: GitHub Issues page
        - Feature Requests: GitHub Discussions
        """)
    
    # Footer with version info
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🧬 DeepCode v2.0 | Open Source AI Research Engine</p>
        <p>Developed by Data Intelligence Lab @ HKU</p>
        <p>Licensed under MIT License</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()