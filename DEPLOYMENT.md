# Deployment Guide for Vercel

This guide will help you deploy the Stock Event AI application to Vercel.

## Prerequisites

1. A GitHub account
2. A Vercel account (sign up at https://vercel.com)
3. Your API keys ready:
   - `SUPER_MIND_API_KEY`
   - `POLYGON_API_KEY`
   - `OPENAI_API_KEY` (optional, for faster scoring)

## Step 1: Push to GitHub

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Stock Event AI application"
   ```

2. **Create a GitHub repository**:
   - Go to https://github.com/new
   - Create a new repository (e.g., `project_news_scanner_v1`)
   - Do NOT initialize with README, .gitignore, or license

3. **Push your code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy to Vercel

1. **Connect GitHub to Vercel**:
   - Log in to your Vercel account at https://vercel.com
   - Click "New Project" in your dashboard
   - Select "Import Git Repository"
   - Authorize Vercel to access your GitHub account if prompted
   - Select your repository (`project_news_scanner_v1`)

2. **Configure Project Settings**:
   - **Framework Preset**: Select "Other" or leave as auto-detected
   - **Root Directory**: Leave as `./` (root)
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

3. **Add Environment Variables**:
   Click "Environment Variables" and add:
   - `SUPER_MIND_API_KEY` = `your_supermind_api_key`
   - `POLYGON_API_KEY` = `your_polygon_api_key`
   - `OPENAI_API_KEY` = `your_openai_api_key` (optional)
   
   **Important**: Make sure to add these for all environments (Production, Preview, Development)

4. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be live at `https://your-project-name.vercel.app`

## Step 3: Verify Deployment

1. Visit your deployment URL
2. Check the `/api/health` endpoint: `https://your-project-name.vercel.app/api/health`
3. Test the main interface at the root URL

## Important Notes

### Background Monitoring
- The background monitoring service starts automatically when the app starts
- On Vercel's serverless functions, background tasks may have limitations
- Consider using Vercel Cron Jobs or external schedulers for production monitoring

### Environment Variables
- Never commit `.env` file to GitHub (already in `.gitignore`)
- Always set environment variables in Vercel dashboard
- Update environment variables if you change API keys

### Cold Starts
- Vercel serverless functions may experience cold starts
- First request after inactivity may take a few seconds
- Subsequent requests will be faster

### File System Limitations
- Vercel serverless functions have read-only file systems (except `/tmp`)
- The `background.md` file should be committed to the repository if needed
- Consider storing configuration in environment variables or a database

## Troubleshooting

### Build Failures
- Check that `requirements.txt` includes all dependencies
- Verify Python version compatibility (Vercel uses Python 3.11 by default)
- Check build logs in Vercel dashboard

### Runtime Errors
- Check function logs in Vercel dashboard
- Verify all environment variables are set correctly
- Ensure API keys are valid and have proper permissions

### API Errors
- Verify API keys are set in Vercel environment variables
- Check API rate limits
- Review error logs in Vercel dashboard

## Continuous Deployment

Vercel automatically deploys:
- **Production**: Every push to `main` branch
- **Preview**: Every pull request gets a preview deployment URL
- **Development**: Can be configured for other branches

## Updating the Application

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```
3. Vercel will automatically deploy the changes

## Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

