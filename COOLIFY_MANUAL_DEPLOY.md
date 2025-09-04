# 🚀 Manual Deployment to Coolify

Since the API deployment requires specific endpoint knowledge, here's how to deploy ROTZ Coder manually through the Coolify UI.

## 📝 Step-by-Step Deployment

### 1. Login to Coolify
Navigate to: https://coolify.rotz.ai

### 2. Create New Application

1. **Click "New Resource"** or "Add Application"
2. **Select Source Type**: 
   - Choose "Public Repository" (GitHub)
   
3. **Configure Git Repository**:
   - Repository URL: `https://github.com/rotzmediagroup/ROTZ-Coder`
   - Branch: `coolify`
   - Build Pack: `Docker Compose`
   
4. **Set Application Details**:
   - Name: `rotz-coder`
   - Description: `ROTZ Coder AI Research Engine`

### 3. Configure Environment Variables

Click on "Environment Variables" and add the following (generate secure values):

```bash
# Required Security Keys
JWT_SECRET=<generate with: openssl rand -hex 32>
ENCRYPTION_KEY=<generate with: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
DB_PASSWORD=<generate with: openssl rand -base64 32>

# Application Configuration
DOMAIN=coder.rotz.app
SSL_ENABLED=true
APP_ENV=production
LOG_LEVEL=INFO

# Super Admin Account
SUPER_ADMIN_EMAIL=jerome@rotz.host
SUPER_ADMIN_PASSWORD=ChangeMe123!

# Database Configuration
DATABASE_URL=postgresql://rotz:${DB_PASSWORD}@db:5432/rotz_coder

# Redis Configuration (Optional)
REDIS_PASSWORD=<generate secure password>
```

### 4. Configure Domains & SSL

1. **Domain Settings**:
   - Primary Domain: `coder.rotz.app`
   - Enable SSL: ✅ Yes
   - Force HTTPS: ✅ Yes

2. **Proxy Settings**:
   - Port: `8501`
   - Health Check Path: `/_stcore/health`

### 5. Docker Compose Configuration

Ensure the Docker Compose file path is set to: `/docker-compose.yml`

### 6. Resource Limits (Optional)

Set appropriate resource limits:
- CPU: 2 cores (minimum)
- Memory: 4GB (recommended)
- Storage: 10GB

### 7. Deploy

1. Click **"Save"** to save all configurations
2. Click **"Deploy"** to start the deployment
3. Monitor the build logs
4. Wait for the health checks to pass

## 🔍 Verification Steps

### Check Deployment Status
1. Go to the application dashboard
2. Check that all services are "Running":
   - `app` - Main application
   - `db` - PostgreSQL database
   - `redis` - Cache service (optional)

### Verify Application
1. Visit: https://coder.rotz.app
2. You should see the ROTZ Coder homepage
3. Login with: `jerome@rotz.host` / `ChangeMe123!`

### Health Check
Visit: https://coder.rotz.app/_stcore/health
Should return: `{"status": "ok"}`

## 🔐 Generated Secrets Examples

Here are example commands to generate secure secrets:

```bash
# JWT Secret (64 characters hex)
openssl rand -hex 32
# Example: a1b2c3d4e5f6789...

# Encryption Key (Fernet key)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Example: gAAAAABh...

# Database Password (strong random)
openssl rand -base64 32
# Example: xY9Zw8V7u6T5s4R3...
```

## 🚨 Troubleshooting

### If deployment fails:

1. **Check Build Logs**:
   - Look for Docker build errors
   - Check for missing dependencies

2. **Check Runtime Logs**:
   ```
   Application > Logs > View All
   ```

3. **Database Connection Issues**:
   - Verify `DATABASE_URL` is correct
   - Check PostgreSQL container is running

4. **Domain Not Working**:
   - Verify DNS points to Coolify server
   - Check SSL certificate generation

### Common Issues:

- **Port Already in Use**: Change `APP_PORT` environment variable
- **Memory Issues**: Increase resource limits
- **Database Migration Failed**: Check database logs

## 📊 Post-Deployment

After successful deployment:

1. **Change Default Password**:
   - Login as super admin
   - Go to Profile > Change Password

2. **Configure API Keys**:
   - Go to Profile > API Keys
   - Add your LLM provider keys

3. **Test Features**:
   - Upload a test document
   - Try a simple query
   - Check analytics dashboard

4. **Set Up Backups**:
   - Configure automated database backups
   - Set up monitoring alerts

## 🔗 Access Points

- **Application**: https://coder.rotz.app
- **Health Check**: https://coder.rotz.app/_stcore/health
- **Coolify Dashboard**: https://coolify.rotz.ai
- **GitHub Repository**: https://github.com/rotzmediagroup/ROTZ-Coder

## 📝 Notes

- The application will automatically initialize the database on first run
- All secrets are stored encrypted in the database
- User API keys are encrypted with the `ENCRYPTION_KEY`
- Sessions are managed with JWT tokens using `JWT_SECRET`

---

Need help? Contact support@rotz.media