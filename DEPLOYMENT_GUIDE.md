# Sephira Orion - Deployment Guide

## Prerequisites

Before deploying, ensure you have:

1. **GitHub Account** - Repository created at https://github.com/akshatc0/sephiraorion
2. **Vercel Account** - Sign up at https://vercel.com (free)
3. **Railway Account** - Sign up at https://railway.app (free $5/month credits)
4. **API Keys Ready**:
   - OpenAI API Key (GPT-5.1 access)
   - Tavily API Key (web search)
   - News API Key (optional)
   - Alpha Vantage Key (optional)
   - FRED API Key (optional)

## Step-by-Step Deployment

### 1. Create GitHub Repository

**If not already created:**

1. Go to https://github.com/new
2. Repository name: `sephiraorion`
3. Keep it **Public** or **Private** (your choice)
4. **DO NOT** initialize with README (we already have one)
5. Click "Create repository"

### 2. Push Code to GitHub

The code is already committed locally. To push:

```bash
cd /Users/akshatchopra/Desktop/Desktop/sephira4
git push -u origin main
```

If the repository doesn't exist yet, create it first on GitHub, then run the push command above.

### 3. Deploy Backend to Railway

1. **Go to Railway**: https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authenticate with GitHub if needed
5. Select repository: **`akshatc0/sephiraorion`**
6. Railway will auto-detect Python and start building

**Configure Environment Variables:**

Click on your project → Variables → Add these:

```
OPENAI_API_KEY=sk-proj-... (your key)
TAVILY_API_KEY=tvly-dev-... (your key)
NEWS_API_KEY=290708200086459eb567181579f16f15
ALPHA_VANTAGE_KEY=X7P9W48CGST2JR9W
FRED_API_KEY=6eab1e52328b6e2cb2471f7f1e4ecef3
CHROMADB_PATH=./data/chroma
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_QUERIES_PER_MINUTE=10
MAX_QUERIES_PER_HOUR=100
MAX_RESPONSE_TOKENS=2000
```

**Get Your Backend URL:**

Once deployed, Railway will show you a URL like:
```
https://sephiraorion-production-XXXX.up.railway.app
```

Copy this URL - you'll need it for Vercel!

### 4. Deploy Frontend to Vercel

1. **Go to Vercel**: https://vercel.com
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repo: **`akshatc0/sephiraorion`**

**Configure Build Settings:**

- Framework Preset: **Next.js**
- Root Directory: **`frontend`**
- Build Command: `npm run build` (default)
- Output Directory: `.next` (default)
- Install Command: `npm install` (default)

**Add Environment Variables:**

Click "Environment Variables" and add:

```
NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
```

(Replace with your actual Railway backend URL from step 3)

4. Click **"Deploy"**

### 5. Update CORS (if needed)

After getting your Vercel URL (e.g., `https://sephiraorion.vercel.app`), you may need to update the CORS settings in the backend to specifically allow your domain.

The backend is already configured to allow all `.vercel.app` domains in production mode.

### 6. Initialize Data on Railway

The ChromaDB needs to be initialized with your sentiment data. Two options:

**Option A: Railway CLI** (Recommended)
```bash
# Install Railway CLI
brew install railway  # or npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run setup
railway run python setup.py
```

**Option B: Add Admin Endpoint**

Access the API docs at your Railway URL:
```
https://your-railway-url.railway.app/docs
```

If setup endpoint exists, trigger it there.

**Option C: Let it initialize on first query**

The system will initialize ChromaDB on the first query automatically, but this may timeout on the first request.

## Verification Steps

### 1. Test Backend

Visit: `https://your-railway-url.railway.app/docs`

You should see the Sephira Orion API documentation.

Test the health endpoint:
```
GET https://your-railway-url.railway.app/api/health
```

### 2. Test Frontend

Visit: `https://your-vercel-url.vercel.app`

You should see the Sephira Orion chat interface.

### 3. Test Chat Functionality

