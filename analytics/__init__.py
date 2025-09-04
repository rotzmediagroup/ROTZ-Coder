"""
Analytics module for tracking user behavior and system performance
"""

from .collectors import (
    AnalyticsCollector,
    track_user_activity,
    track_api_usage,
    track_system_metrics,
    track_error,
    track_performance
)

from .dashboard import (
    get_user_analytics,
    get_system_analytics,
    get_api_usage_analytics,
    get_performance_analytics,
    get_error_analytics
)

__all__ = [
    'AnalyticsCollector',
    'track_user_activity',
    'track_api_usage',
    'track_system_metrics',
    'track_error',
    'track_performance',
    'get_user_analytics',
    'get_system_analytics',
    'get_api_usage_analytics',
    'get_performance_analytics',
    'get_error_analytics'
]