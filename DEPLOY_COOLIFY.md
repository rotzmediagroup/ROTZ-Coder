# 🚀 Deploying ROTZ Coder with Coolify

This guide explains how to deploy ROTZ Coder using Coolify for easy, automated deployment with SSL, monitoring, and zero-downtime updates.

## 📋 Prerequisites

- Coolify server installed and running
- GitHub repository access
- Domain name configured (e.g., coder.rotz.app)

## 🔧 Quick Deploy

### 1. Via Coolify UI

1. **Login to Coolify** at https://coolify.rotz.ai
2. **Create New Application**:
   - Type: Docker Compose
   - Source: GitHub
   - Repository: `https://github.com/rotzmediagroup/ROTZ-Coder`
   - Branch: `coolify`
   - Docker Compose Path: `/docker-compose.yml`

3. **Configure Environment Variables**:
   ```env
   JWT_SECRET=<generate-secure-secret>
   ENCRYPTION_KEY=<generate-encryption-key>
   DB_PASSWORD=<strong-database-password>
   DOMAIN=coder.rotz.app
   SSL_ENABLED=true
   ```

4. **Deploy**: Click "Deploy" and Coolify will handle the rest!

### 2. Via API Deployment

```bash
# Deploy using Coolify API
curl -X POST https://coolify.rotz.ai/api/v1/applications \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rotz-coder",
    "repository": "https://github.com/rotzmediagroup/ROTZ-Coder",
    "branch": "coolify",
    "compose_file": "docker-compose.yml",
    "domain": "coder.rotz.app",
    "environment": {
      "JWT_SECRET": "your-secret",
      "ENCRYPTION_KEY": "your-key",
      "DB_PASSWORD": "your-password"
    }
  }'
```

## 🔐 Security Configuration

### Generate Required Secrets

```bash
# Generate JWT Secret
openssl rand -hex 32

# Generate Encryption Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate Database Password
openssl rand -base64 32
```

### Environment Variables

Required variables that MUST be set:

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET` | JWT signing key | 64-character hex string |
| `ENCRYPTION_KEY` | API key encryption | Fernet key (base64) |
| `DB_PASSWORD` | PostgreSQL password | Strong password |

Optional but recommended:

| Variable | Description | Default |
|----------|-------------|---------|
| `DOMAIN` | Your domain | coder.rotz.app |
| `SSL_ENABLED` | Enable HTTPS | true |
| `SUPER_ADMIN_EMAIL` | Admin email | jerome@rotz.host |
| `SUPER_ADMIN_PASSWORD` | Initial password | ChangeMe123! |

## 🗄️ Database Setup

The application automatically:
1. Creates PostgreSQL database on first run
2. Runs all migrations
3. Creates super admin account
4. Initializes default LLM configurations

### Backup Strategy

```bash
# Backup database
docker exec rotz-coder-db pg_dump -U rotz rotz_coder > backup.sql

# Restore database
docker exec -i rotz-coder-db psql -U rotz rotz_coder < backup.sql
```

## 🌐 Domain & SSL Setup

Coolify automatically:
- Configures nginx proxy
- Generates Let's Encrypt SSL certificates
- Sets up auto-renewal
- Handles WebSocket connections for Streamlit

Your app will be available at: https://coder.rotz.app

## 📊 Monitoring

### Health Checks

The application includes health checks:
- Endpoint: `https://coder.rotz.app/_stcore/health`
- Interval: 30 seconds
- Timeout: 10 seconds

### Logs

View logs through Coolify UI or:

```bash
# Application logs
docker logs rotz-coder-app

# Database logs
docker logs rotz-coder-db

# All services
docker-compose logs -f
```

## 🔄 Updates & Maintenance

### Zero-Downtime Updates

```bash
# Via Coolify UI
1. Go to your application
2. Click "Redeploy"
3. Coolify handles rolling update

# Via Git Push
git push origin coolify
# Coolify auto-deploys on push
```

### Scaling

Modify `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker exec rotz-coder-db pg_isready
   ```

2. **Application Won't Start**
   ```bash
   # Check logs
   docker logs rotz-coder-app --tail 100
   ```

3. **SSL Certificate Issues**
   - Verify domain DNS points to server
   - Check Coolify proxy settings
   - Ensure port 443 is open

### Reset Application

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: Deletes data)
docker-compose down -v

# Restart fresh
docker-compose up -d
```

## 📈 Performance Tuning

### Optimize Streamlit

Add to `.streamlit/config.toml`:

```toml
[server]
maxCachedMessageAge = 12h
maxMessageSize = 200

[runner]
fastReruns = true

[browser]
serverAddress = "coder.rotz.app"
```

### Database Optimization

```sql
-- Add indexes for performance
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_api_usage_created ON api_usage_logs(created_at);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
```

## 🎯 Post-Deployment Checklist

- [ ] Verify application accessible at https://coder.rotz.app
- [ ] Login with super admin account
- [ ] Change default password
- [ ] Configure API keys
- [ ] Test LLM providers
- [ ] Set up email notifications
- [ ] Configure backup schedule
- [ ] Set up monitoring alerts
- [ ] Review security settings
- [ ] Test user registration flow

## 📞 Support

- **GitHub Issues**: https://github.com/rotzmediagroup/ROTZ-Coder/issues
- **Email**: support@rotz.media
- **Documentation**: https://github.com/rotzmediagroup/ROTZ-Coder/wiki

## 🔗 Useful Links

- **Coolify Dashboard**: https://coolify.rotz.ai
- **Application URL**: https://coder.rotz.app
- **Health Check**: https://coder.rotz.app/_stcore/health
- **GitHub Repository**: https://github.com/rotzmediagroup/ROTZ-Coder

---

Made with ❤️ by ROTZ Media Group