Type in the chat:
- "tell me about sentiment data from 2022"
- "What's happening in the world today?" (tests web search)
- "forecast Russia for 30 days" (tests predictions)

### 4. Monitor Logs

**Railway Logs:**
- Go to Railway dashboard → Your project → Logs
- Watch for any errors during requests

**Vercel Logs:**
- Go to Vercel dashboard → Your project → Logs
- Monitor frontend errors

## Troubleshooting

### Issue: "No response from server"

**Solution:**
1. Check Railway backend is running (visit `/docs` endpoint)
2. Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
3. Check Railway logs for errors
4. Ensure all environment variables are set in Railway

### Issue: "CORS error"

**Solution:**
1. Check backend logs on Railway
2. Verify CORS settings in `backend/api/main.py`
3. Ensure `ENVIRONMENT=production` is set in Railway

### Issue: "ChromaDB not initialized"

**Solution:**
1. Use Railway CLI to run `python setup.py`
2. Or wait for first query to initialize (may timeout first time)
3. Check Railway logs for initialization status

### Issue: Backend build fails on Railway

**Solution:**
1. Check Railway build logs
2. Ensure `requirements.txt` is in root directory
3. Verify Python version compatibility (Railway uses Python 3.11+)

### Issue: Frontend shows old data

**Solution:**
1. Clear browser cache
2. Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)
3. Check browser console for errors

## URLs

After deployment, you'll have:

- **Frontend**: `https://sephiraorion.vercel.app` (or custom domain)
- **Backend**: `https://sephiraorion-production-XXXX.up.railway.app`
- **API Docs**: `https://backend-url/docs`

## Custom Domain (Optional)

### For Vercel (Frontend):
1. Go to Vercel project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

### For Railway (Backend):
1. Railway supports custom domains on paid plans
2. Or use Vercel as reverse proxy (not recommended for API)

## Monitoring

### Railway Dashboard:
- View real-time logs
- Monitor CPU/Memory usage
- Track deployment history
- View metrics

### Vercel Dashboard:
- Analytics (page views, visitors)
- Build logs
- Deployment previews
- Performance insights

## Cost Management

### Railway Costs:
- Free: $5/month credit
- Typical usage: $3-8/month for this app
- Monitor usage in Railway dashboard

### Vercel Costs:
- Free tier: Unlimited bandwidth for hobby projects
- Upgrade if you exceed limits

### OpenAI Costs:
- GPT-5.1: ~$0.01-0.05 per query (depending on length)
- Monitor usage at https://platform.openai.com/usage

## Automatic Deployments

Both Vercel and Railway support automatic deployments:

- **Push to `main` branch** → Auto-deploys to production
- **Push to other branches** → Creates preview deployments (Vercel)
- **Pull Requests** → Automatic preview URLs (Vercel)

## Rollback

If something goes wrong:

**Vercel:**
1. Go to Deployments tab
2. Find previous working deployment
3. Click "..." → "Promote to Production"

**Railway:**
1. Go to Deployments tab
2. Click on previous deployment
3. Click "Redeploy"

## Security Checklist

- [ ] All API keys stored as environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] CORS configured for production domains only
- [ ] Rate limiting enabled
- [ ] HTTPS enforced (automatic on Vercel/Railway)
- [ ] Monitor logs for suspicious activity

## Backup Strategy

**Code:**
- Backed up on GitHub automatically
- Create tags for major releases: `git tag v1.0.0 && git push --tags`

**Data:**
- Railway persistent volume backs up ChromaDB automatically
- For critical data, export periodically via API
- CSV source file is in git repository

## Next Steps After Deployment

1. **Test thoroughly** - All features, edge cases
2. **Monitor costs** - Check Railway and OpenAI usage
3. **Set up alerts** - Configure Railway/Vercel notifications
4. **Custom domain** - Add professional domain if desired
5. **Analytics** - Set up user analytics if needed

## Support

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Issue Tracking**: Use GitHub Issues on your repository

---

**You're ready to deploy!** 🚀

Start with creating the GitHub repo (if not done), then follow Railway → Vercel → Test.
