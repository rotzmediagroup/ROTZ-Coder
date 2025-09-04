"""
Database models for DeepCode user management and LLM configuration
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)
    totp_secret = Column(String(32))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_keys = relationship("UserApiKey", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    research_tasks = relationship("ResearchTask", back_populates="user", cascade="all, delete-orphan")
    llm_configurations = relationship("LLMConfiguration", back_populates="created_by_user")
    user_activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    api_usage_logs = relationship("ApiUsageLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', is_admin={self.is_admin})>"


class UserApiKey(Base):
    __tablename__ = 'user_api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic, brave, deepseek, gemini, openrouter, qwen, grok
    api_key_encrypted = Column(Text, nullable=False)  # Encrypted API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<UserApiKey(user_id={self.user_id}, provider='{self.provider}')>"


class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, expires_at={self.expires_at})>"


class LLMConfiguration(Base):
    __tablename__ = 'llm_configurations'
    
    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)  # openai, anthropic, etc.
    model_name = Column(String(100), nullable=False)  # gpt-4, claude-3, etc.
    task_type = Column(String(100), nullable=False)  # code_generation, document_analysis, etc.
    priority = Column(Integer, default=1)  # Priority for task assignment
    parameters = Column(JSON)  # Additional model parameters
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User", back_populates="llm_configurations")
    
    def __repr__(self):
        return f"<LLMConfiguration(provider='{self.provider}', model='{self.model_name}', task='{self.task_type}')>"


class ResearchTask(Base):
    __tablename__ = 'research_tasks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_type = Column(String(50))  # paper2code, text2web, codebase_analysis, etc.
    input_type = Column(String(50))  # pdf, url, text, file
    input_data = Column(Text)  # Store input content or reference
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    result = Column(JSON)  # Store the result as JSON
    error_message = Column(Text)
    processing_time = Column(Float)  # Time taken in seconds
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="research_tasks")
    
    def __repr__(self):
        return f"<ResearchTask(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class UserActivity(Base):
    """Track user actions and behavior for analytics"""
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # login, logout, research_task, api_key_update, etc.
    page = Column(String(100))  # Which page/section the activity occurred on
    details = Column(JSON)  # Additional activity details
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    session_id = Column(String(255), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="user_activities")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_activity_time', 'user_id', 'created_at'),
        Index('idx_activity_type_time', 'activity_type', 'created_at'),
    )
    
    def __repr__(self):
        return f"<UserActivity(user_id={self.user_id}, type='{self.activity_type}', time={self.created_at})>"


class ApiUsageLog(Base):
    """Track API usage and performance metrics"""
    __tablename__ = 'api_usage_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)  # openai, anthropic, etc.
    model_name = Column(String(100), nullable=False, index=True)
    task_type = Column(String(100), index=True)  # code_generation, document_analysis, etc.
    request_type = Column(String(50))  # completion, chat, embedding, etc.
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    response_time_ms = Column(Integer)  # Response time in milliseconds
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text)
    cost_estimate = Column(Float)  # Estimated cost in USD
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="api_usage_logs")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_usage_time', 'user_id', 'created_at'),
        Index('idx_provider_usage_time', 'provider', 'created_at'),
        Index('idx_success_time', 'success', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ApiUsageLog(user_id={self.user_id}, provider='{self.provider}', tokens={self.total_tokens})>"


class SystemMetrics(Base):
    """Track system-wide performance and health metrics"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    metric_type = Column(String(50), nullable=False, index=True)  # cpu_usage, memory_usage, active_users, etc.
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # percent, bytes, count, etc.
    tags = Column(JSON)  # Additional metadata as key-value pairs
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_metric_type_time', 'metric_type', 'created_at'),
        Index('idx_metric_name_time', 'metric_name', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SystemMetrics(type='{self.metric_type}', name='{self.metric_name}', value={self.value})>"


class ErrorLog(Base):
    """Track application errors and exceptions"""
    __tablename__ = 'error_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Can be null for system errors
    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    request_path = Column(String(500))
    request_method = Column(String(10))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    severity = Column(String(20), default='error', index=True)  # debug, info, warning, error, critical
    resolved = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")  # Optional relationship
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_error_type_time', 'error_type', 'created_at'),
        Index('idx_severity_time', 'severity', 'created_at'),
        Index('idx_resolved_time', 'resolved', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ErrorLog(type='{self.error_type}', severity='{self.severity}', time={self.created_at})>"


class PerformanceMetrics(Base):
    """Track page load times and application performance"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    page = Column(String(100), nullable=False, index=True)
    load_time_ms = Column(Integer, nullable=False)  # Page load time in milliseconds
    memory_usage_mb = Column(Float)  # Memory usage in MB
    cpu_usage_percent = Column(Float)  # CPU usage percentage
    database_queries = Column(Integer)  # Number of database queries
    database_time_ms = Column(Integer)  # Total database query time
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")  # Optional relationship
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_page_time', 'page', 'created_at'),
        Index('idx_user_performance', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<PerformanceMetrics(page='{self.page}', load_time={self.load_time_ms}ms)>"


# Database initialization function
def init_database(database_url=None):
    """
    Initialize the database with all tables
    
    Args:
        database_url: Database URL (defaults to SQLite for development)
    """
    if database_url is None:
        # Use SQLite for development
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///deepcode.db')
    
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return engine, Session


# Super admin initialization
def init_super_admin(session):
    """
    Initialize the super admin user (jerome@rotz.host)
    
    Args:
        session: SQLAlchemy session
    """
    from auth.authentication import hash_password
    
    super_admin_email = "jerome@rotz.host"
    
    # Check if super admin already exists
    existing_admin = session.query(User).filter_by(email=super_admin_email).first()
    
    if not existing_admin:
        # Create super admin with a default password (should be changed on first login)
        super_admin = User(
            email=super_admin_email,
            password_hash=hash_password("ChangeMe123!"),  # Default password
            full_name="Jerome Rotz",
            is_admin=True,
            is_super_admin=True
        )
        session.add(super_admin)
        session.commit()
        print(f"✅ Super admin created: {super_admin_email}")
        print("⚠️  Default password: ChangeMe123! (Please change on first login)")
    else:
        # Ensure existing user has super admin privileges
        if not existing_admin.is_super_admin:
            existing_admin.is_super_admin = True
            existing_admin.is_admin = True
            session.commit()
            print(f"✅ Existing user {super_admin_email} promoted to super admin")
        else:
            print(f"✅ Super admin {super_admin_email} already exists")


# Default LLM configurations
def init_default_llm_configs(session, admin_id):
    """
    Initialize default LLM configurations
    
    Args:
        session: SQLAlchemy session
        admin_id: ID of the admin user creating the configs
    """
    default_configs = [
        # OpenAI configurations
        {
            "provider": "openai",
            "model_name": "gpt-4-turbo-preview",
            "task_type": "code_generation",
            "priority": 1,
            "parameters": {"temperature": 0.7, "max_tokens": 4000}
        },
        {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "task_type": "general_query",
            "priority": 2,
            "parameters": {"temperature": 0.5, "max_tokens": 2000}
        },
        # Anthropic configurations
        {
            "provider": "anthropic",
            "model_name": "claude-3-opus-20240229",
            "task_type": "document_analysis",
            "priority": 1,
            "parameters": {"temperature": 0.3, "max_tokens": 4000}
        },
        {
            "provider": "anthropic",
            "model_name": "claude-3-sonnet-20240229",
            "task_type": "code_review",
            "priority": 1,
            "parameters": {"temperature": 0.2, "max_tokens": 3000}
        },
        # DeepSeek configurations
        {
            "provider": "deepseek",
            "model_name": "deepseek-coder-33b",
            "task_type": "code_generation",
            "priority": 2,
            "parameters": {"temperature": 0.5, "max_tokens": 3000}
        },
        # Gemini configurations
        {
            "provider": "gemini",
            "model_name": "gemini-pro",
            "task_type": "multimodal_analysis",
            "priority": 1,
            "parameters": {"temperature": 0.4, "max_tokens": 3000}
        },
        # OpenRouter configurations
        {
            "provider": "openrouter",
            "model_name": "meta-llama/llama-2-70b-chat",
            "task_type": "general_query",
            "priority": 3,
            "parameters": {"temperature": 0.6, "max_tokens": 2000}
        },
        # Qwen configurations
        {
            "provider": "qwen",
            "model_name": "qwen-72b-chat",
            "task_type": "multilingual_processing",
            "priority": 1,
            "parameters": {"temperature": 0.5, "max_tokens": 3000}
        },
        # Grok configurations
        {
            "provider": "grok",
            "model_name": "grok-1",
            "task_type": "reasoning",
            "priority": 1,
            "parameters": {"temperature": 0.4, "max_tokens": 3000}
        }
    ]
    
    for config_data in default_configs:
        # Check if configuration already exists
        existing = session.query(LLMConfiguration).filter_by(
            provider=config_data["provider"],
            model_name=config_data["model_name"],
            task_type=config_data["task_type"]
        ).first()
        
        if not existing:
            config = LLMConfiguration(
                provider=config_data["provider"],
                model_name=config_data["model_name"],
                task_type=config_data["task_type"],
                priority=config_data["priority"],
                parameters=config_data["parameters"],
                created_by=admin_id
            )
            session.add(config)
    
    session.commit()
    print("✅ Default LLM configurations initialized")


if __name__ == "__main__":
    # Test database creation
    engine, Session = init_database()
    session = Session()
    
    # Initialize super admin
    init_super_admin(session)
    
    # Get super admin for creating default configs
    super_admin = session.query(User).filter_by(email="jerome@rotz.host").first()
    if super_admin:
        init_default_llm_configs(session, super_admin.id)
    
    session.close()
    print("✅ Database initialized successfully")