# Vercel Deployment Setup Guide

## Issues Fixed

1. ✅ Changed model from "gpt-5" (doesn't exist) to "gpt-3.5-turbo"
2. ✅ Added Mangum for proper ASGI handling on Vercel
3. ✅ Updated vercel.json for proper serverless function routing
4. ✅ Updated requirements.txt with Mangum dependency

## Required Environment Variables

**CRITICAL:** You MUST set the `OPENAI_API_KEY` environment variable in Vercel:

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add a new environment variable:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key (starts with `sk-`)
   - **Environment:** Production, Preview, and Development (select all)
4. Click **Save**
5. **Redeploy** your application for the changes to take effect

## Deployment Steps

1. Make sure all changes are committed:
   ```bash
   git add .
   git commit -m "Fix Vercel deployment configuration"
   git push
   ```

2. Vercel will automatically redeploy, or you can trigger a new deployment from the dashboard

3. After deployment, check the **Runtime Logs** in Vercel to see if there are any errors

## Troubleshooting

### Serverless Function Crashes

If you still see crashes:

1. **Check Environment Variables:**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Verify `OPENAI_API_KEY` is set correctly
   - Make sure it's enabled for Production environment

2. **Check Runtime Logs:**
   - Go to your deployment → **Runtime Logs** tab
   - Look for error messages that indicate what's failing

3. **Common Issues:**
   - Missing `OPENAI_API_KEY` → Set it in Vercel environment variables
   - Invalid API key → Verify your key is correct
   - Quota exceeded → Check your OpenAI account billing
   - Model not found → Should be fixed (changed to gpt-3.5-turbo)

### Testing the API

After deployment, test the API endpoint:
```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Frontend Configuration

Make sure your frontend is configured to point to the deployed backend:

1. In `frontend/.env.local` or Vercel environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.vercel.app
   ```

2. Or update `frontend/lib/api.ts` to use the deployed URL in production.

