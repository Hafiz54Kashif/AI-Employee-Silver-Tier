# LinkedIn Setup Guide

## Step 1: Create LinkedIn Developer App

1. Go to: https://www.linkedin.com/developers/apps
2. Click "Create App"
3. Fill in:
   - App Name: AI Employee
   - LinkedIn Page: your company page (or create one)
   - App Logo: any image
4. Click "Create App"

## Step 2: Get Permissions

1. Go to your app → "Products" tab
2. Request access to: **Share on LinkedIn**
3. Go to "Auth" tab
4. Under OAuth 2.0 scopes, make sure these are added:
   - `openid`
   - `profile`
   - `w_member_social`

## Step 3: Get Access Token

1. Go to: https://www.linkedin.com/developers/tools/oauth/token-generator
2. Select your app
3. Check scopes: `openid`, `profile`, `w_member_social`
4. Click "Request access token"
5. Authorize the app
6. Copy the Access Token

## Step 4: Add Token to .env File

Create a `.env` file in your project root:

```
D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project\.env
```

Add this line:
```
LINKEDIN_ACCESS_TOKEN=your_access_token_here
```

## Step 5: Start LinkedIn Watcher

```bash
python watchers/linkedin_watcher.py
```

## How to Post on LinkedIn

Create a `.md` file in `vault/LinkedIn_Posts/`:

```markdown
Excited to share our latest AI Employee project!

We built an autonomous AI system that:
- Monitors Gmail automatically
- Processes tasks without human input
- Posts updates on LinkedIn

Built with Claude Code + Python + Obsidian

#AI #Automation #Innovation #Pakistan
```

The watcher will automatically post it to LinkedIn within 30 seconds!
