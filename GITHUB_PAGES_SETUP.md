# GitHub Pages Setup Guide

This guide explains how to deploy the Brain in a Jar documentation website to GitHub Pages.

## Overview

The project now includes a beautiful cyberpunk-themed documentation website located in `docs/website/`. This website displays:

- **Code Overview**: Comprehensive codebase structure and architecture
- **Improvement Plan**: Detailed roadmap for future enhancements
- **Statistics**: Visual metrics and project stats

## Quick Setup

### Option 1: Automatic Deployment (Recommended)

The repository includes a GitHub Actions workflow that automatically deploys the website.

1. **Enable GitHub Actions**:
   - Go to your repository settings
   - Navigate to "Actions" → "General"
   - Enable "Read and write permissions" for workflows

2. **Enable GitHub Pages**:
   - Go to repository Settings
   - Navigate to "Pages" (in the left sidebar)
   - Under "Build and deployment":
     - Source: Select "GitHub Actions"
   - Save changes

3. **Trigger Deployment**:
   - Push any commit to the `main` or `claude/*` branches
   - Or manually trigger the workflow from Actions tab

4. **Access Your Site**:
   - After deployment completes (1-2 minutes)
   - Visit: `https://[your-username].github.io/brain-in-jar/`

### Option 2: Manual Setup

If you prefer not to use GitHub Actions:

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Under "Build and deployment":
     - Source: Select "Deploy from a branch"
     - Branch: Select `main` (or your default branch)
     - Folder: Select `/docs/website`
   - Save changes

2. **Access Your Site**:
   - Wait 1-2 minutes for deployment
   - Visit: `https://[your-username].github.io/brain-in-jar/`

## Verifying Deployment

1. **Check Actions Tab**:
   - Go to the "Actions" tab in your repository
   - Look for "Deploy GitHub Pages" workflow
   - Ensure it shows a green checkmark ✅

2. **Check Deployment Status**:
   - Go to Settings → Pages
   - You should see "Your site is live at [URL]"

3. **Test the Website**:
   - Click the provided URL
   - You should see the cyberpunk-themed dashboard
   - Try switching between tabs (Code Overview, Improvement Plan, Statistics)

## Troubleshooting

### Site Not Loading

**Issue**: 404 error when accessing the site

**Solution**:
1. Check that GitHub Pages is enabled in Settings → Pages
2. Verify the correct branch and folder are selected
3. Wait 5-10 minutes for initial deployment
4. Clear browser cache and retry

### Content Not Displaying

**Issue**: Website loads but markdown content shows "Error Loading Content"

**Solution**:
1. Check that `docs/CODE_OVERVIEW.md` and `docs/IMPROVEMENT_PLAN.md` exist
2. Verify file paths in `script.js` (relative paths: `../CODE_OVERVIEW.md`)
3. Check browser console for CORS errors
4. Ensure files are committed to the repository

### GitHub Actions Failing

**Issue**: Workflow shows red X ❌

**Solution**:
1. Check workflow logs in Actions tab
2. Verify Pages is enabled in Settings
3. Ensure workflow has proper permissions
4. Try re-running the workflow

### Styling Issues

**Issue**: Website loads but looks broken

**Solution**:
1. Check that `style.css` is loading (browser DevTools → Network tab)
2. Verify CDN links for Marked.js and Highlight.js are accessible
3. Clear browser cache
4. Try different browser

## Updating the Website

### Automatic Updates

When using GitHub Actions, the website automatically updates when you:
- Push changes to `main` or `claude/*` branches
- Update any files in `docs/website/`
- Update markdown files in `docs/`

### Manual Updates

If using manual deployment:
1. Make changes to files in `docs/website/` or `docs/`
2. Commit and push to your repository
3. Wait 1-2 minutes for GitHub Pages to rebuild
4. Refresh the website in your browser

## Customization

### Changing Colors

Edit `docs/website/style.css`:

```css
:root {
    --bg-primary: #0a0a0a;        /* Background color */
    --text-primary: #00ff41;      /* Main text color */
    --accent-pink: #ff00ff;       /* Accent color 1 */
    --accent-cyan: #00ffff;       /* Accent color 2 */
}
```

### Adding Content

1. **New Documentation Files**:
   - Create markdown files in `docs/`
   - Update `script.js` to load them:
   ```javascript
   await this.loadMarkdown('../YOUR_FILE.md', 'content-id', 'tab-id');
   ```

2. **New Tabs**:
   - Add tab button in `index.html`:
   ```html
   <button class="tab-button" data-tab="newtab">New Tab</button>
   ```
   - Add corresponding content div
   - Update JavaScript to handle the new tab

### Modifying Statistics

Edit the statistics in `docs/website/index.html`:

```html
<div class="stat-item">
    <span class="stat-label">Your Metric</span>
    <span class="stat-value">Value</span>
</div>
```

## Performance Optimization

The website is already optimized, but you can further improve it:

1. **Enable Compression**:
   - GitHub Pages automatically serves gzip compressed files

2. **Use Service Worker** (Advanced):
   - Uncomment service worker registration in `script.js`
   - Create `sw.js` for offline caching

3. **Minify Assets**:
   - Minify `style.css` and `script.js` for production
   - Use tools like `cssnano` or `terser`

## Custom Domain (Optional)

To use a custom domain:

1. **Add CNAME File**:
   ```bash
   echo "yourdomain.com" > docs/website/CNAME
   ```

2. **Configure DNS**:
   - Add CNAME record pointing to `[username].github.io`
   - Or A records pointing to GitHub Pages IPs:
     - 185.199.108.153
     - 185.199.109.153
     - 185.199.110.153
     - 185.199.111.153

3. **Update GitHub Settings**:
   - Settings → Pages → Custom domain
   - Enter your domain and save
   - Enable "Enforce HTTPS"

## Security

### HTTPS

GitHub Pages provides free HTTPS for all sites:
- Automatically enabled for `*.github.io` domains
- Available for custom domains (after DNS verification)

### Content Security

The website only:
- Loads markdown from the same repository
- Uses CDN resources (Marked.js, Highlight.js) via HTTPS
- Doesn't collect or transmit user data
- No backend or database

## Analytics (Optional)

To track visitors:

1. **Google Analytics**:
   - Add tracking code to `index.html` before `</head>`:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
   ```

2. **GitHub Traffic**:
   - View basic traffic stats in Insights → Traffic

## Support

If you encounter issues:

1. Check this troubleshooting guide first
2. Review GitHub Pages documentation: https://docs.github.com/pages
3. Check Actions workflow logs for error details
4. Verify all files are committed and pushed

## Resources

- [GitHub Pages Documentation](https://docs.github.com/pages)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Marked.js Documentation](https://marked.js.org/)
- [Highlight.js Documentation](https://highlightjs.org/)

## Example Sites

Once deployed, your site will look like this:

```
https://[username].github.io/brain-in-jar/
├── Code Overview Tab    (Full codebase documentation)
├── Improvement Plan Tab (Detailed enhancement roadmap)
└── Statistics Tab       (Visual project metrics)
```

---

**Need help?** Open an issue in the repository with the label "documentation" or "github-pages".
