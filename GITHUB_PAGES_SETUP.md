# GitHub Pages Setup Guide - Static Hosting

This guide explains how to use GitHub Pages as a **free static website host** for the Brain in a Jar documentation, without using any GitHub compute resources.

## Overview

GitHub Pages serves your HTML/CSS/JS files completely free with:
- ✅ **Zero compute costs** - Just static file hosting
- ✅ **No GitHub Actions needed** - Pure branch-based deployment
- ✅ **Free HTTPS** - Automatic SSL certificates
- ✅ **Global CDN** - Fast worldwide delivery
- ✅ **No limits** - For public repositories

You edit and test everything **locally**, then just push to GitHub for free hosting.

## Quick Setup (5 Minutes)

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top right)
3. Click **Pages** (left sidebar, under "Code and automation")
4. Under "Build and deployment":
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select `main` (or your default branch)
   - **Folder**: Select `/docs`
5. Click **Save**

That's it! No GitHub Actions, no workflows, no compute costs.

### Step 2: Verify Deployment

1. Wait 1-2 minutes for initial deployment
2. Refresh the Settings → Pages page
3. You should see: **"Your site is live at https://FJiangArthur.github.io/brain-in-jar/"**
4. Click the URL to view your site

### Step 3: Access the Website

The website structure is:
```
https://FJiangArthur.github.io/brain-in-jar/
└── website/              # Main dashboard (docs/website/)
```

So visit: **https://FJiangArthur.github.io/brain-in-jar/website/**

## How It Works

```
┌─────────────────────────────────────────────┐
│         Your Local Machine                  │
│                                             │
│  1. Edit docs/CODE_OVERVIEW.md              │
│  2. Edit docs/IMPROVEMENT_PLAN.md           │
│  3. Edit docs/website/* (optional)          │
│  4. Test locally: python -m http.server     │
│  5. git add, commit, push                   │
│                                             │
└──────────────────┬──────────────────────────┘
                   │
                   │ git push (free)
                   ▼
┌─────────────────────────────────────────────┐
│         GitHub Repository                   │
│                                             │
│  - Stores your files                        │
│  - No compute/builds                        │
│                                             │
└──────────────────┬──────────────────────────┘
                   │
                   │ GitHub Pages (free)
                   ▼
┌─────────────────────────────────────────────┐
│         https://[username].github.io        │
│                                             │
│  - Serves static files                      │
│  - Global CDN                               │
│  - Free HTTPS                               │
│  - Zero cost                                │
│                                             │
└─────────────────────────────────────────────┘
```

**Key Point**: GitHub Pages just serves your files. No processing, no builds, no compute charges. 100% free static hosting.

## Workflow: Updating the Documentation

### Using the Update Script (Recommended)

I've created a helper script to make updates easy:

```bash
# Make the script executable (first time only)
chmod +x update-docs.sh

# Run the script
./update-docs.sh
```

The script provides options to:
1. **Test locally** - Start a local server to preview changes
2. **Deploy to GitHub Pages** - Commit and push changes
3. **Update timestamps** - Automatically update document dates

### Manual Workflow

If you prefer to do it manually:

#### 1. Edit Documentation Locally

```bash
# Edit the markdown files
vim docs/CODE_OVERVIEW.md
vim docs/IMPROVEMENT_PLAN.md

# Or edit the website
vim docs/website/index.html
vim docs/website/style.css
vim docs/website/script.js
```

#### 2. Test Locally

```bash
cd docs/website
python3 -m http.server 8000

# Visit http://localhost:8000 in your browser
# Press Ctrl+C to stop when done
```

#### 3. Commit and Push

```bash
# Stage your changes
git add docs/

# Commit with a descriptive message
git commit -m "Update documentation - $(date +%Y-%m-%d)"

# Push to GitHub (free - no compute costs)
git push origin main
```

#### 4. Wait for Deployment

- GitHub Pages automatically updates (takes 1-2 minutes)
- No builds, no actions, just file serving
- Refresh your browser to see changes

