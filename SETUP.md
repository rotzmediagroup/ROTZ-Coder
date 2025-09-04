# DeepCode Enhanced Setup Guide

## Overview

DeepCode has been transformed from a simple Streamlit app into a comprehensive AI research platform with user authentication, multi-LLM support, and admin management capabilities.

## New Features

### 🔐 Authentication System
- User registration with email/password
- Two-factor authentication (TOTP)
- Secure session management
- Encrypted API key storage per user

### 🤖 Multi-LLM Provider Support
- **OpenAI**: GPT-4, GPT-3.5 models
- **Anthropic**: Claude 3 models  
- **DeepSeek**: Coder-specialized models
- **Google Gemini**: Multimodal capabilities
- **OpenRouter**: Access to various open-source models
- **Qwen**: Alibaba's multilingual models
- **Grok**: xAI's real-time models
- **Brave Search**: Web search integration

### ⚙️ Admin Panel
- User management (super admin: jerome@rotz.host)
- LLM provider configuration
- Model-to-task assignment
- System analytics and monitoring

### 🎨 Modern UI
- Clean homepage design (inspired by lovable.dev)
- Multi-page structure
- Responsive design
- Hero section with centered prompt box

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Secrets

Copy the template configuration:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your settings:

```toml
# JWT Secret (generate a strong key)
jwt_secret = "your-super-secret-jwt-key-change-in-production"

# Encryption key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
encryption_key = "your-base64-encryption-key-change-in-production"

# Database URL (optional - SQLite used by default)
# database_url = "postgresql://username:password@localhost/deepcode"
```

### 3. Generate Security Keys

```bash
# Generate JWT secret
python -c "import secrets; print('JWT Secret:', secrets.token_urlsafe(32))"

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print('Encryption Key:', Fernet.generate_key().decode())"
```

### 4. Run the Application

```bash
streamlit run ui/streamlit_app.py
```

Or run the main script:

```bash
python deepcode.py
```

### 5. Initial Setup

1. **Access the app**: Open your browser to `http://localhost:8501`
2. **Database initialization**: The database will be automatically created on first run
3. **Super admin account**: jerome@rotz.host is created with password `ChangeMe123!`
4. **Navigate**: Use the homepage to register new users or login

## File Structure

```
deepcode/
├── auth/                   # Authentication system
│   ├── authentication.py  # User auth, TOTP
│   ├── encryption.py      # API key encryption
│   └── __init__.py
├── database/              # Database models
│   ├── models.py          # SQLAlchemy models
│   └── __init__.py
├── pages/                 # Streamlit pages
│   ├── 1_🏠_Home.py       # Clean homepage
│   ├── 2_📚_Information.py # Documentation
│   ├── 3_👤_Profile.py    # User dashboard
│   ├── 4_⚙️_Admin.py      # Admin panel
│   ├── 5_📊_Results.py    # Research results
│   ├── 6_🔑_Login.py      # Login page
│   └── 7_📝_Register.py   # Registration
├── providers/             # LLM providers
│   ├── base_provider.py   # Base provider class
│   ├── deepseek_provider.py
│   ├── gemini_provider.py
│   ├── openrouter_provider.py
│   ├── qwen_provider.py
│   ├── grok_provider.py
│   ├── provider_factory.py
│   └── __init__.py
├── utils/                 # Utilities
│   ├── database.py        # DB utilities
│   └── ...
├── ui/                    # Original UI (enhanced)
│   ├── streamlit_app.py   # Main app entry
│   └── ...
├── .streamlit/
│   └── secrets.toml       # Configuration
└── requirements.txt       # Dependencies
```

## Usage Guide

### For Regular Users

1. **Register**: Create an account with email/password
2. **Set up 2FA**: Configure TOTP on first login
3. **Add API Keys**: Go to Profile → API Keys to add your LLM provider keys
4. **Start Research**: Use the main prompt box to begin research tasks

### For Administrators

1. **Login as Admin**: Use jerome@rotz.host (super admin) or promoted admin account
2. **User Management**: Admin Panel → Users to promote users to admin
3. **LLM Configuration**: Admin Panel → LLM Config to set up model assignments
4. **System Monitoring**: Admin Panel → Analytics for usage statistics

### API Key Setup

Each user needs to configure their own API keys:

1. **OpenAI**: Get from https://platform.openai.com/api-keys
2. **Anthropic**: Get from https://console.anthropic.com/settings/keys  
3. **DeepSeek**: Get from https://platform.deepseek.com/api_keys
4. **Gemini**: Get from https://makersuite.google.com/app/apikey
5. **OpenRouter**: Get from https://openrouter.ai/keys
6. **Qwen**: Get from https://dashscope.aliyun.com/api-key
7. **Grok**: Get from https://console.x.ai/settings/api-keys
8. **Brave Search**: Get from https://api.search.brave.com/app/keys

## Security Features

- **Password Hashing**: bcrypt with salt
- **API Key Encryption**: AES encryption via cryptography.fernet
- **Session Management**: JWT tokens with expiration
- **2FA Required**: TOTP authentication for enhanced security
- **Role-based Access**: User/Admin/Super Admin roles
- **Input Validation**: All inputs sanitized and validated

## Database

### Default (SQLite)
- File: `deepcode.db` (created automatically)
- Good for: Development, small deployments

### Production (PostgreSQL)
```bash
# Install PostgreSQL
pip install psycopg2-binary

# Configure in secrets.toml
database_url = "postgresql://username:password@localhost/deepcode"
```

## Troubleshooting

### Database Issues
```bash
# Reset database
rm deepcode.db
# Restart app to recreate
```

### Authentication Issues
```bash
# Clear Streamlit cache
streamlit cache clear
```

### API Key Issues
- Verify key format for each provider
- Check API key permissions and quotas
- Test keys in provider's playground first

## Production Deployment

### Environment Variables
```bash
export JWT_SECRET="your-jwt-secret"
export ENCRYPTION_KEY="your-encryption-key"
export DATABASE_URL="postgresql://..."
```

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy

### Docker (Future)
```dockerfile
# Dockerfile will be provided in future update
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "ui/streamlit_app.py"]
```

## Migration from Original DeepCode

The original functionality is preserved in the Information page. New features are additive:

- **Original workflows**: Still available through the main prompt
- **Existing tools**: All original tools and agents work unchanged  
- **New UI**: Modern interface with authentication layer
- **Enhanced capabilities**: Multi-LLM support for better results

## Support

- **Issues**: Report on GitHub repository
- **Documentation**: Check Information page for detailed feature docs
- **Super Admin**: jerome@rotz.host for system administration
- **API Help**: Each provider page has links to official documentation

---

## Quick Start Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure secrets in `.streamlit/secrets.toml`
- [ ] Run app: `streamlit run ui/streamlit_app.py`
- [ ] Register user account or login as super admin
- [ ] Add API keys in Profile section
- [ ] Start researching with enhanced multi-LLM support!

🎉 **Welcome to the enhanced DeepCode experience!**