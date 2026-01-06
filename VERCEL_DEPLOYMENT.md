# Vercel Deployment Guide

## Current Setup

This project has both a Next.js frontend and a FastAPI backend. For Vercel deployment, you have two options:

## Option 1: Deploy as Separate Projects (RECOMMENDED)

### Step 1: Deploy Backend API

1. In Vercel, create a new project
2. Connect your GitHub repository
3. **Root Directory:** Leave as root (or set to project root)
4. **Framework Preset:** Other
5. **Build Command:** (leave empty)
6. **Output Directory:** (leave empty)
7. **Install Command:** (leave empty)

**Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key

**Important:** Make sure `vercel.json` only has the API configuration:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

After deployment, note your backend URL (e.g., `https://your-backend.vercel.app`)

### Step 2: Deploy Frontend

1. In Vercel, create another new project
2. Connect the same GitHub repository
3. **Root Directory:** `frontend`
4. **Framework Preset:** Next.js (auto-detected)
5. **Build Command:** `npm run build` (or leave default)
6. **Output Directory:** `.next` (or leave default)

**Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Your backend URL from Step 1 (e.g., `https://your-backend.vercel.app`)

The frontend will automatically build and deploy.

## Option 2: Deploy as Monorepo (Current Setup)

If you want everything in one project:

1. In Vercel project settings:
   - **Root Directory:** Leave as root
   - **Framework Preset:** Other
   - Vercel should auto-detect both Next.js and Python

2. **Environment Variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `NEXT_PUBLIC_API_URL`: Leave empty (will use relative paths)

3. Make sure `vercel.json` is configured correctly (already done)

4. **Important:** Vercel might need you to specify the build settings:
   - For Next.js: It should auto-detect
   - For Python: It should use the `vercel.json` configuration

## Troubleshooting 404 Errors

### If you get 404 on the root:

1. **Check Root Directory:**
   - Go to Vercel Project Settings → General
   - If frontend is in a subdirectory, you might need to set Root Directory to `frontend`

2. **Check Build Logs:**
   - Go to your deployment → Build Logs
   - See if Next.js is building correctly

3. **Check vercel.json:**
   - Make sure routes are configured correctly
   - Frontend routes should come after API routes

### If API endpoints return 404:

1. **Check API Routes:**
   - Test: `https://your-app.vercel.app/api/` (should return `{"status": "ok"}`)
   - If this fails, the Python build might have issues

2. **Check Runtime Logs:**
   - Go to deployment → Runtime Logs
   - Look for Python errors

3. **Verify Environment Variables:**
   - Make sure `OPENAI_API_KEY` is set
   - Check it's enabled for Production environment

## Quick Test After Deployment

1. **Test Backend:**
   ```bash
   curl https://your-app.vercel.app/api/
   # Should return: {"status":"ok"}
   ```

2. **Test Frontend:**
   - Visit: `https://your-app.vercel.app`
   - Should show the chat interface

3. **Test Full Flow:**
   - Send a message in the chat
   - Check browser console for any errors
   - Check Vercel Runtime Logs for API calls

## Recommended: Separate Projects

I recommend Option 1 (separate projects) because:
- ✅ Cleaner separation of concerns
- ✅ Independent scaling
- ✅ Easier debugging
- ✅ Better Vercel support
- ✅ Can update frontend/backend independently

