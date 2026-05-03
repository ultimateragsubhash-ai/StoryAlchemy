# 🚀 Deployment Guide

## Overview

Deploy StoryAlchemy using:
- **Railway** for the FastAPI backend (free tier available)
- **Streamlit Cloud** for the frontend (free tier)

## Prerequisites

1. GitHub repository with your code
2. Railway account (https://railway.app)
3. Streamlit Cloud account (https://share.streamlit.io)
4. External service accounts:
   - MongoDB Atlas (https://cloud.mongodb.com)
   - Redis Cloud (https://redis.io/cloud/)
   - Qdrant Cloud (https://cloud.qdrant.io)
   - MeshAPI key (https://meshapi.ai)

---

## Part 1: Backend Deployment (Railway)

### Step 1: Prepare Your Code

Your repository already has:
- ✅ `railway.json` - Railway configuration
- ✅ `Procfile` - Process configuration
- ✅ `requirements.txt` - Dependencies
- ✅ `app/` - FastAPI application

### Step 2: Create External Services

#### MongoDB Atlas (Database)

1. Go to https://cloud.mongodb.com
2. Sign up and create a cluster (M0 free tier)
3. Create a database user (username/password)
4. Add IP allowlist: `0.0.0.0/0` (or Railway IPs)
5. Get connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/storyalchemy?retryWrites=true&w=majority
   ```

#### Redis Cloud (Caching)

1. Go to https://redis.io/cloud/
2. Sign up (30MB free tier)
3. Create a subscription and database
4. Get connection details:
   ```
   redis://default:password@host.redis-cloud.com:port
   ```

#### Qdrant Cloud (Vector DB)

1. Go to https://cloud.qdrant.io
2. Sign up (free tier)
3. Create a cluster
4. Get URL and API key:
   ```
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your_key_here
   ```

### Step 3: Deploy to Railway

1. Go to https://railway.app and login
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your StoryAlchemy repository
5. Click "Deploy"

### Step 4: Add Environment Variables

In Railway dashboard, go to Variables and add:

```env
# LLM API
MESHAPI_API_KEY=your_meshapi_key
MESHAPI_BASE_URL=https://api.meshapi.ai/v1

# Databases
MONGODB_URL=mongodb+srv://...
REDIS_URL=redis://...
QDRANT_URL=https://...
QDRANT_API_KEY=your_key
QDRANT_COLLECTION=story_patterns

# App Settings
ENV=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-app.streamlit.app
ENABLE_SEMANTIC_CACHE=true
MAX_REQUESTS_PER_HOUR=100

# Models
DEFAULT_GENERATION_MODEL=openai/gpt-4o-mini
CHEAP_MODEL=openai/gpt-4o-mini
```

### Step 5: Get Backend URL

1. After deployment, Railway provides a URL like:
   ```
   https://storyalchemy-production.up.railway.app
   ```
2. Save this URL - you'll need it for the frontend

### Step 6: Verify Deployment

Test the health endpoint:
```bash
curl https://your-app.up.railway.app/health
```

Should return:
```json
{"status": "healthy", "services": {...}}
```

---

## Part 2: Frontend Deployment (Streamlit Cloud)

### Step 1: Prepare Frontend Code

Update `streamlit_app/app.py` to point to Railway backend:

```python
# Change this line at the top:
API_URL = os.getenv("FASTAPI_URL", "https://your-railway-url.up.railway.app/api/v1")
```

Or use environment variable in Streamlit Cloud.

### Step 2: Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select your repository
5. Set Main file path: `streamlit_app/app.py`
6. Click "Deploy"

### Step 3: Add Secrets (if needed)

In Streamlit Cloud dashboard:

1. Go to your app settings
2. Click "Secrets"
3. Add:
   ```toml
   FASTAPI_URL = "https://your-railway-url.up.railway.app/api/v1"
   ```

### Step 4: Update CORS

In Railway backend, update `CORS_ORIGINS`:
```
CORS_ORIGINS=https://your-app.streamlit.app,https://your-app.streamlit.cloud
```

---

## Part 3: Free Tier Limits

### Railway (Free Tier)
- $5 credit/month
- 512MB RAM
- 1GB disk
- Sleep after inactivity (wakes on request)

### Streamlit Cloud (Community)
- Unlimited public apps
- 1GB RAM
- Community support

### External Services (Free Tiers)
- **MongoDB Atlas**: 512MB storage
- **Redis Cloud**: 30MB RAM
- **Qdrant Cloud**: 1GB storage, 1M vectors
- **MeshAPI**: Pay-per-use (~$0.005 per story)

---

## Part 4: Post-Deployment Checklist

### Verify API Connectivity
```bash
curl https://backend-url.up.railway.app/api/v1/analytics/stats
```

### Test Story Generation
1. Open Streamlit app
2. Enter an idea
3. Click "Generate Story"
4. Verify story appears

### Test History
1. Generate a few stories
2. Navigate to History tab
3. Verify stories persist

### Test Knowledge Base
1. Upload a pattern
2. Verify it appears in "Your Uploaded Patterns"

---

## Troubleshooting

### CORS Errors
```
Add your Streamlit URL to Railway's CORS_ORIGINS
```

### Database Connection Fails
```
Check MONGODB_URL includes all parameters
Verify IP allowlist includes Railway IPs
```

### App Sleeps (Cold Start)
```
Railway free tier sleeps after 30 min
First request may take 10-30s to wake
```

### Vector Search Not Working
```
Check QDRANT_URL and QDRANT_API_KEY
Verify collection exists in Qdrant Cloud
```

---

## Monitoring

### Railway Dashboard
- Logs: View in real-time
- Metrics: CPU, memory, requests
- Deployments: Rollback if needed

### External Services
- MongoDB Atlas: Monitor queries and storage
- Redis Cloud: Check cache hit rates
- Qdrant Cloud: Monitor vector operations

---

## Cost Estimation

| Component | Free Tier | Paid (Optional) |
|-----------|-----------|----------------|
| Railway Backend | $5/mo credit | $5+/mo |
| Streamlit Cloud | Free | $0 (public apps) |
| MongoDB Atlas | 512MB | $9/mo (2GB) |
| Redis Cloud | 30MB | $7/mo (100MB) |
| Qdrant Cloud | 1GB | $0 (1GB free) |
| MeshAPI | Pay per use | ~$0.005/story |

**Typical Monthly Cost (Free Tier Only):**
- 100 stories: ~$0.50 (MeshAPI only)
- Infrastructure: $0

---

## Next Steps

1. **Custom Domain**: Add custom domain in Railway/Streamlit
2. **Monitoring**: Add Sentry for error tracking
3. **Analytics**: Add Google Analytics to frontend
4. **Backups**: Schedule MongoDB Atlas backups
5. **Scaling**: Upgrade Railway if needed

---

## Support

- Railway Docs: https://docs.railway.app
- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- MongoDB Atlas Docs: https://www.mongodb.com/docs/atlas/
- Qdrant Cloud Docs: https://qdrant.tech/documentation/cloud/
