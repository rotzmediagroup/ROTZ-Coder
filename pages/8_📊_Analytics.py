"""
📊 Analytics Dashboard - Advanced analytics and insights for ROTZ Coder
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time

from analytics.dashboard import (
    get_user_analytics,
    get_api_usage_analytics,
    get_system_analytics,
    get_error_analytics,
    get_performance_analytics,
    get_comprehensive_dashboard_data
)
from analytics.collectors import track_user_activity, track_page_performance
from auth.session_manager import require_auth


def init_page():
    """Initialize the analytics page"""
    st.set_page_config(
        page_title="Analytics Dashboard - ROTZ Coder",
        page_icon="📊",
        layout="wide"
    )


def create_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """Create a metric card"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            help=help_text
        )


def plot_time_series(data: list, x_field: str, y_field: str, title: str, color: str = None):
    """Create a time series plot"""
    if not data:
        st.info(f"No data available for {title}")
        return
    
    df = pd.DataFrame(data)
    if df.empty:
        st.info(f"No data available for {title}")
        return
    
    fig = px.line(
        df, 
        x=x_field, 
        y=y_field,
        title=title,
        color_discrete_sequence=[color] if color else None
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=y_field.replace('_', ' ').title(),
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_bar_chart(data: list, x_field: str, y_field: str, title: str, color: str = None):
    """Create a bar chart"""
    if not data:
        st.info(f"No data available for {title}")
        return
    
    df = pd.DataFrame(data)
    if df.empty:
        st.info(f"No data available for {title}")
        return
    
    fig = px.bar(
        df, 
        x=x_field, 
        y=y_field,
        title=title,
        color_discrete_sequence=[color] if color else None
    )
    fig.update_layout(
        xaxis_title=x_field.replace('_', ' ').title(),
        yaxis_title=y_field.replace('_', ' ').title(),
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_pie_chart(data: list, names_field: str, values_field: str, title: str):
    """Create a pie chart"""
    if not data:
        st.info(f"No data available for {title}")
        return
    
    df = pd.DataFrame(data)
    if df.empty:
        st.info(f"No data available for {title}")
        return
    
    fig = px.pie(
        df,
        names=names_field,
        values=values_field,
        title=title
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def show_user_analytics(user_id: int = None, days: int = 30):
    """Show user analytics section"""
    st.subheader("👥 User Analytics")
    
    try:
        data = get_user_analytics(user_id=user_id, days=days)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total Activities",
                f"{data['total_activities']:,}",
                help_text="Total user activities tracked"
            )
        
        with col2:
            if data['active_users']:
                create_metric_card(
                    "Active Users",
                    f"{len(data['active_users']):,}",
                    help_text="Users with activity in the selected period"
                )
        
        with col3:
            if data['activity_types']:
                most_common = max(data['activity_types'], key=lambda x: x['count'])
                create_metric_card(
                    "Top Activity",
                    most_common['type'].replace('_', ' ').title(),
                    f"{most_common['count']} times",
                    help_text="Most common activity type"
                )
        
        with col4:
            if data['daily_activities']:
                avg_daily = sum(day['count'] for day in data['daily_activities']) / len(data['daily_activities'])
                create_metric_card(
                    "Avg Daily Activities",
                    f"{avg_daily:.1f}",
                    help_text="Average activities per day"
                )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_time_series(
                data['daily_activities'],
                'date',
                'count',
                "Daily User Activities",
                '#1f77b4'
            )
        
        with col2:
            plot_pie_chart(
                data['activity_types'],
                'type',
                'count',
                "Activity Types Distribution"
            )
        
        # Active users table (if available)
        if data['active_users'] and not user_id:
            st.subheader("Most Active Users")
            df = pd.DataFrame(data['active_users'])
            st.dataframe(
                df,
                column_config={
                    "email": "Email",
                    "name": "Name",
                    "activity_count": st.column_config.NumberColumn(
                        "Activity Count",
                        format="%d"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Recent activities
        if data['recent_activities']:
            st.subheader("Recent Activities")
            activities_df = pd.DataFrame(data['recent_activities'])
            activities_df['created_at'] = pd.to_datetime(activities_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                activities_df[['created_at', 'type', 'page']],
                column_config={
                    "created_at": "Timestamp",
                    "type": "Activity Type",
                    "page": "Page"
                },
                hide_index=True,
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error loading user analytics: {str(e)}")


def show_api_analytics(user_id: int = None, days: int = 30):
    """Show API usage analytics section"""
    st.subheader("🔌 API Usage Analytics")
    
    try:
        data = get_api_usage_analytics(user_id=user_id, days=days)
        summary = data['summary']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total API Calls",
                f"{summary['total_calls']:,}",
                help_text="Total API calls made"
            )
        
        with col2:
            create_metric_card(
                "Success Rate",
                f"{summary['success_rate']:.1f}%",
                help_text="Percentage of successful API calls"
            )
        
        with col3:
            create_metric_card(
                "Total Tokens",
                f"{summary['total_tokens']:,}",
                help_text="Total tokens processed"
            )
        
        with col4:
            create_metric_card(
                "Total Cost",
                f"${summary['total_cost']:.2f}",
                help_text="Estimated total cost"
            )
        
        # More detailed metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Avg Tokens/Call",
                f"{summary['avg_tokens_per_call']:.0f}",
                help_text="Average tokens per API call"
            )
        
        with col2:
            create_metric_card(
                "Input Tokens",
                f"{summary['input_tokens']:,}",
                help_text="Total input tokens"
            )
        
        with col3:
            create_metric_card(
                "Output Tokens",
                f"{summary['output_tokens']:,}",
                help_text="Total output tokens"
            )
        
        with col4:
            create_metric_card(
                "Avg Cost/Call",
                f"${summary['avg_cost_per_call']:.4f}",
                help_text="Average cost per API call"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_bar_chart(
                data['provider_usage'],
                'provider',
                'call_count',
                "API Calls by Provider",
                '#ff7f0e'
            )
        
        with col2:
            plot_pie_chart(
                data['provider_usage'],
                'provider',
                'total_cost',
                "Cost Distribution by Provider"
            )
        
        # Time series
        plot_time_series(
            data['daily_usage'],
            'date',
            'call_count',
            "Daily API Usage",
            '#2ca02c'
        )
        
        # Model usage table
        if data['model_usage']:
            st.subheader("Top Models by Usage")
            df = pd.DataFrame(data['model_usage'])
            st.dataframe(
                df,
                column_config={
                    "provider": "Provider",
                    "model_name": "Model",
                    "call_count": st.column_config.NumberColumn(
                        "Calls",
                        format="%d"
                    ),
                    "total_tokens": st.column_config.NumberColumn(
                        "Tokens",
                        format="%d"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Response times
        response_times = data['response_times']
        if response_times['avg_ms'] > 0:
            st.subheader("Response Time Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                create_metric_card(
                    "Avg Response Time",
                    f"{response_times['avg_ms']:.0f}ms",
                    help_text="Average API response time"
                )
            
            with col2:
                create_metric_card(
                    "Min Response Time",
                    f"{response_times['min_ms']}ms",
                    help_text="Fastest API response time"
                )
            
            with col3:
                create_metric_card(
                    "Max Response Time",
                    f"{response_times['max_ms']}ms",
                    help_text="Slowest API response time"
                )
    
    except Exception as e:
        st.error(f"Error loading API analytics: {str(e)}")


def show_system_analytics(days: int = 30):
    """Show system analytics section"""
    st.subheader("⚙️ System Analytics")
    
    try:
        data = get_system_analytics(days=days)
        
        # User metrics
        st.markdown("**User Statistics**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total Users",
                f"{data['users']['total']:,}",
                help_text="Total registered users"
            )
        
        with col2:
            create_metric_card(
                "New Users",
                f"{data['users']['new_users']:,}",
                help_text=f"New users in last {days} days"
            )
        
        with col3:
            create_metric_card(
                "Active Users",
                f"{data['users']['active_users']:,}",
                help_text=f"Users active in last {days} days"
            )
        
        with col4:
            create_metric_card(
                "Retention Rate",
                f"{data['users']['retention_rate']:.1f}%",
                help_text="Active users / total users"
            )
        
        # Task metrics
        st.markdown("**Research Task Statistics**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total Tasks",
                f"{data['research_tasks']['total']:,}",
                help_text=f"Research tasks in last {days} days"
            )
        
        with col2:
            create_metric_card(
                "Completed Tasks",
                f"{data['research_tasks']['completed']:,}",
                help_text="Successfully completed tasks"
            )
        
        with col3:
            create_metric_card(
                "Failed Tasks",
                f"{data['research_tasks']['failed']:,}",
                help_text="Failed or errored tasks"
            )
        
        with col4:
            create_metric_card(
                "Success Rate",
                f"{data['research_tasks']['success_rate']:.1f}%",
                help_text="Task completion success rate"
            )
        
        # Performance metrics
        if data['research_tasks']['avg_processing_time_seconds'] > 0:
            st.markdown("**Performance**")
            create_metric_card(
                "Avg Processing Time",
                f"{data['research_tasks']['avg_processing_time_seconds']:.1f}s",
                help_text="Average task processing time"
            )
        
        # System metrics (if available)
        if data['system_metrics']:
            st.subheader("System Metrics")
            df = pd.DataFrame(data['system_metrics'])
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                df,
                column_config={
                    "created_at": "Timestamp",
                    "type": "Metric Type",
                    "name": "Metric Name",
                    "value": st.column_config.NumberColumn(
                        "Value",
                        format="%.2f"
                    ),
                    "unit": "Unit"
                },
                hide_index=True,
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error loading system analytics: {str(e)}")


def show_error_analytics(days: int = 30):
    """Show error analytics section"""
    st.subheader("🚨 Error Analytics")
    
    try:
        data = get_error_analytics(days=days)
        
        # Summary metrics
        col1, col2 = st.columns(2)
        
        with col1:
            create_metric_card(
                "Total Errors",
                f"{data['summary']['total_errors']:,}",
                help_text=f"Total errors in last {days} days"
            )
        
        with col2:
            create_metric_card(
                "Unresolved Errors",
                f"{data['summary']['unresolved_count']:,}",
                help_text="Errors that need attention"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            plot_pie_chart(
                data['by_severity'],
                'severity',
                'count',
                "Errors by Severity"
            )
        
        with col2:
            plot_bar_chart(
                data['by_type'][:10],  # Top 10 error types
                'type',
                'count',
                "Top Error Types",
                '#d62728'
            )
        
        # Daily error trends
        plot_time_series(
            data['daily_errors'],
            'date',
            'count',
            "Daily Error Count",
            '#d62728'
        )
        
        # Unresolved errors table
        if data['unresolved_errors']:
            st.subheader("Unresolved Errors")
            df = pd.DataFrame(data['unresolved_errors'])
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                df[['created_at', 'severity', 'type', 'message']],
                column_config={
                    "created_at": "Timestamp",
                    "severity": "Severity",
                    "type": "Error Type",
                    "message": "Error Message"
                },
                hide_index=True,
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error loading error analytics: {str(e)}")


def show_performance_analytics(days: int = 30):
    """Show performance analytics section"""
    st.subheader("⚡ Performance Analytics")
    
    try:
        data = get_performance_analytics(days=days)
        summary = data['summary']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Avg Load Time",
                f"{summary['avg_load_time_ms']:.0f}ms",
                help_text="Average page load time"
            )
        
        with col2:
            create_metric_card(
                "Min Load Time",
                f"{summary['min_load_time_ms']}ms",
                help_text="Fastest page load time"
            )
        
        with col3:
            create_metric_card(
                "Max Load Time",
                f"{summary['max_load_time_ms']}ms",
                help_text="Slowest page load time"
            )
        
        with col4:
            create_metric_card(
                "Avg Memory Usage",
                f"{summary['avg_memory_mb']:.1f}MB",
                help_text="Average memory usage"
            )
        
        # Performance by page
        if data['by_page']:
            st.subheader("Performance by Page")
            df = pd.DataFrame(data['by_page'])
            
            fig = px.bar(
                df,
                x='page',
                y='avg_load_time_ms',
                title="Average Load Time by Page",
                color='avg_load_time_ms',
                color_continuous_scale='RdYlBu_r'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Table view
            st.dataframe(
                df,
                column_config={
                    "page": "Page",
                    "avg_load_time_ms": st.column_config.NumberColumn(
                        "Avg Load Time (ms)",
                        format="%.0f"
                    ),
                    "sample_count": st.column_config.NumberColumn(
                        "Samples",
                        format="%d"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Daily trends
        if data['daily_trends']:
            st.subheader("Performance Trends")
            
            df = pd.DataFrame(data['daily_trends'])
            df['date'] = pd.to_datetime(df['date'])
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Load Time', 'Memory Usage', 'CPU Usage', ''),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"type": "table"}]]
            )
            
            # Load time trend
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['avg_load_time_ms'],
                    mode='lines+markers',
                    name='Load Time (ms)',
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
            
            # Memory usage trend
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['avg_memory_mb'],
                    mode='lines+markers',
                    name='Memory (MB)',
                    line=dict(color='green')
                ),
                row=1, col=2
            )
            
            # CPU usage trend
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['avg_cpu_percent'],
                    mode='lines+markers',
                    name='CPU (%)',
                    line=dict(color='red')
                ),
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading performance analytics: {str(e)}")


def main():
    """Main analytics dashboard"""
    init_page()
    
    # Track page performance
    start_time = time.time()
    
    # Authentication check
    user = require_auth()
    if not user:
        st.warning("Please log in to access analytics.")
        st.stop()
    
    # Check if user has analytics access (admin or super admin)
    if not (user.is_admin or user.is_super_admin):
        st.error("Access denied. Analytics dashboard is only available to administrators.")
        st.stop()
    
    # Track user activity
    track_user_activity(
        activity_type='analytics_dashboard_view',
        page='analytics',
        user_id=user.id
    )
    
    st.title("📊 Analytics Dashboard")
    st.markdown("---")
    
    # Time range selector
    st.sidebar.subheader("Analytics Settings")
    
    days = st.sidebar.selectbox(
        "Time Range",
        options=[7, 14, 30, 60, 90],
        index=2,  # Default to 30 days
        help="Select the number of days to analyze"
    )
    
    # User filter (for super admins)
    user_filter = None
    if user.is_super_admin:
        if st.sidebar.checkbox("Filter by specific user"):
            user_email = st.sidebar.text_input("User email")
            if user_email:
                # TODO: Look up user by email
                pass
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.success("Data refreshed!")
        st.rerun()
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto-refresh every 30 seconds")
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Users", "🔌 API Usage", "⚙️ System", "🚨 Errors", "⚡ Performance"
    ])
    
    with tab1:
        show_user_analytics(user_id=user_filter, days=days)
    
    with tab2:
        show_api_analytics(user_id=user_filter, days=days)
    
    with tab3:
        show_system_analytics(days=days)
    
    with tab4:
        show_error_analytics(days=days)
    
    with tab5:
        show_performance_analytics(days=days)
    
    # Footer with last updated
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data range: Last {days} days")
    
    # Track page performance
    load_time_ms = int((time.time() - start_time) * 1000)
    track_page_performance(
        page='analytics',
        load_time_ms=load_time_ms,
        user_id=user.id
    )


if __name__ == "__main__":
    main()