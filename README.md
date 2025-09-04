# 🧬 ROTZ Coder

**Enhanced AI Research Engine with Multi-LLM Support, User Authentication & Modern UI**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/rotzmediagroup/ROTZ-Coder.svg)](https://github.com/rotzmediagroup/ROTZ-Coder/releases)

> Transform research papers into production-ready code with enterprise-grade user management, security, and multi-provider AI access.

## 🚀 Overview

ROTZ Coder is an enhanced version of DeepCode, transformed into a comprehensive AI research platform featuring:

- **🔐 Enterprise Authentication**: Email/password + TOTP 2FA security
- **🤖 Multi-LLM Support**: 8+ AI providers including OpenAI, Anthropic, DeepSeek, Gemini
- **🎨 Modern UI**: Clean, responsive design inspired by modern web apps
- **👑 Admin Management**: Complete user and system administration
- **🔒 Secure Storage**: Encrypted API key storage per user
- **📊 Advanced Analytics**: Real-time usage tracking, performance monitoring, and insights dashboard

## ✨ Key Features

### 🔐 User Management
- **Secure Registration**: Email verification with strong password requirements
- **Two-Factor Authentication**: TOTP integration with QR code setup
- **Role-Based Access**: User, Admin, and Super Admin levels
- **Session Management**: JWT-based secure sessions with auto-expiry

### 🤖 Multi-LLM Provider Support
| Provider | Models | Specialization |
|----------|--------|----------------|
| **OpenAI** | GPT-4, GPT-3.5 Turbo | General purpose, coding |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | Document analysis, reasoning |
| **DeepSeek** | Coder-33B, Chat models | Code generation, debugging |
| **Google Gemini** | Pro, Ultra, Vision | Multimodal analysis |
| **OpenRouter** | Various open-source models | Cost-effective alternatives |
| **Qwen** | Chat, Coder models | Multilingual processing |
| **Grok** | xAI models | Real-time information |
| **Brave Search** | Web search API | Information retrieval |

### 🎨 Modern Interface
- **Clean Homepage**: Hero section with centered prompt box
- **Multi-Page Structure**: Organized navigation and workflows  
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Themes**: Customizable appearance (coming soon)

### ⚙️ Admin Panel
- **User Management**: Promote users, monitor activity
- **LLM Configuration**: Assign models to specific tasks
- **System Analytics**: Usage statistics and performance metrics
- **Provider Management**: Configure and monitor AI providers

### 📊 Advanced Analytics Dashboard
- **Real-time Monitoring**: Live usage tracking and system health metrics
- **User Behavior Analysis**: Activity patterns, feature usage, and engagement insights
- **API Usage & Costs**: Token consumption, cost analysis across all LLM providers
- **Performance Metrics**: Page load times, system performance, and optimization insights
- **Error Tracking**: Comprehensive error logging with severity categorization
- **Interactive Charts**: Plotly-powered visualizations with time-range filtering
- **Export Capabilities**: Data export for further analysis and reporting

## 🏃‍♂️ Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/rotzmediagroup/ROTZ-Coder.git
cd ROTZ-Coder

# Install dependencies
pip install -r requirements.txt

# Run installation test
python test_installation.py
```

### 2. Configuration
```bash
# Copy configuration template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# Edit with your settings
nano .streamlit/secrets.toml
```

### 3. Launch
```bash
# Start the application
streamlit run ui/streamlit_app.py

# Open your browser to http://localhost:8501
```

### 4. Initial Setup
1. **Super Admin Login**: jerome@rotz.host / ChangeMe123!
2. **Change Password**: Update super admin password
3. **Configure API Keys**: Add your LLM provider keys
4. **Create Users**: Register additional accounts as needed

## 📁 Project Structure

```
ROTZ-Coder/
├── 📱 pages/                    # Multi-page Streamlit app
│   ├── 1_🏠_Home.py            # Clean homepage with hero
│   ├── 2_📚_Information.py      # Documentation & guides
│   ├── 3_👤_Profile.py         # User dashboard & API keys
│   ├── 4_⚙️_Admin.py           # Admin panel
│   ├── 5_📊_Results.py         # Research results
│   ├── 6_🔑_Login.py           # Authentication
│   ├── 7_📝_Register.py        # User registration
│   └── 8_📊_Analytics.py       # Advanced analytics dashboard
├── 🔐 auth/                     # Authentication system
│   ├── authentication.py       # User auth, TOTP, JWT
│   ├── encryption.py          # API key encryption
│   └── __init__.py
├── 🗄️ database/                # Data models & migrations
│   ├── models.py               # SQLAlchemy models
│   └── __init__.py
├── 🤖 providers/                # LLM provider integrations
│   ├── base_provider.py        # Abstract provider class
│   ├── deepseek_provider.py    # DeepSeek integration
│   ├── gemini_provider.py      # Google Gemini integration
│   ├── openrouter_provider.py  # OpenRouter integration
│   ├── qwen_provider.py        # Qwen/Alibaba integration
│   ├── grok_provider.py        # xAI Grok integration
│   ├── provider_factory.py     # Provider factory pattern
│   └── __init__.py
├── 📊 analytics/                # Analytics & monitoring system
│   ├── collectors.py           # Data collection utilities
│   ├── dashboard.py            # Analytics dashboard functions
│   └── __init__.py
├── 🛠️ utils/                    # Utilities & helpers
│   ├── database.py             # Database utilities
│   └── ...
├── 🎨 ui/                       # Original UI (enhanced)
├── 🧪 tests/                    # Test suite
│   ├── test_analytics.py       # Analytics tests
│   └── __init__.py
├── 🔧 .streamlit/               # Configuration
│   └── secrets.toml            # App secrets (template)
├── 📚 SETUP.md                  # Detailed setup guide
├── 🧪 test_installation.py     # Installation verification
├── 📋 requirements.txt         # Python dependencies
├── 📋 requirements-dev.txt     # Development dependencies
└── ⚙️ pytest.ini               # Test configuration
```

## 🛠️ Configuration

### Environment Variables
```bash
# Required for production
export JWT_SECRET="your-super-secret-jwt-key"
export ENCRYPTION_KEY="your-base64-encryption-key"
export DATABASE_URL="postgresql://user:pass@localhost/rotz_coder"
```

### Streamlit Secrets
```toml
# .streamlit/secrets.toml
jwt_secret = "your-jwt-secret-here"
encryption_key = "your-encryption-key-here"

[admin_api_keys]
openai = "sk-your-openai-key"
anthropic = "sk-ant-your-anthropic-key"
```

### API Keys Setup
Each user configures their own encrypted API keys:

1. **OpenAI**: [Get API Key](https://platform.openai.com/api-keys)
2. **Anthropic**: [Get API Key](https://console.anthropic.com/settings/keys)
3. **DeepSeek**: [Get API Key](https://platform.deepseek.com/api_keys)
4. **Gemini**: [Get API Key](https://makersuite.google.com/app/apikey)
5. **OpenRouter**: [Get API Key](https://openrouter.ai/keys)
6. **Qwen**: [Get API Key](https://dashscope.aliyun.com/api-key)
7. **Grok**: [Get API Key](https://console.x.ai/settings/api-keys)
8. **Brave Search**: [Get API Key](https://api.search.brave.com/app/keys)

## 🎯 Usage Examples

### Research Paper Analysis
```python
# Upload a research paper PDF or paste arXiv URL
# ROTZ Coder will:
# 1. Extract key algorithms and mathematical models
# 2. Generate production-ready implementation
# 3. Create comprehensive documentation
# 4. Provide testing and optimization suggestions
```

### Code Generation from Description
```python
# Natural language prompt:
"Create a REST API for user management with authentication, 
rate limiting, and PostgreSQL integration using FastAPI"

# ROTZ Coder generates:
# - Complete FastAPI application structure
# - Database models and migrations
# - Authentication middleware
# - API documentation
# - Docker configuration
# - Unit tests
```

### Multi-Modal Analysis
```python
# Upload documents, images, or code repositories
# ROTZ Coder combines multiple AI providers to:
# - Analyze diagrams and flowcharts (Gemini Vision)
# - Generate code implementations (DeepSeek Coder)  
# - Create documentation (Claude 3)
# - Optimize performance (GPT-4)
```

### Analytics & Monitoring
```python
# Access the Analytics Dashboard (Admin only):
# 1. Navigate to 📊 Analytics page
# 2. View real-time usage metrics and system health
# 3. Analyze user behavior and API costs
# 4. Monitor performance and identify optimization opportunities
# 5. Track errors and system stability

# Analytics automatically tracks:
# - User activities and engagement patterns
# - API usage across all LLM providers
# - System performance and response times
# - Error rates and categorization
# - Cost analysis and token consumption
```

## 🔒 Security Features

- **Password Security**: bcrypt hashing with salt
- **API Key Encryption**: AES encryption using cryptography.fernet
- **Session Management**: JWT tokens with configurable expiry
- **Two-Factor Auth**: TOTP with QR code setup
- **Role-Based Access**: Granular permission system
- **Input Validation**: All inputs sanitized and validated
- **HTTPS Ready**: SSL/TLS support for production

## 📈 Analytics Features (v2.1)

### Real-time Dashboard
The Advanced Analytics Dashboard provides comprehensive insights into system usage and performance:

#### 👥 User Analytics
- **Activity Tracking**: Login patterns, feature usage, session duration
- **Engagement Metrics**: Most active users, popular features, retention rates
- **Behavior Analysis**: User flow analysis and interaction patterns

#### 🔌 API Usage Monitoring
- **Provider Performance**: Response times and success rates across all LLM providers
- **Cost Analysis**: Token consumption and estimated costs per provider/model
- **Usage Patterns**: Daily/weekly usage trends and peak usage times
- **Model Comparison**: Performance and cost comparison between different AI models

#### ⚡ Performance Metrics
- **System Health**: CPU, memory usage, and system load monitoring
- **Response Times**: Page load times and API response analytics
- **Database Performance**: Query execution times and optimization insights
- **Error Tracking**: Real-time error monitoring with severity categorization

#### 📊 Interactive Visualizations
- **Time-series Charts**: Track metrics over customizable time periods (7-90 days)
- **Bar Charts**: Compare usage across providers, models, and users
- **Pie Charts**: Visualize distribution of activities, costs, and errors
- **Real-time Updates**: Live data refresh with 30-second auto-refresh option

#### 🔐 Security & Access Control
- **Admin-only Access**: Analytics restricted to administrators and super admins
- **User Privacy**: Optional user-specific filtering for detailed analysis
- **Data Export**: Export analytics data for further analysis (coming soon)
- **Audit Trail**: Track who accesses analytics and when

### Technical Implementation
- **Database Models**: 5 new tables for comprehensive analytics tracking
- **Collection System**: Automatic, non-intrusive data collection
- **Performance**: Indexed queries for fast analytics even with large datasets
- **Scalability**: Designed to handle high-volume production environments

## 📊 System Requirements

### Minimum Requirements
- **Python**: 3.9+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for application + space for user data
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Recommended Setup
- **Python**: 3.11+
- **RAM**: 16GB for optimal performance
- **CPU**: Multi-core processor for concurrent AI requests
- **Database**: PostgreSQL for production deployments

## 🚀 Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to [Streamlit Cloud](https://share.streamlit.io)
3. Add secrets via dashboard
4. Deploy with one click

### Docker (Coming Soon)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "ui/streamlit_app.py"]
```

### Production Checklist
- [ ] Configure PostgreSQL database
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure email SMTP for notifications
- [ ] Set up monitoring and logging
- [ ] Configure backup procedures
- [ ] Set up CI/CD pipeline

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup
git clone https://github.com/rotzmediagroup/ROTZ-Coder.git
cd ROTZ-Coder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python test_installation.py
pytest tests/
```

### Adding New LLM Providers
1. Create provider class in `providers/`
2. Inherit from `LLMProvider` base class
3. Implement required methods
4. Register in `provider_factory.py`
5. Add configuration in admin panel
6. Update documentation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original DeepCode**: Built upon the excellent foundation from [HKUDS/DeepCode](https://github.com/HKUDS/DeepCode)
- **Data Intelligence Lab @ HKU**: For the original research and development
- **Streamlit Team**: For the amazing web framework
- **AI Provider Teams**: OpenAI, Anthropic, Google, and others for their APIs

## 📞 Support

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/rotzmediagroup/ROTZ-Coder/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/rotzmediagroup/ROTZ-Coder/discussions)
- **📧 Email**: [support@rotz.media](mailto:support@rotz.media)
- **🔗 Website**: [rotz.media](https://rotz.media)

## 🗺️ Roadmap

### ✅ v2.1 (Current Release)
- [x] **Advanced Analytics Dashboard**: Real-time monitoring, user behavior analysis, API cost tracking
- [x] **Enhanced Database Models**: Comprehensive analytics and monitoring tables
- [x] **Interactive Visualizations**: Plotly-powered charts with time-range filtering
- [x] **Performance Tracking**: System metrics, error logging, and optimization insights
- [x] **Test Framework**: Complete test suite with pytest and coverage reporting
- [ ] Email notifications system
- [ ] Export research results to various formats  
- [ ] Batch processing capabilities

### v2.2 (Next Release)
- [ ] **Notification System**: Email alerts for system events and user activities
- [ ] **Advanced Export**: PDF, Excel, JSON export capabilities for research results
- [ ] **Batch Processing**: Queue system for handling multiple research tasks
- [ ] **API Endpoints**: RESTful API for programmatic access
- [ ] **Enhanced Security**: Advanced audit logging and session management

### v2.3 (Future)
- [ ] **Team Collaboration**: Shared workspaces and collaborative research
- [ ] **Custom AI Models**: Fine-tuning capabilities for specialized tasks
- [ ] **Advanced Workflows**: Automated research pipelines and templates
- [ ] **Integration Hub**: Connect with popular development tools and platforms

### v3.0 (Long-term Vision)
- [ ] **Plugin Architecture**: Extensible system for custom tools and integrations
- [ ] **IDE Extensions**: Native support for VS Code, PyCharm, and other IDEs
- [ ] **Enterprise Features**: SSO integration, advanced user management, compliance tools
- [ ] **AI Orchestration**: Advanced multi-model coordination and optimization

---

<div align="center">

**🧬 ROTZ Coder - Transforming Research into Reality**

[![GitHub stars](https://img.shields.io/github/stars/rotzmediagroup/ROTZ-Coder.svg?style=social&label=Star)](https://github.com/rotzmediagroup/ROTZ-Coder)
[![GitHub forks](https://img.shields.io/github/forks/rotzmediagroup/ROTZ-Coder.svg?style=social&label=Fork)](https://github.com/rotzmediagroup/ROTZ-Coder/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/rotzmediagroup/ROTZ-Coder.svg?style=social&label=Watch)](https://github.com/rotzmediagroup/ROTZ-Coder)

Made with ❤️ by the ROTZ Media Group

</div>
