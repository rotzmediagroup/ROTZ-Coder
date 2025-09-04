"""
DeepCode - Results Page
"""

import streamlit as st
import os
import sys
import json
import time

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auth.authentication import require_authentication
from utils.database import get_db_session, save_research_task, update_research_task, get_user_api_key
from ui.handlers import handle_start_processing_button
from ui.components import results_display_component

# Page config
st.set_page_config(
    page_title="DeepCode - Results",
    page_icon="📊",
    layout="wide"
)

def main():
    # Require authentication
    user = require_authentication()
    
    st.title("📊 Research Results")
    
    # Navigation
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏠 Home", type="secondary"):
            st.switch_page("pages/1_🏠_Home.py")
    with col2:
        if st.button("📚 Information", type="secondary"):
            st.switch_page("pages/2_📚_Information.py")
    with col3:
        if st.button("👤 Profile", type="secondary"):
            st.switch_page("pages/3_👤_Profile.py")
    with col4:
        if st.button("🔄 New Research", type="secondary"):
            # Clear processing state and go home
            if 'processing_input' in st.session_state:
                del st.session_state.processing_input
            if 'processing_result' in st.session_state:
                del st.session_state.processing_result
            st.switch_page("pages/1_🏠_Home.py")
    
    st.markdown("---")
    
    # Check if we have input to process
    if 'processing_input' in st.session_state and 'processing_result' not in st.session_state:
        process_input(user)
    elif 'processing_result' in st.session_state:
        display_results(user)
    else:
        # No input - show recent results or redirect to home
        show_recent_results(user)


def process_input(user):
    """Process the user input"""
    input_data = st.session_state.processing_input
    
    st.header("🔄 Processing Your Request")
    
    # Show what we're processing
    if input_data.get('text'):
        st.subheader("📝 Text Input")
        st.text_area("Your input:", input_data['text'], height=100, disabled=True)
    
    if input_data.get('url'):
        st.subheader("🔗 URL Input")
        st.text(input_data['url'])
    
    if input_data.get('file'):
        st.subheader("📁 File Input")
        st.text(f"File: {input_data['file'].name} ({input_data['file'].size} bytes)")
    
    # Check API key availability
    with get_db_session() as session:
        has_openai = get_user_api_key(session, user['user_id'], 'openai') is not None
        has_anthropic = get_user_api_key(session, user['user_id'], 'anthropic') is not None
        has_brave = get_user_api_key(session, user['user_id'], 'brave') is not None
    
    if not (has_openai or has_anthropic):
        st.error("🔑 No LLM API keys configured! Please add your API keys in your profile.")
        if st.button("👤 Go to Profile", type="primary"):
            st.switch_page("pages/3_👤_Profile.py")
        return
    
    # Processing status
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate processing (replace with actual processing logic)
    with st.spinner("Processing your request..."):
        # Save task to database
        task_id = save_research_task(
            user_id=user['user_id'],
            task_type='general_research',
            input_type='text' if input_data.get('text') else 'url' if input_data.get('url') else 'file',
            input_data=input_data.get('text', input_data.get('url', input_data.get('file', {}).name if input_data.get('file') else '')),
            status='processing'
        )
        
        # Simulate processing steps
        steps = [
            "Analyzing input...",
            "Selecting optimal LLM model...",
            "Generating research plan...",
            "Processing with AI agents...",
            "Synthesizing results...",
            "Finalizing output..."
        ]
        
        start_time = time.time()
        
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(2)  # Simulate processing time
        
        processing_time = time.time() - start_time
        
        # Mock result (replace with actual processing result)
        mock_result = {
            "summary": "Research analysis completed successfully",
            "key_findings": [
                "Identified main algorithmic approaches",
                "Found relevant implementation patterns",
                "Extracted key mathematical models"
            ],
            "generated_code": """
# Example generated code
def research_function(input_data):
    \"\"\"
    Generated function based on research analysis
    \"\"\"
    results = []
    
    # Process input data
    for item in input_data:
        processed = analyze_item(item)
        results.append(processed)
    
    return results

def analyze_item(item):
    \"\"\"
    Analyze individual item
    \"\"\"
    # Implementation based on research findings
    return {"processed": item, "confidence": 0.95}
            """,
            "recommendations": [
                "Consider implementing additional error handling",
                "Add unit tests for generated functions",
                "Optimize for large-scale data processing"
            ],
            "references": [
                "https://arxiv.org/abs/example1",
                "https://github.com/example/repo",
                "https://docs.example.com/api"
            ]
        }
        
        # Update task in database
        update_research_task(
            task_id=task_id,
            status='completed',
            result=mock_result,
            processing_time=processing_time,
            tokens_used=1250  # Mock token count
        )
        
        # Store result in session state
        st.session_state.processing_result = {
            'task_id': task_id,
            'result': mock_result,
            'processing_time': processing_time,
            'tokens_used': 1250
        }
        
        st.success("✅ Processing completed!")
        st.balloons()
        time.sleep(1)
        st.rerun()


