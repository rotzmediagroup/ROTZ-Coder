"""
Data collection utilities for analytics
"""

import time
import traceback
import psutil
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

from database.models import (
    UserActivity, ApiUsageLog, SystemMetrics, ErrorLog, PerformanceMetrics
)
from utils.database import get_db_session


class AnalyticsCollector:
    """Main analytics collection class"""
    
    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """Get current session information from Streamlit"""
        try:
            # Initialize session info with default values
            session_info = {
                'user_id': None,
                'session_id': None,
                'user_email': None,
                'ip_address': 'unknown',
                'user_agent': 'Streamlit-App'
            }
            
            if hasattr(st, 'session_state') and st.session_state:
                session_info.update({
                    'user_id': getattr(st.session_state, 'user_id', None),
                    'session_id': getattr(st.session_state, 'session_id', None),
                    'user_email': getattr(st.session_state, 'user_email', None)
                })
            
            # Try to get request info if available
            try:
                if hasattr(st, 'get_option') and st.get_option('server.headless') is False:
                    # In development/local mode, we might not have full request info
                    session_info.update({
                        'ip_address': '127.0.0.1',  # Default for local development
                        'user_agent': 'Streamlit-Local'
                    })
            except Exception:
                # Fallback for production or when request info is not available
                session_info.update({
                    'ip_address': 'unknown',
                    'user_agent': 'Streamlit-App'
                })
            
            return session_info
        except Exception:
            # Fallback if session state is not available
            return {
                'user_id': None,
                'session_id': None,
                'user_email': None,
                'ip_address': 'unknown',
                'user_agent': 'Streamlit-App'
            }


def track_user_activity(
    activity_type: str,
    page: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None
) -> bool:
    """
    Track user activity
    
    Args:
        activity_type: Type of activity (login, logout, research_task, etc.)
        page: Page where activity occurred
        details: Additional details as dict
        user_id: User ID (will try to get from session if not provided)
    
    Returns:
        bool: Success status
    """
    try:
        session_info = AnalyticsCollector.get_session_info()
        
        # Use provided user_id or get from session
        if user_id is None:
            user_id = session_info.get('user_id')
        
        # Skip tracking if no user_id (anonymous activity)
        if user_id is None:
            return False
        
        with get_db_session() as session:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                page=page,
                details=details,
                ip_address=session_info.get('ip_address'),
                user_agent=session_info.get('user_agent'),
                session_id=session_info.get('session_id')
            )
            session.add(activity)
            session.commit()
            return True
    
    except Exception as e:
        # Log error but don't break the application
        track_error('analytics_tracking_error', str(e), severity='warning')
        return False


def track_api_usage(
    provider: str,
    model_name: str,
    task_type: Optional[str] = None,
    request_type: str = 'completion',
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    response_time_ms: Optional[int] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    cost_estimate: Optional[float] = None,
    user_id: Optional[int] = None
) -> bool:
    """
    Track API usage
    
    Args:
        provider: LLM provider (openai, anthropic, etc.)
        model_name: Model used
        task_type: Type of task
        request_type: Type of API request
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        response_time_ms: Response time in milliseconds
        success: Whether the request was successful
        error_message: Error message if failed
        cost_estimate: Estimated cost in USD
        user_id: User ID (will try to get from session if not provided)
    
    Returns:
        bool: Success status
    """
    try:
        session_info = AnalyticsCollector.get_session_info()
        
        # Use provided user_id or get from session
        if user_id is None:
            user_id = session_info.get('user_id')
        
        # Skip tracking if no user_id
        if user_id is None:
            return False
        
        total_tokens = 0
        if input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens
        elif input_tokens is not None:
            total_tokens = input_tokens
        elif output_tokens is not None:
            total_tokens = output_tokens
        
        with get_db_session() as session:
            usage_log = ApiUsageLog(
                user_id=user_id,
                provider=provider,
                model_name=model_name,
                task_type=task_type,
                request_type=request_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time_ms,
                success=success,
                error_message=error_message,
                cost_estimate=cost_estimate
            )
            session.add(usage_log)
            session.commit()
            return True
    
    except Exception as e:
        # Log error but don't break the application
        track_error('api_usage_tracking_error', str(e), severity='warning')
        return False