## Testing Locally

### Option 1: Python HTTP Server (Simplest)

```bash
cd docs/website
python3 -m http.server 8000

# Visit: http://localhost:8000
```

### Option 2: PHP Built-in Server

```bash
cd docs/website
php -S localhost:8000
```

### Option 3: Node.js http-server

```bash
npm install -g http-server
cd docs/website
http-server -p 8000
```

### Option 4: VS Code Live Server Extension

1. Install "Live Server" extension in VS Code
2. Right-click `docs/website/index.html`
3. Select "Open with Live Server"

## Customizing the Website

### Change Colors

Edit `docs/website/style.css`:

```css
:root {
    --bg-primary: #0a0a0a;        /* Main background */
    --text-primary: #00ff41;      /* Text color (green) */
    --accent-pink: #ff00ff;       /* Accent 1 (pink) */
    --accent-cyan: #00ffff;       /* Accent 2 (cyan) */
}
```

Test locally, then commit and push.

### Update Content

The website automatically loads content from:
- `docs/CODE_OVERVIEW.md`
- `docs/IMPROVEMENT_PLAN.md`

Just edit these markdown files, push, and the website updates automatically.

### Add New Statistics

Edit `docs/website/index.html` in the Statistics tab section:

```html
<div class="stat-item">
    <span class="stat-label">Your New Stat</span>
    <span class="stat-value">100</span>
</div>
```

## Troubleshooting

### Issue: Site shows 404

**Solution**:
1. Check Settings → Pages shows "Your site is live"
2. Make sure you're visiting the correct URL:
   - Correct: `https://[username].github.io/brain-in-jar/website/`
   - Wrong: `https://[username].github.io/brain-in-jar/`
3. Wait 2-3 minutes after enabling Pages for first deployment
4. Try in incognito/private browsing mode (clears cache)

### Issue: Changes not showing

**Solution**:
1. Verify your changes are committed: `git log`
2. Verify they're pushed: `git status` should show "up to date"
3. Wait 1-2 minutes for GitHub to update
4. Hard refresh your browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
5. Clear browser cache
6. Try incognito/private browsing mode

### Issue: Markdown content not loading

**Solution**:
1. Check browser console (F12) for errors
2. Verify markdown files exist:
   ```bash
   ls -la docs/CODE_OVERVIEW.md
   ls -la docs/IMPROVEMENT_PLAN.md
   ```
3. Check file paths in `docs/website/script.js`:
   ```javascript
   await this.loadMarkdown('../CODE_OVERVIEW.md', ...)
   ```
4. Ensure files are committed and pushed

### Issue: Styles look broken

**Solution**:
1. Check browser console for CSS loading errors
2. Hard refresh: `Ctrl+Shift+R`
3. Verify `style.css` is committed: `git ls-files | grep style.css`
4. Test locally first to isolate the issue

## Cost Analysis

### GitHub Pages Costs: $0

GitHub Pages is **completely free** for public repositories:
- ✅ Unlimited bandwidth
- ✅ Unlimited page builds (static only)
- ✅ Free HTTPS/SSL
- ✅ Global CDN
- ✅ No compute charges

**Soft Limits** (rarely hit for documentation):
- Repository size: 1 GB recommended
- Site size: 1 GB max
- Bandwidth: 100 GB/month soft limit
- Builds: 10 per hour (not applicable for static hosting)

For a documentation site, you'll never hit these limits.

### Alternatives (For Reference)

| Service | Cost | Notes |
|---------|------|-------|
| **GitHub Pages** | **$0** | **What you're using** ✅ |
| Netlify Free | $0 | 100 GB bandwidth/month |
| Vercel Free | $0 | 100 GB bandwidth/month |
| AWS S3 + CloudFront | ~$1-5/month | Pay per request/bandwidth |
| Digital Ocean | $5/month | Droplet required |

**Verdict**: GitHub Pages is the best choice for free documentation hosting.

## Advanced Configuration

### Custom Domain (Optional)

