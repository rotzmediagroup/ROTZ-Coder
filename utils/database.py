"""
Database utility functions for DeepCode
"""

import os
import streamlit as st
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Generator


@st.cache_resource
def get_database_url() -> str:
    """
    Get the database URL from configuration
    
    Returns:
        Database URL string
    """
    # Check Streamlit secrets first
    if hasattr(st, 'secrets') and 'database_url' in st.secrets:
        return st.secrets['database_url']
    
    # Check environment variable
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Handle Heroku postgres:// to postgresql:// conversion
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    
    # Default to SQLite for development
    return 'sqlite:///deepcode.db'


@st.cache_resource
def init_database_engine():
    """
    Initialize the database engine (cached)
    
    Returns:
        SQLAlchemy engine and session factory
    """
    database_url = get_database_url()
    
    # Create engine with appropriate settings
    if database_url.startswith('sqlite'):
        engine = create_engine(
            database_url,
            connect_args={'check_same_thread': False},
            echo=False
        )
    else:
        engine = create_engine(
            database_url,
            pool_size=10,
            pool_recycle=3600,
            echo=False
        )
    
    # Create session factory
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    
    # Create all tables
    from database.models import Base
    Base.metadata.create_all(engine)
    
    return engine, Session


@contextmanager
def get_db_session() -> Generator:
    """
    Context manager for database sessions
    
    Usage:
        with get_db_session() as session:
            # Use session here
            pass
    """
    _, Session = init_database_engine()
    session = Session()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def init_database_tables():
    """
    Initialize all database tables and default data
    """
    from database.models import init_super_admin, init_default_llm_configs, User
    
    engine, Session = init_database_engine()
    
    with get_db_session() as session:
        # Initialize super admin
        init_super_admin(session)
        
        # Get super admin for creating default configs
        super_admin = session.query(User).filter_by(email="jerome@rotz.host").first()
        if super_admin:
            init_default_llm_configs(session, super_admin.id)
    
    print("✅ Database tables initialized")


def get_user_by_email(email: str):
    """
    Get a user by email address
    
    Args:
        email: User's email
        
    Returns:
        User object or None
    """
    from database.models import User
    
    with get_db_session() as session:
        return session.query(User).filter_by(email=email).first()


def get_user_by_id(user_id: int):
    """
    Get a user by ID
    
    Args:
        user_id: User's ID
        
    Returns:
        User object or None
    """
    from database.models import User
    
    with get_db_session() as session:
        return session.query(User).filter_by(id=user_id).first()


def get_all_users():
    """
    Get all users (for admin panel)
    
    Returns:
        List of all users
    """
    from database.models import User
    
    with get_db_session() as session:
        return session.query(User).all()


def update_user_admin_status(user_id: int, is_admin: bool) -> bool:
    """
    Update a user's admin status
    
    Args:
        user_id: User's ID
        is_admin: New admin status
        
    Returns:
        True if updated successfully, False otherwise
    """
    from database.models import User
    
    try:
        with get_db_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user and user.email != "jerome@rotz.host":  # Can't change super admin
                user.is_admin = is_admin
                session.commit()
                return True
            return False
    except Exception as e:
        print(f"Error updating user admin status: {e}")
        return False


def get_llm_configurations(task_type: str = None):
    """
    Get LLM configurations, optionally filtered by task type
    
    Args:
        task_type: Optional task type to filter by
        
    Returns:
        List of LLM configurations
    """
    from database.models import LLMConfiguration
    
    with get_db_session() as session:
        query = session.query(LLMConfiguration).filter_by(is_active=True)
        
        if task_type:
            query = query.filter_by(task_type=task_type)
        
        return query.order_by(LLMConfiguration.priority).all()


def save_llm_configuration(provider: str, model_name: str, task_type: str, 
                          priority: int, parameters: dict, created_by: int) -> bool:
    """
    Save or update an LLM configuration
    
    Args:
        provider: Provider name
        model_name: Model name
        task_type: Task type
        priority: Priority level
        parameters: Model parameters
        created_by: User ID who created/updated
        
    Returns:
        True if saved successfully, False otherwise
    """
    from database.models import LLMConfiguration
    
    try:
        with get_db_session() as session:
            # Check if configuration exists
            config = session.query(LLMConfiguration).filter_by(
                provider=provider,
                model_name=model_name,
                task_type=task_type
            ).first()
            
            if config:
                # Update existing
                config.priority = priority
                config.parameters = parameters
                config.created_by = created_by
            else:
                # Create new
                config = LLMConfiguration(
                    provider=provider,
                    model_name=model_name,
                    task_type=task_type,
                    priority=priority,
                    parameters=parameters,
                    created_by=created_by
                )
                session.add(config)
            
            session.commit()
            return True
    except Exception as e:
        print(f"Error saving LLM configuration: {e}")
        return False


def delete_llm_configuration(config_id: int) -> bool:
    """
    Delete an LLM configuration
    
    Args:
        config_id: Configuration ID
        
    Returns:
        True if deleted successfully, False otherwise
    """
    from database.models import LLMConfiguration
    
    try:
        with get_db_session() as session:
            config = session.query(LLMConfiguration).filter_by(id=config_id).first()
            if config:
                session.delete(config)
                session.commit()
                return True
            return False
    except Exception as e:
        print(f"Error deleting LLM configuration: {e}")
        return False


def save_research_task(user_id: int, task_type: str, input_type: str, 
                       input_data: str, status: str = 'pending'):
    """
    Save a new research task
    
    Args:
        user_id: User's ID
        task_type: Type of task
        input_type: Type of input
        input_data: Input data
        status: Task status
        
    Returns:
        Task ID if created successfully, None otherwise
    """
    from database.models import ResearchTask
    
    try:
        with get_db_session() as session:
            task = ResearchTask(
                user_id=user_id,
                task_type=task_type,
                input_type=input_type,
                input_data=input_data,
                status=status
            )
            session.add(task)
            session.commit()
            return task.id
    except Exception as e:
        print(f"Error saving research task: {e}")
        return None


def update_research_task(task_id: int, status: str = None, result: dict = None, 
                        error_message: str = None, processing_time: float = None,
                        tokens_used: int = None):
    """
    Update a research task
    
    Args:
        task_id: Task ID
        status: New status
        result: Task result
        error_message: Error message if failed
        processing_time: Processing time in seconds
        tokens_used: Number of tokens used
        
    Returns:
        True if updated successfully, False otherwise
    """
    from database.models import ResearchTask
    from datetime import datetime
    
    try:
        with get_db_session() as session:
            task = session.query(ResearchTask).filter_by(id=task_id).first()
            if task:
                if status:
                    task.status = status
                if result is not None:
                    task.result = result
                if error_message:
                    task.error_message = error_message
                if processing_time is not None:
                    task.processing_time = processing_time
                if tokens_used is not None:
                    task.tokens_used = tokens_used
                if status == 'completed':
                    task.completed_at = datetime.utcnow()
                
                session.commit()
                return True
            return False
    except Exception as e:
        print(f"Error updating research task: {e}")
        return False


def get_user_research_tasks(user_id: int, limit: int = 10):
    """
    Get research tasks for a user
    
    Args:
        user_id: User's ID
        limit: Maximum number of tasks to return
        
    Returns:
        List of research tasks
    """
    from database.models import ResearchTask
    
    with get_db_session() as session:
        return session.query(ResearchTask).filter_by(
            user_id=user_id
        ).order_by(ResearchTask.created_at.desc()).limit(limit).all()