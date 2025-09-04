#!/bin/bash
set -e

echo "🚀 Starting ROTZ Coder..."

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL to be ready..."
    while ! nc -z db 5432; do
        sleep 1
    done
    echo "✅ PostgreSQL is ready!"
}

# Function to generate secrets if not provided
generate_secrets() {
    if [ -z "$JWT_SECRET" ]; then
        echo "⚠️  JWT_SECRET not set, generating random secret..."
        export JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
        echo "Generated JWT_SECRET (save this): $JWT_SECRET"
    fi
    
    if [ -z "$ENCRYPTION_KEY" ]; then
        echo "⚠️  ENCRYPTION_KEY not set, generating random key..."
        export ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
        echo "Generated ENCRYPTION_KEY (save this): $ENCRYPTION_KEY"
    fi
}

# Function to initialize database
init_database() {
    echo "🗄️  Initializing database..."
    python -c "
from database.models import init_database, init_super_admin, init_default_llm_configs, User
import os

# Initialize database with PostgreSQL URL
database_url = os.environ.get('DATABASE_URL', 'sqlite:///deepcode.db')
print(f'Using database: {database_url.split(\"@\")[1] if \"@\" in database_url else database_url}')

engine, Session = init_database(database_url)
session = Session()

try:
    # Initialize super admin
    init_super_admin(session)
    
    # Get super admin for default configs
    super_admin = session.query(User).filter_by(email=os.environ.get('SUPER_ADMIN_EMAIL', 'jerome@rotz.host')).first()
    if super_admin:
        init_default_llm_configs(session, super_admin.id)
    
    session.commit()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️  Database initialization warning: {e}')
    session.rollback()
finally:
    session.close()
"
}

# Function to create Streamlit secrets file
create_streamlit_secrets() {
    echo "🔐 Creating Streamlit secrets..."
    cat > /app/.streamlit/secrets.toml << EOF
# Auto-generated Streamlit secrets
jwt_secret = "${JWT_SECRET}"
encryption_key = "${ENCRYPTION_KEY}"

[database]
url = "${DATABASE_URL}"

[admin_api_keys]
openai = "${OPENAI_API_KEY:-}"
anthropic = "${ANTHROPIC_API_KEY:-}"
deepseek = "${DEEPSEEK_API_KEY:-}"
gemini = "${GEMINI_API_KEY:-}"
openrouter = "${OPENROUTER_API_KEY:-}"
qwen = "${QWEN_API_KEY:-}"
grok = "${GROK_API_KEY:-}"
brave_search = "${BRAVE_SEARCH_API_KEY:-}"

[email]
smtp_host = "${SMTP_HOST:-}"
smtp_port = ${SMTP_PORT:-587}
smtp_user = "${SMTP_USER:-}"
smtp_password = "${SMTP_PASSWORD:-}"
smtp_from = "${SMTP_FROM:-noreply@rotz.host}"

[app]
env = "${APP_ENV:-production}"
log_level = "${LOG_LEVEL:-INFO}"
session_timeout = ${SESSION_TIMEOUT:-3600}
max_upload_size = ${MAX_UPLOAD_SIZE:-100}
EOF
    
    echo "✅ Streamlit secrets created"
}

# Main execution
echo "🔧 Running pre-flight checks..."

# Generate secrets if needed
generate_secrets

# Wait for database
if [ ! -z "$DATABASE_URL" ] && [[ "$DATABASE_URL" == *"postgresql"* ]]; then
    wait_for_postgres
fi

# Initialize database
init_database

# Create Streamlit secrets
create_streamlit_secrets

# Create necessary directories
mkdir -p /app/data /app/uploads /app/logs

echo "✅ Pre-flight checks complete!"
echo "🚀 Starting Streamlit application..."

# Execute the main command
exec "$@"