#!/bin/bash

# Coolify API Deployment Script for ROTZ Coder
# This script deploys the application to Coolify using the API

COOLIFY_URL="https://coolify.rotz.ai"
API_TOKEN="1|XMRaNatT0Mj1HlC6hxjiD4CdaAPxHatYF2emV8JUc2392aa7"
PROJECT_UUID="k8ssk8g88w448sg48s8goc4o"
SERVER_UUID="isk08ss8w8k0skk4o4wswwg8"

echo "🚀 Deploying ROTZ Coder to Coolify..."

# Generate secure secrets if not already set
if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -hex 32)
    echo "Generated JWT_SECRET: $JWT_SECRET"
fi

if [ -z "$ENCRYPTION_KEY" ]; then
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    echo "Generated ENCRYPTION_KEY: $ENCRYPTION_KEY"
fi

if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d '\n')
    echo "Generated DB_PASSWORD: $DB_PASSWORD"
fi

# Create the deployment configuration
DEPLOYMENT_CONFIG='{
  "project_uuid": "'$PROJECT_UUID'",
  "server_uuid": "'$SERVER_UUID'",
  "environment_name": "production",
  "type": "public-gh",
  "name": "rotz-coder",
  "description": "ROTZ Coder AI Research Engine",
  "git_repository": "https://github.com/rotzmediagroup/ROTZ-Coder",
  "git_branch": "coolify",
  "git_commit_sha": "HEAD",
  "publish_directory": ".",
  "build_pack": "dockercompose",
  "ports_exposes": "8501",
  "domains": "coder.rotz.app",
  "docker_compose_location": "/docker-compose.yml",
  "instant_deploy": false,
  "environment_variables": [
    {
      "key": "JWT_SECRET",
      "value": "'$JWT_SECRET'",
      "is_build_time": false
    },
    {
      "key": "ENCRYPTION_KEY",
      "value": "'$ENCRYPTION_KEY'",
      "is_build_time": false
    },
    {
      "key": "DB_PASSWORD",
      "value": "'$DB_PASSWORD'",
      "is_build_time": false
    },
    {
      "key": "DOMAIN",
      "value": "coder.rotz.app",
      "is_build_time": false
    },
    {
      "key": "SSL_ENABLED",
      "value": "true",
      "is_build_time": false
    },
    {
      "key": "SUPER_ADMIN_EMAIL",
      "value": "jerome@rotz.host",
      "is_build_time": false
    },
    {
      "key": "SUPER_ADMIN_PASSWORD",
      "value": "ChangeMe123!",
      "is_build_time": false
    }
  ]
}'

# Make the API call to create the application
echo "📝 Creating application in Coolify..."
RESPONSE=$(curl -s -X POST "${COOLIFY_URL}/api/v1/applications" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "${DEPLOYMENT_CONFIG}")

echo "Response: $RESPONSE"

# Check if deployment was successful
if echo "$RESPONSE" | grep -q "uuid"; then
    APP_UUID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['uuid'])")
    echo "✅ Application created successfully!"
    echo "🆔 Application UUID: $APP_UUID"
    echo ""
    echo "📊 Next steps:"
    echo "1. Visit ${COOLIFY_URL} to monitor deployment"
    echo "2. Check application logs"
    echo "3. Access the app at https://coder.rotz.app once deployed"
    echo ""
    echo "🔐 Important: Save these secrets!"
    echo "JWT_SECRET=${JWT_SECRET}"
    echo "ENCRYPTION_KEY=${ENCRYPTION_KEY}"
    echo "DB_PASSWORD=${DB_PASSWORD}"
else
    echo "❌ Deployment failed. Response:"
    echo "$RESPONSE"
    echo ""
    echo "Please check the Coolify dashboard manually at: ${COOLIFY_URL}"
fi