def track_system_metrics(
    metric_type: str,
    metric_name: str,
    value: float,
    unit: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Track system metrics
    
    Args:
        metric_type: Type of metric (cpu_usage, memory_usage, etc.)
        metric_name: Specific metric name
        value: Metric value
        unit: Unit of measurement
        tags: Additional metadata
    
    Returns:
        bool: Success status
    """
    try:
        with get_db_session() as session:
            metric = SystemMetrics(
                metric_type=metric_type,
                metric_name=metric_name,
                value=value,
                unit=unit,
                tags=tags
            )
            session.add(metric)
            session.commit()
            return True
    
    except Exception as e:
        # Log error but don't break the application
        print(f"Error tracking system metrics: {e}")
        return False


def track_error(
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    request_path: Optional[str] = None,
    request_method: Optional[str] = None,
    severity: str = 'error',
    user_id: Optional[int] = None
) -> bool:
    """
    Track application errors
    
    Args:
        error_type: Type of error
        error_message: Error message
        stack_trace: Stack trace if available
        request_path: Request path where error occurred
        request_method: HTTP method
        severity: Error severity (debug, info, warning, error, critical)
        user_id: User ID if applicable
    
    Returns:
        bool: Success status
    """
    try:
        session_info = AnalyticsCollector.get_session_info()
        
        # Use provided user_id or get from session
        if user_id is None:
            user_id = session_info.get('user_id')
        
        # Get stack trace if not provided
        if stack_trace is None:
            stack_trace = traceback.format_exc()
        
        with get_db_session() as session:
            error_log = ErrorLog(
                user_id=user_id,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                request_path=request_path,
                request_method=request_method,
                user_agent=session_info.get('user_agent'),
                ip_address=session_info.get('ip_address'),
                severity=severity
            )
            session.add(error_log)
            session.commit()
            return True
    
    except Exception as e:
        # Fallback logging to prevent infinite loops
        print(f"Error tracking error log: {e}")
        return False


def track_performance(
    page: str,
    load_time_ms: int,
    memory_usage_mb: Optional[float] = None,
    cpu_usage_percent: Optional[float] = None,
    database_queries: Optional[int] = None,
    database_time_ms: Optional[int] = None,
    user_id: Optional[int] = None
) -> bool:
    """
    Track page performance metrics
    
    Args:
        page: Page name
        load_time_ms: Load time in milliseconds
        memory_usage_mb: Memory usage in MB
        cpu_usage_percent: CPU usage percentage
        database_queries: Number of database queries
        database_time_ms: Total database query time
        user_id: User ID if applicable
    
    Returns:
        bool: Success status
    """
    try:
        session_info = AnalyticsCollector.get_session_info()
        
        # Use provided user_id or get from session
        if user_id is None:
            user_id = session_info.get('user_id')
        
        # Get system metrics if not provided
        if memory_usage_mb is None or cpu_usage_percent is None:
            try:
                process = psutil.Process()
                if memory_usage_mb is None:
                    memory_usage_mb = process.memory_info().rss / (1024 * 1024)  # Convert to MB
                if cpu_usage_percent is None:
                    cpu_usage_percent = process.cpu_percent()
            except Exception:
                # Fallback values if psutil fails
                memory_usage_mb = memory_usage_mb or 0.0
                cpu_usage_percent = cpu_usage_percent or 0.0
        
        with get_db_session() as session:
            performance_metric = PerformanceMetrics(
                user_id=user_id,
                page=page,
                load_time_ms=load_time_ms,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                database_queries=database_queries,
                database_time_ms=database_time_ms,
                user_agent=session_info.get('user_agent')
            )
            session.add(performance_metric)
            session.commit()
            return True
    
    except Exception as e:
        # Log error but don't break the application
        track_error('performance_tracking_error', str(e), severity='warning')
        return False


@contextmanager
def track_api_call(provider: str, model_name: str, task_type: Optional[str] = None):
    """
    Context manager for tracking API calls with automatic timing
    
    Usage:
        with track_api_call('openai', 'gpt-4', 'code_generation') as tracker:
            result = api_call()
            tracker.set_tokens(input_tokens=100, output_tokens=200)
            tracker.set_cost(0.05)
    """
    class APICallTracker:
        def __init__(self, provider: str, model_name: str, task_type: Optional[str]):
            self.provider = provider
            self.model_name = model_name
            self.task_type = task_type
            self.start_time = time.time()
            self.input_tokens = None
            self.output_tokens = None
            self.cost_estimate = None
            self.success = True
            self.error_message = None
        
        def set_tokens(self, input_tokens: Optional[int] = None, output_tokens: Optional[int] = None):
            """Set token counts"""
            self.input_tokens = input_tokens
            self.output_tokens = output_tokens
        
        def set_cost(self, cost: float):
            """Set cost estimate"""
            self.cost_estimate = cost
        
        def set_error(self, error_message: str):
            """Mark call as failed with error message"""
            self.success = False
            self.error_message = error_message
    
    tracker = APICallTracker(provider, model_name, task_type)
    
    try:
        yield tracker
    except Exception as e:
        tracker.set_error(str(e))
        raise
    finally:
        # Calculate response time
        response_time_ms = int((time.time() - tracker.start_time) * 1000)
        
        # Track the API usage
        track_api_usage(
            provider=tracker.provider,
            model_name=tracker.model_name,
            task_type=tracker.task_type,
            input_tokens=tracker.input_tokens,
            output_tokens=tracker.output_tokens,
            response_time_ms=response_time_ms,
            success=tracker.success,
            error_message=tracker.error_message,
            cost_estimate=tracker.cost_estimate
        )


@contextmanager
def track_page_performance(page: str):
    """
    Context manager for tracking page performance
    
    Usage:
        with track_page_performance('home') as tracker:
            # Page loading logic
            tracker.add_database_query()  # Call for each DB query
    """
    class PagePerformanceTracker:
        def __init__(self, page: str):
            self.page = page
            self.start_time = time.time()
            self.database_queries = 0
            self.database_start_time = None
            self.database_total_time = 0
        
        def add_database_query(self):
            """Track a database query"""
            self.database_queries += 1
        
        @contextmanager
        def track_database_query(self):
            """Context manager for tracking individual database queries"""
            start_time = time.time()
            try:
                yield
            finally:
                query_time = (time.time() - start_time) * 1000  # Convert to ms
                self.database_total_time += query_time
                self.database_queries += 1
    
    tracker = PagePerformanceTracker(page)
    
    try:
        yield tracker
    finally:
        # Calculate load time
        load_time_ms = int((time.time() - tracker.start_time) * 1000)
        
        # Track the performance
        track_performance(
            page=tracker.page,
            load_time_ms=load_time_ms,
            database_queries=tracker.database_queries,
            database_time_ms=int(tracker.database_total_time) if tracker.database_total_time > 0 else None
        )