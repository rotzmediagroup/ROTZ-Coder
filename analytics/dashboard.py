"""
Analytics dashboard data functions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session

from database.models import (
    User, UserActivity, ApiUsageLog, SystemMetrics, 
    ErrorLog, PerformanceMetrics, ResearchTask
)
from utils.database import get_db_session


def get_date_range_filter(days: int = 30) -> datetime:
    """Get datetime filter for the last N days"""
    return datetime.utcnow() - timedelta(days=days)


def get_user_analytics(user_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
    """
    Get user analytics data
    
    Args:
        user_id: Specific user ID (None for all users)
        days: Number of days to look back
    
    Returns:
        Dict with user analytics data
    """
    with get_db_session() as session:
        date_filter = get_date_range_filter(days)
        
        # Base query
        query = session.query(UserActivity).filter(UserActivity.created_at >= date_filter)
        if user_id:
            query = query.filter(UserActivity.user_id == user_id)
        
        # Total activities
        total_activities = query.count()
        
        # Activities by type
        activity_types = session.query(
            UserActivity.activity_type,
            func.count(UserActivity.id).label('count')
        ).filter(UserActivity.created_at >= date_filter)
        
        if user_id:
            activity_types = activity_types.filter(UserActivity.user_id == user_id)
        
        activity_types = activity_types.group_by(UserActivity.activity_type).all()
        
        # Activities by day
        daily_activities = session.query(
            func.date(UserActivity.created_at).label('date'),
            func.count(UserActivity.id).label('count')
        ).filter(UserActivity.created_at >= date_filter)
        
        if user_id:
            daily_activities = daily_activities.filter(UserActivity.user_id == user_id)
        
        daily_activities = daily_activities.group_by(
            func.date(UserActivity.created_at)
        ).order_by(func.date(UserActivity.created_at)).all()
        
        # Most active users (if not filtering by specific user)
        active_users = []
        if not user_id:
            active_users = session.query(
                User.email,
                User.full_name,
                func.count(UserActivity.id).label('activity_count')
            ).join(UserActivity).filter(
                UserActivity.created_at >= date_filter
            ).group_by(User.id).order_by(
                desc('activity_count')
            ).limit(10).all()
        
        # Recent activities
        recent_activities = query.order_by(
            desc(UserActivity.created_at)
        ).limit(20).all()
        
        return {
            'total_activities': total_activities,
            'activity_types': [
                {'type': item[0], 'count': item[1]} 
                for item in activity_types
            ],
            'daily_activities': [
                {'date': item[0].isoformat() if item[0] else None, 'count': item[1]}
                for item in daily_activities
            ],
            'active_users': [
                {
                    'email': item[0],
                    'name': item[1] or 'Unknown',
                    'activity_count': item[2]
                }
                for item in active_users
            ],
            'recent_activities': [
                {
                    'id': activity.id,
                    'type': activity.activity_type,
                    'page': activity.page,
                    'created_at': activity.created_at.isoformat(),
                    'details': activity.details
                }
                for activity in recent_activities
            ],
            'date_range_days': days
        }


def get_api_usage_analytics(user_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
    """
    Get API usage analytics
    
    Args:
        user_id: Specific user ID (None for all users)
        days: Number of days to look back
    
    Returns:
        Dict with API usage analytics
    """
    with get_db_session() as session:
        date_filter = get_date_range_filter(days)
        
        # Base query
        query = session.query(ApiUsageLog).filter(ApiUsageLog.created_at >= date_filter)
        if user_id:
            query = query.filter(ApiUsageLog.user_id == user_id)
        
        # Total API calls
        total_calls = query.count()
        successful_calls = query.filter(ApiUsageLog.success == True).count()
        failed_calls = total_calls - successful_calls
        
        # Token usage
        token_stats = session.query(
            func.sum(ApiUsageLog.total_tokens).label('total_tokens'),
            func.avg(ApiUsageLog.total_tokens).label('avg_tokens'),
            func.sum(ApiUsageLog.input_tokens).label('input_tokens'),
            func.sum(ApiUsageLog.output_tokens).label('output_tokens')
        ).filter(ApiUsageLog.created_at >= date_filter)
        
        if user_id:
            token_stats = token_stats.filter(ApiUsageLog.user_id == user_id)
        
        token_stats = token_stats.first()
        
        # Cost analysis
        cost_stats = session.query(
            func.sum(ApiUsageLog.cost_estimate).label('total_cost'),
            func.avg(ApiUsageLog.cost_estimate).label('avg_cost')
        ).filter(
            and_(
                ApiUsageLog.created_at >= date_filter,
                ApiUsageLog.cost_estimate.isnot(None)
            )
        )
        
        if user_id:
            cost_stats = cost_stats.filter(ApiUsageLog.user_id == user_id)
        
        cost_stats = cost_stats.first()
        
        # Usage by provider
        provider_usage = session.query(
            ApiUsageLog.provider,
            func.count(ApiUsageLog.id).label('call_count'),
            func.sum(ApiUsageLog.total_tokens).label('total_tokens'),
            func.sum(ApiUsageLog.cost_estimate).label('total_cost')
        ).filter(ApiUsageLog.created_at >= date_filter)
        
        if user_id:
            provider_usage = provider_usage.filter(ApiUsageLog.user_id == user_id)
        
        provider_usage = provider_usage.group_by(ApiUsageLog.provider).all()
        
        # Usage by model
        model_usage = session.query(
            ApiUsageLog.provider,
            ApiUsageLog.model_name,
            func.count(ApiUsageLog.id).label('call_count'),
            func.sum(ApiUsageLog.total_tokens).label('total_tokens')
        ).filter(ApiUsageLog.created_at >= date_filter)
        
        if user_id:
            model_usage = model_usage.filter(ApiUsageLog.user_id == user_id)
        
        model_usage = model_usage.group_by(
            ApiUsageLog.provider, ApiUsageLog.model_name
        ).order_by(desc('call_count')).limit(10).all()
        
        # Daily usage
        daily_usage = session.query(
            func.date(ApiUsageLog.created_at).label('date'),
            func.count(ApiUsageLog.id).label('call_count'),
            func.sum(ApiUsageLog.total_tokens).label('total_tokens'),
            func.sum(ApiUsageLog.cost_estimate).label('total_cost')
        ).filter(ApiUsageLog.created_at >= date_filter)
        
        if user_id:
            daily_usage = daily_usage.filter(ApiUsageLog.user_id == user_id)
        
        daily_usage = daily_usage.group_by(
            func.date(ApiUsageLog.created_at)
        ).order_by(func.date(ApiUsageLog.created_at)).all()
        
        # Response time analysis
        response_time_stats = session.query(
            func.avg(ApiUsageLog.response_time_ms).label('avg_response_time'),
            func.min(ApiUsageLog.response_time_ms).label('min_response_time'),
            func.max(ApiUsageLog.response_time_ms).label('max_response_time')
        ).filter(
            and_(
                ApiUsageLog.created_at >= date_filter,
                ApiUsageLog.response_time_ms.isnot(None)
            )
        )
        
        if user_id:
            response_time_stats = response_time_stats.filter(ApiUsageLog.user_id == user_id)
        
        response_time_stats = response_time_stats.first()
        
        return {
            'summary': {
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'failed_calls': failed_calls,
                'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 0,
                'total_tokens': int(token_stats[0]) if token_stats[0] else 0,
                'avg_tokens_per_call': float(token_stats[1]) if token_stats[1] else 0,
                'input_tokens': int(token_stats[2]) if token_stats[2] else 0,
                'output_tokens': int(token_stats[3]) if token_stats[3] else 0,
                'total_cost': float(cost_stats[0]) if cost_stats[0] else 0,
                'avg_cost_per_call': float(cost_stats[1]) if cost_stats[1] else 0
            },
            'provider_usage': [
                {
                    'provider': item[0],
                    'call_count': item[1],
                    'total_tokens': int(item[2]) if item[2] else 0,
                    'total_cost': float(item[3]) if item[3] else 0
                }
                for item in provider_usage
            ],
            'model_usage': [
                {
                    'provider': item[0],
                    'model_name': item[1],
                    'call_count': item[2],
                    'total_tokens': int(item[3]) if item[3] else 0
                }
                for item in model_usage
            ],
            'daily_usage': [
                {
                    'date': item[0].isoformat() if item[0] else None,
                    'call_count': item[1],
                    'total_tokens': int(item[2]) if item[2] else 0,
                    'total_cost': float(item[3]) if item[3] else 0
                }
                for item in daily_usage
            ],
            'response_times': {
                'avg_ms': float(response_time_stats[0]) if response_time_stats[0] else 0,
                'min_ms': int(response_time_stats[1]) if response_time_stats[1] else 0,
                'max_ms': int(response_time_stats[2]) if response_time_stats[2] else 0
            },
            'date_range_days': days
        }


def get_system_analytics(days: int = 30) -> Dict[str, Any]:
    """
    Get system-wide analytics
    
    Args:
        days: Number of days to look back
    
    Returns:
        Dict with system analytics
    """
    with get_db_session() as session:
        date_filter = get_date_range_filter(days)
        
        # User statistics
        total_users = session.query(User).count()
        new_users = session.query(User).filter(User.created_at >= date_filter).count()
        active_users = session.query(User).join(UserActivity).filter(
            UserActivity.created_at >= date_filter
        ).distinct().count()
        
        # Research task statistics
        total_tasks = session.query(ResearchTask).filter(
            ResearchTask.created_at >= date_filter
        ).count()
        
        completed_tasks = session.query(ResearchTask).filter(
            and_(
                ResearchTask.created_at >= date_filter,
                ResearchTask.status == 'completed'
            )
        ).count()
        
        failed_tasks = session.query(ResearchTask).filter(
            and_(
                ResearchTask.created_at >= date_filter,
                ResearchTask.status == 'failed'
            )
        ).count()
        
        # Average processing time for completed tasks
        avg_processing_time = session.query(
            func.avg(ResearchTask.processing_time)
        ).filter(
            and_(
                ResearchTask.created_at >= date_filter,
                ResearchTask.processing_time.isnot(None),
                ResearchTask.status == 'completed'
            )
        ).scalar()
        
        # System metrics (if any)
        latest_metrics = session.query(SystemMetrics).filter(
            SystemMetrics.created_at >= date_filter
        ).order_by(desc(SystemMetrics.created_at)).limit(100).all()
        
        return {
            'users': {
                'total': total_users,
                'new_users': new_users,
                'active_users': active_users,
                'retention_rate': (active_users / total_users * 100) if total_users > 0 else 0
            },
            'research_tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'failed': failed_tasks,
                'success_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                'avg_processing_time_seconds': float(avg_processing_time) if avg_processing_time else 0
            },
            'system_metrics': [
                {
                    'type': metric.metric_type,
                    'name': metric.metric_name,
                    'value': metric.value,
                    'unit': metric.unit,
                    'created_at': metric.created_at.isoformat()
                }
                for metric in latest_metrics
            ],
            'date_range_days': days
        }


def get_error_analytics(days: int = 30) -> Dict[str, Any]:
    """
    Get error analytics
    
    Args:
        days: Number of days to look back
    
    Returns:
        Dict with error analytics
    """
    with get_db_session() as session:
        date_filter = get_date_range_filter(days)
        
        # Total errors
        total_errors = session.query(ErrorLog).filter(
            ErrorLog.created_at >= date_filter
        ).count()
        
        # Errors by severity
        error_by_severity = session.query(
            ErrorLog.severity,
            func.count(ErrorLog.id).label('count')
        ).filter(ErrorLog.created_at >= date_filter).group_by(
            ErrorLog.severity
        ).all()
        
        # Errors by type
        error_by_type = session.query(
            ErrorLog.error_type,
            func.count(ErrorLog.id).label('count')
        ).filter(ErrorLog.created_at >= date_filter).group_by(
            ErrorLog.error_type
        ).order_by(desc('count')).limit(10).all()
        
        # Daily error count
        daily_errors = session.query(
            func.date(ErrorLog.created_at).label('date'),
            func.count(ErrorLog.id).label('count'),
            func.count(func.nullif(ErrorLog.severity == 'critical', False)).label('critical_count')
        ).filter(ErrorLog.created_at >= date_filter).group_by(
            func.date(ErrorLog.created_at)
        ).order_by(func.date(ErrorLog.created_at)).all()
        
        # Unresolved errors
        unresolved_errors = session.query(ErrorLog).filter(
            and_(
                ErrorLog.created_at >= date_filter,
                ErrorLog.resolved == False
            )
        ).order_by(desc(ErrorLog.created_at)).limit(20).all()
        
        return {
            'summary': {
                'total_errors': total_errors,
                'unresolved_count': len(unresolved_errors)
            },
            'by_severity': [
                {'severity': item[0], 'count': item[1]}
                for item in error_by_severity
            ],
            'by_type': [
                {'type': item[0], 'count': item[1]}
                for item in error_by_type
            ],
            'daily_errors': [
                {
                    'date': item[0].isoformat() if item[0] else None,
                    'count': item[1],
                    'critical_count': item[2] if item[2] else 0
                }
                for item in daily_errors
            ],
            'unresolved_errors': [
                {
                    'id': error.id,
                    'type': error.error_type,
                    'message': error.error_message,
                    'severity': error.severity,
                    'created_at': error.created_at.isoformat()
                }
                for error in unresolved_errors
            ],
            'date_range_days': days
        }


def get_performance_analytics(days: int = 30) -> Dict[str, Any]:
    """
    Get performance analytics
    
    Args:
        days: Number of days to look back
    
    Returns:
        Dict with performance analytics
    """
    with get_db_session() as session:
        date_filter = get_date_range_filter(days)
        
        # Average performance metrics
        performance_stats = session.query(
            func.avg(PerformanceMetrics.load_time_ms).label('avg_load_time'),
            func.min(PerformanceMetrics.load_time_ms).label('min_load_time'),
            func.max(PerformanceMetrics.load_time_ms).label('max_load_time'),
            func.avg(PerformanceMetrics.memory_usage_mb).label('avg_memory'),
            func.avg(PerformanceMetrics.cpu_usage_percent).label('avg_cpu')
        ).filter(PerformanceMetrics.created_at >= date_filter).first()
        
        # Performance by page
        page_performance = session.query(
            PerformanceMetrics.page,
            func.avg(PerformanceMetrics.load_time_ms).label('avg_load_time'),
            func.count(PerformanceMetrics.id).label('sample_count')
        ).filter(PerformanceMetrics.created_at >= date_filter).group_by(
            PerformanceMetrics.page
        ).order_by(desc('avg_load_time')).all()
        
        # Daily performance trends
        daily_performance = session.query(
            func.date(PerformanceMetrics.created_at).label('date'),
            func.avg(PerformanceMetrics.load_time_ms).label('avg_load_time'),
            func.avg(PerformanceMetrics.memory_usage_mb).label('avg_memory'),
            func.avg(PerformanceMetrics.cpu_usage_percent).label('avg_cpu')
        ).filter(PerformanceMetrics.created_at >= date_filter).group_by(
            func.date(PerformanceMetrics.created_at)
        ).order_by(func.date(PerformanceMetrics.created_at)).all()
        
        return {
            'summary': {
                'avg_load_time_ms': float(performance_stats[0]) if performance_stats[0] else 0,
                'min_load_time_ms': int(performance_stats[1]) if performance_stats[1] else 0,
                'max_load_time_ms': int(performance_stats[2]) if performance_stats[2] else 0,
                'avg_memory_mb': float(performance_stats[3]) if performance_stats[3] else 0,
                'avg_cpu_percent': float(performance_stats[4]) if performance_stats[4] else 0
            },
            'by_page': [
                {
                    'page': item[0],
                    'avg_load_time_ms': float(item[1]) if item[1] else 0,
                    'sample_count': item[2]
                }
                for item in page_performance
            ],
            'daily_trends': [
                {
                    'date': item[0].isoformat() if item[0] else None,
                    'avg_load_time_ms': float(item[1]) if item[1] else 0,
                    'avg_memory_mb': float(item[2]) if item[2] else 0,
                    'avg_cpu_percent': float(item[3]) if item[3] else 0
                }
                for item in daily_performance
            ],
            'date_range_days': days
        }


def get_comprehensive_dashboard_data(days: int = 30) -> Dict[str, Any]:
    """
    Get all analytics data for comprehensive dashboard
    
    Args:
        days: Number of days to look back
    
    Returns:
        Dict with all analytics data
    """
    return {
        'user_analytics': get_user_analytics(days=days),
        'api_usage': get_api_usage_analytics(days=days),
        'system_analytics': get_system_analytics(days=days),
        'error_analytics': get_error_analytics(days=days),
        'performance_analytics': get_performance_analytics(days=days),
        'generated_at': datetime.utcnow().isoformat()
    }