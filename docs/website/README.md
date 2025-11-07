# Brain in a Jar - Documentation Website

This directory contains the web-based documentation dashboard for the Brain in a Jar project.

## Features

- **Interactive Documentation**: Browse code overview and improvement plans with a cyberpunk-themed interface
- **Real-time Updates**: Content is loaded dynamically from markdown files
- **Syntax Highlighting**: Code blocks are highlighted for better readability
- **Responsive Design**: Works on desktop and mobile devices
- **Accessibility**: Keyboard navigation and screen reader support

## Structure

```
website/
├── index.html      # Main dashboard page
├── style.css       # Cyberpunk-themed styles
├── script.js       # Dashboard functionality
└── README.md       # This file
```

## Usage

### Local Development

Open `index.html` in a web browser:

```bash
# From the website directory
open index.html

# Or use a simple HTTP server
python -m http.server 8000
# Then visit http://localhost:8000
```

### GitHub Pages

This website is designed to be hosted on GitHub Pages:

1. Enable GitHub Pages in repository settings
2. Set source to `/docs` directory
3. Access at: `https://[username].github.io/brain-in-jar/website/`

## Features

### Navigation Tabs

- **Code Overview**: Comprehensive overview of the codebase structure
- **Improvement Plan**: Detailed improvement roadmap with priorities
- **Statistics**: Visual statistics and project metrics

### Easter Eggs

- **Konami Code**: Try entering ↑ ↑ ↓ ↓ ← → ← → B A for a surprise
- **Random Glitch**: Watch for glitch effects on headings

### Customization

Edit CSS variables in `style.css` to customize the theme:

```css
:root {
    --bg-primary: #0a0a0a;
    --text-primary: #00ff41;
    --accent-pink: #ff00ff;
    /* ... more variables */
}
```

## Dependencies

- [Marked.js](https://marked.js.org/) - Markdown parser (v11.0.0+)
- [Highlight.js](https://highlightjs.org/) - Syntax highlighting (v11.9.0+)

Both are loaded via CDN in `index.html`.

## Browser Support

- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- Mobile browsers: ✅ Responsive design

## Performance

- Lazy loading of markdown content
- Minimal external dependencies
- Optimized for fast initial load
- Auto-refresh every 5 minutes

## Accessibility

- Semantic HTML structure
- ARIA labels where appropriate
- Keyboard navigation support
- Reduced motion support for accessibility preferences

## License

Part of the Brain in a Jar project. Open source.