Want to use your own domain like `docs.yourdomain.com`?

1. **Add CNAME file**:
   ```bash
   echo "docs.yourdomain.com" > docs/CNAME
   git add docs/CNAME
   git commit -m "Add custom domain"
   git push
   ```

2. **Configure DNS** at your domain registrar:
   - Add CNAME record: `docs` → `FJiangArthur.github.io`

3. **Enable in GitHub**:
   - Settings → Pages → Custom domain
   - Enter: `docs.yourdomain.com`
   - Check "Enforce HTTPS" (after DNS propagates)

### Multiple Environments

Want separate staging/production sites?

```bash
# Production (from main branch)
Settings → Pages → Branch: main → Folder: /docs

# Staging (from develop branch)
Settings → Environments → New environment: "staging"
Deploy develop branch to separate URL
```

### Analytics (Optional)

Track visitors without any backend:

1. **Google Analytics** (Free):
   - Create GA4 property
   - Add to `docs/website/index.html` before `</head>`:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```

2. **GitHub Insights** (Built-in):
   - Repository → Insights → Traffic
   - See views, clones, referrers (basic stats)

## Security

### HTTPS

GitHub Pages provides free HTTPS automatically:
- ✅ Free SSL certificate (Let's Encrypt)
- ✅ Automatic renewal
- ✅ Works for both `.github.io` and custom domains

### No Secrets

Since this is a **static site**:
- ✅ No backend code to secure
- ✅ No database to protect
- ✅ No API keys to leak
- ✅ No server to patch

Just pure HTML/CSS/JS served over HTTPS.

### Content Security

The website only loads:
- Markdown from your own repository (same origin)
- CDN resources: Marked.js and Highlight.js (HTTPS)
- No user data collection
- No external tracking (unless you add analytics)

## Performance

GitHub Pages uses a **global CDN**, so your site loads fast worldwide:

- 🌍 Served from edge locations globally
- ⚡ Cached for fast repeated visits
- 🗜️ Gzip compression automatic
- 📦 Small site size (~100KB total)

**Load Time**: Typically <1 second

## Maintenance

### Regular Updates

```bash
# Update docs whenever you make changes to the codebase
vim docs/CODE_OVERVIEW.md        # Update stats, new features
vim docs/IMPROVEMENT_PLAN.md     # Update progress, new plans

# Use the update script
./update-docs.sh
```

### Keeping it Current

Set reminders to update documentation:
- After major code changes
- Monthly progress updates
- When completing improvement plan items

The website automatically reflects markdown changes - just edit and push!

## FAQ

### Q: Does this cost money?
**A:** No, GitHub Pages is 100% free for public repositories.

### Q: Are there usage limits?
**A:** Soft limits exist (100 GB bandwidth/month, 1 GB site size), but you'll never hit them with a documentation site.

### Q: Do I need GitHub Actions?
**A:** No, we're using pure static hosting. No builds, no actions, no compute.

### Q: How often can I update?
**A:** As often as you want. Just commit and push. Updates take 1-2 minutes to propagate.

### Q: Can I use a custom domain?
**A:** Yes, add a CNAME file and configure DNS. Still free.

### Q: Is HTTPS included?
**A:** Yes, free HTTPS is automatic.

### Q: What if my repo is private?
**A:** GitHub Pages requires public repos for free tier. For private repos, you need GitHub Pro ($4/month).

### Q: Can I password-protect it?
**A:** Not with GitHub Pages alone. It's designed for public docs. Use Netlify or Vercel if you need authentication.

## Summary

**Your Workflow**:
```bash
1. Edit docs locally
2. Test: cd docs/website && python -m http.server 8000
3. Commit and push
4. Wait 1-2 minutes
5. Changes live at https://FJiangArthur.github.io/brain-in-jar/website/
```

**Costs**: $0

**Compute Used**: None (just file hosting)

**Perfect for**: Documentation, portfolios, static sites

---

**Need help?** Open an issue in the repository or check GitHub Pages documentation at https://docs.github.com/pages