def display_results(user):
    """Display the processing results"""
    result_data = st.session_state.processing_result
    result = result_data['result']
    
    st.header("✅ Research Results")
    
    # Processing info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Processing Time", f"{result_data['processing_time']:.2f}s")
    with col2:
        st.metric("Tokens Used", f"{result_data['tokens_used']:,}")
    with col3:
        st.metric("Status", "✅ Completed")
    
    st.markdown("---")
    
    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "💻 Generated Code", "🎯 Recommendations", "📚 References"])
    
    with tab1:
        st.subheader("📋 Research Summary")
        st.write(result['summary'])
        
        st.subheader("🔍 Key Findings")
        for finding in result['key_findings']:
            st.write(f"• {finding}")
    
    with tab2:
        st.subheader("💻 Generated Code")
        st.code(result['generated_code'], language='python')
        
        # Download button
        if st.button("💾 Download Code", type="secondary"):
            st.download_button(
                label="📥 Download Python File",
                data=result['generated_code'],
                file_name="generated_code.py",
                mime="text/python"
            )
    
    with tab3:
        st.subheader("🎯 Recommendations")
        for rec in result['recommendations']:
            st.info(f"💡 {rec}")
    
    with tab4:
        st.subheader("📚 References")
        for ref in result['references']:
            st.markdown(f"- [{ref}]({ref})")
    
    # Action buttons
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 New Research", type="primary"):
            # Clear session state
            if 'processing_input' in st.session_state:
                del st.session_state.processing_input
            if 'processing_result' in st.session_state:
                del st.session_state.processing_result
            st.switch_page("pages/1_🏠_Home.py")
    
    with col2:
        if st.button("💾 Save Results", type="secondary"):
            # Results are automatically saved to database
            st.success("Results saved to your profile!")
    
    with col3:
        if st.button("🔗 Share Results", type="secondary"):
            st.info("Sharing functionality will be available in a future update")
    
    with col4:
        if st.button("📊 View History", type="secondary"):
            st.switch_page("pages/3_👤_Profile.py")


def show_recent_results(user):
    """Show recent results if no current processing"""
    st.header("📊 Your Research History")
    
    from utils.database import get_user_research_tasks
    
    with get_db_session() as session:
        recent_tasks = get_user_research_tasks(user['user_id'], limit=10)
    
    if not recent_tasks:
        st.info("No research history found. Start by creating a new research task!")
        if st.button("🚀 Start New Research", type="primary"):
            st.switch_page("pages/1_🏠_Home.py")
        return
    
    st.write(f"Showing your last {len(recent_tasks)} research tasks:")
    
    for i, task in enumerate(recent_tasks):
        with st.expander(
            f"{'✅' if task.status == 'completed' else '⏳' if task.status == 'processing' else '❌' if task.status == 'failed' else '⏸️'} "
            f"{task.task_type or 'Research Task'} - {task.created_at.strftime('%Y-%m-%d %H:%M')}"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Status:** {task.status.title()}")
                st.write(f"**Type:** {task.task_type or 'General'}")
                st.write(f"**Input Type:** {task.input_type or 'Text'}")
            
            with col2:
                if task.processing_time:
                    st.write(f"**Processing Time:** {task.processing_time:.2f}s")
                if task.tokens_used:
                    st.write(f"**Tokens Used:** {task.tokens_used:,}")
                if task.completed_at:
                    st.write(f"**Completed:** {task.completed_at.strftime('%Y-%m-%d %H:%M')}")
            
            if task.input_data:
                st.write("**Input:**")
                input_preview = task.input_data[:200] + "..." if len(task.input_data) > 200 else task.input_data
                st.text(input_preview)
            
            if task.error_message:
                st.error(f"Error: {task.error_message}")
            
            if task.result and task.status == 'completed':
                if st.button(f"👀 View Full Results", key=f"view_{task.id}"):
                    # Load this result into session state
                    st.session_state.processing_result = {
                        'task_id': task.id,
                        'result': task.result,
                        'processing_time': task.processing_time or 0,
                        'tokens_used': task.tokens_used or 0
                    }
                    st.rerun()
    
    # New research button
    st.markdown("---")
    if st.button("🚀 Start New Research", type="primary", use_container_width=True):
        st.switch_page("pages/1_🏠_Home.py")


if __name__ == "__main__":
    main()