# Vercel Deployment Guide

## Quick Deploy via Dashboard

### Step 1: Import Project
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"** or **"Import Project"**
3. Select your GitHub repository: `muhammedidris004/toyota-GR`

### Step 2: Configure Project
- **Framework Preset**: Next.js (auto-detected)
- **Root Directory**: `frontend` ⚠️ **IMPORTANT**
- **Build Command**: `npm run build` (auto)
- **Output Directory**: `.next` (auto)
- **Install Command**: `npm install` (auto)

### Step 3: Add Environment Variable
Click **"Environment Variables"** and add:
- **Key**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://toyota-gr.onrender.com`
- **Apply to**: Production, Preview, Development

### Step 4: Deploy
Click **"Deploy"** and wait for the build to complete.

## After Deployment

1. You'll receive a deployment URL (e.g., `https://toyota-gr-ai.vercel.app`)
2. Visit the URL to test your frontend
3. The frontend will automatically connect to the Render backend

## Troubleshooting

### If you see CORS errors:
1. Share your Vercel URL with the team
2. We'll add it to the backend CORS allow list

### If build fails:
- Check that Root Directory is set to `frontend`
- Verify `package.json` exists in `frontend/` folder
- Check build logs in Vercel dashboard

## CLI Deployment (Alternative)

If you prefer CLI:

```bash
cd frontend
npx vercel login
npx vercel --yes
```

Follow the prompts to link your project.

