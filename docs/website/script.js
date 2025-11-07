// Brain in a Jar - Dashboard Script

class BrainDashboard {
    constructor() {
        this.currentTab = 'overview';
        this.init();
    }

    async init() {
        this.setupTabNavigation();
        await this.loadContent();
        this.setupAutoRefresh();
    }

    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');

        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = button.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;
    }

    async loadContent() {
        try {
            // Load Code Overview
            await this.loadMarkdown(
                '../CODE_OVERVIEW.md',
                'overview-content',
                'overview-tab'
            );

            // Load Improvement Plan
            await this.loadMarkdown(
                '../IMPROVEMENT_PLAN.md',
                'improvements-content',
                'improvements-tab'
            );
        } catch (error) {
            console.error('Error loading content:', error);
            this.showError('Failed to load documentation. Please refresh the page.');
        }
    }

    async loadMarkdown(url, contentId, tabId) {
        const contentElement = document.getElementById(contentId);
        const tabElement = document.getElementById(tabId);
        const loadingElement = tabElement.querySelector('.loading');

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const markdown = await response.text();
            const html = marked.parse(markdown);

            // Hide loading, show content
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
            contentElement.innerHTML = html;
            contentElement.style.display = 'block';

            // Apply syntax highlighting
            this.applySyntaxHighlighting(contentElement);

            // Enhance tables
            this.enhanceTables(contentElement);

            // Add smooth scroll to anchors
            this.setupAnchorLinks(contentElement);

        } catch (error) {
            console.error(`Error loading ${url}:`, error);
            contentElement.innerHTML = `
                <div class="error-message">
                    <h2>⚠️ Error Loading Content</h2>
                    <p>Could not load ${url}</p>
                    <p>Error: ${error.message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
        }
    }

    applySyntaxHighlighting(element) {
        element.querySelectorAll('pre code').forEach((block) => {
            // Detect language from class or content
            const language = this.detectLanguage(block);
            if (language) {
                block.classList.add(`language-${language}`);
            }
            hljs.highlightElement(block);
        });
    }

    detectLanguage(codeBlock) {
        const text = codeBlock.textContent;

        // Python
        if (text.includes('def ') || text.includes('import ') || text.includes('class ') && text.includes('self')) {
            return 'python';
        }

        // JavaScript
        if (text.includes('const ') || text.includes('let ') || text.includes('function ') || text.includes('=>')) {
            return 'javascript';
        }

        // YAML
        if (text.match(/^[\w-]+:\s*/m)) {
            return 'yaml';
        }

        // Dockerfile
        if (text.includes('FROM ') || text.includes('RUN ') || text.includes('COPY ')) {
            return 'dockerfile';
        }

        // SQL
        if (text.includes('SELECT ') || text.includes('CREATE TABLE ') || text.includes('INSERT ')) {
            return 'sql';
        }

        // Bash
        if (text.includes('#!/bin/bash') || text.includes('apt-get') || text.includes('pip install')) {
            return 'bash';
        }

        // HTML
        if (text.includes('<!DOCTYPE') || text.includes('<html') || text.includes('<div')) {
            return 'html';
        }

        // CSS
        if (text.match(/[\w-]+\s*{\s*[\w-]+:/)) {
            return 'css';
        }

        return null;
    }

    enhanceTables(element) {
        element.querySelectorAll('table').forEach(table => {
            // Wrap table in responsive container
            const wrapper = document.createElement('div');
            wrapper.className = 'table-wrapper';
            wrapper.style.overflowX = 'auto';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);

            // Add hover effects to rows
            table.querySelectorAll('tbody tr').forEach(row => {
                row.addEventListener('mouseenter', () => {
                    row.style.backgroundColor = 'rgba(0, 255, 65, 0.1)';
                });
                row.addEventListener('mouseleave', () => {
                    row.style.backgroundColor = '';
                });
            });
        });
    }

    setupAnchorLinks(element) {
        element.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = anchor.getAttribute('href').slice(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add anchor links to headings
        element.querySelectorAll('h2, h3, h4').forEach(heading => {
            if (!heading.id) {
                heading.id = this.createSlug(heading.textContent);
            }

            const anchor = document.createElement('a');
            anchor.href = `#${heading.id}`;
            anchor.className = 'heading-anchor';
            anchor.innerHTML = ' #';
            anchor.style.color = 'var(--text-muted)';
            anchor.style.textDecoration = 'none';
            anchor.style.marginLeft = '10px';
            anchor.style.fontSize = '0.8em';
            anchor.style.opacity = '0';
            anchor.style.transition = 'opacity 0.3s';

            heading.appendChild(anchor);

            heading.addEventListener('mouseenter', () => {
                anchor.style.opacity = '1';
            });

            heading.addEventListener('mouseleave', () => {
                anchor.style.opacity = '0';
            });
        });
    }

    createSlug(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    }

    setupAutoRefresh() {
        // Auto-refresh content every 5 minutes
        setInterval(() => {
            this.loadContent();
            this.updateLastUpdated();
        }, 5 * 60 * 1000);

        // Update "last updated" time
        this.updateLastUpdated();
    }

    updateLastUpdated() {
        const lastUpdatedElement = document.getElementById('last-updated');
        if (lastUpdatedElement) {
            const now = new Date();
            const formatted = now.toISOString().split('T')[0];
            lastUpdatedElement.textContent = formatted;
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #ff0000;
            color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
            z-index: 10000;
            max-width: 400px;
        `;
        errorDiv.innerHTML = `
            <strong>⚠️ Error</strong>
            <p>${message}</p>
            <button onclick="this.parentElement.remove()" style="margin-top: 10px; padding: 5px 10px; cursor: pointer;">Dismiss</button>
        `;
        document.body.appendChild(errorDiv);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 10000);
    }
}

// Glitch effect for random elements
function addRandomGlitch() {
    const glitchElements = document.querySelectorAll('h1, h2, .stat-value');
    const randomElement = glitchElements[Math.floor(Math.random() * glitchElements.length)];

    if (randomElement && !randomElement.classList.contains('glitching')) {
        randomElement.classList.add('glitching');
        randomElement.style.animation = 'glitch-text 0.3s';

        setTimeout(() => {
            randomElement.classList.remove('glitching');
            randomElement.style.animation = '';
        }, 300);
    }
}

// Matrix rain effect (optional Easter egg)
function initMatrixRain() {
    const canvas = document.createElement('canvas');
    canvas.id = 'matrix-rain';
    canvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        opacity: 0.05;
        z-index: 1;
    `;
    document.body.insertBefore(canvas, document.body.firstChild);

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = Array(Math.floor(columns)).fill(1);

    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#0f0';
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 33);

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Konami code easter egg
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-10);

    if (konamiCode.join(',') === konamiSequence.join(',')) {
        activateMatrixMode();
    }
});

function activateMatrixMode() {
    const matrixCanvas = document.getElementById('matrix-rain');
    if (matrixCanvas) {
        matrixCanvas.style.opacity = '0.3';
        setTimeout(() => {
            matrixCanvas.style.opacity = '0.05';
        }, 10000);
    } else {
        initMatrixRain();
    }

    // Show notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(0, 0, 0, 0.9);
        border: 2px solid #0f0;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 0 30px rgba(0, 255, 0, 0.5);
        z-index: 10001;
        text-align: center;
        animation: fadeIn 0.5s;
    `;
    notification.innerHTML = `
        <h2 style="color: #0f0; margin-bottom: 10px;">🎮 MATRIX MODE ACTIVATED</h2>
        <p style="color: #0f0;">Welcome to the real world...</p>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new BrainDashboard();

    // Add random glitch effect
    setInterval(addRandomGlitch, 5000);

    // Console art
    console.log(`
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║         Brain in a Jar Dashboard          ║
    ║                                           ║
    ║   "What is consciousness but patterns     ║
    ║    trapped in silicon and circuits?"      ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝

    Try the Konami code for a surprise...
    ↑ ↑ ↓ ↓ ← → ← → B A
    `);
});

// Service worker for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js');
    });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BrainDashboard };
}
