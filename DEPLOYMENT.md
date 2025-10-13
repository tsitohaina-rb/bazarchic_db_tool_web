# Deployment Guide for Render

## Quick Start

This application is configured for one-click deployment to Render.

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your repository
5. Render will automatically detect `render.yaml` and configure the service

### Option 2: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your repository
4. Configure as follows:
   - **Name**: bazarchic-db-tool
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -c gunicorn_config.py app:app`
   - **Plan**: Free (or choose your plan)

### Environment Variables (Required)

Add these in Render's Environment settings:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Database Configuration
DB_HOST=your-database-host
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_NAME=your-database-name
DB_PORT=3306

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Dropbox Configuration (Optional)
DROPBOX_APP_KEY=your-app-key
DROPBOX_APP_SECRET=your-app-secret
DROPBOX_REFRESH_TOKEN=your-refresh-token
```

## Troubleshooting

### Issue: Worker Timeout / No Open Ports

**Solution**: The application is now configured with:
- 120-second worker timeout in `gunicorn_config.py`
- Proper PORT binding from environment variable
- Database connection timeouts (10 seconds)
- Health check endpoint at `/health`

### Issue: Out of Memory

**Solution**: 
- Free tier on Render has 512MB RAM limit
- Consider upgrading to a paid plan if needed
- The app is optimized to use minimal memory during startup

### Issue: Database Connection Failed

**Solution**:
- Verify all database environment variables are correct
- Ensure your database allows connections from Render's IP addresses
- Check if database is accessible from external networks
- Connection timeout is set to 10 seconds

## Files Added for Render Deployment

- `gunicorn_config.py` - Gunicorn production configuration
- `render.yaml` - Render Blueprint configuration
- `Procfile` - Alternative process file
- `DEPLOYMENT.md` - This file

## Health Check

The application includes a health check endpoint:
- **Endpoint**: `/health`
- **Response**: `{"status": "healthy", "service": "bazarchic-db-tool"}`

Render will use this to verify the application is running correctly.

## Deployment Checklist

- [ ] All environment variables configured in Render
- [ ] Database is accessible from external networks
- [ ] Cloudinary credentials are correct
- [ ] Application deploys without errors
- [ ] Health check endpoint returns 200 OK
- [ ] Can access the application via Render URL

## Local Testing with Gunicorn

Test the production configuration locally:

```bash
# Set PORT environment variable
export PORT=5000

# Run with gunicorn
gunicorn -c gunicorn_config.py app:app

# Test health check
curl http://localhost:5000/health
```

## Performance Tips

1. **Database Connection Pool**: Consider implementing connection pooling for high traffic
2. **Caching**: Add Redis for caching database queries
3. **CDN**: Use Cloudinary's CDN for serving images
4. **Async Workers**: Consider switching to `gevent` or `eventlet` worker class for better concurrency

## Support

For issues specific to Render deployment, consult:
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
