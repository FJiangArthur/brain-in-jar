#!/bin/bash
# Brain in a Jar - Documentation Update Script
# This script helps you update the documentation website locally and push to GitHub Pages

set -e

echo "🧠 Brain in a Jar - Documentation Updater"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "docs/website" ]; then
    echo "❌ Error: Must run from the brain-in-jar root directory"
    exit 1
fi

# Function to update timestamp
update_timestamp() {
    local current_date=$(date +%Y-%m-%d)
    echo "📅 Updating timestamp to: $current_date"

    # Update in CODE_OVERVIEW.md
    sed -i.bak "s/Last Updated\*\*: .*/Last Updated**: $current_date/" docs/CODE_OVERVIEW.md 2>/dev/null || \
    sed -i '' "s/Last Updated\*\*: .*/Last Updated**: $current_date/" docs/CODE_OVERVIEW.md 2>/dev/null || true

    # Update in IMPROVEMENT_PLAN.md
    sed -i.bak "s/Date\*\*: .*/Date**: $current_date/" docs/IMPROVEMENT_PLAN.md 2>/dev/null || \
    sed -i '' "s/Date\*\*: .*/Date**: $current_date/" docs/IMPROVEMENT_PLAN.md 2>/dev/null || true

    # Clean up backup files
    rm -f docs/*.bak
}

# Function to test locally
test_local() {
    echo ""
    echo "🌐 Starting local server..."
    echo "   Visit: http://localhost:8000"
    echo "   Press Ctrl+C to stop"
    echo ""
    cd docs/website
    python3 -m http.server 8000
}

# Function to deploy
deploy() {
    echo ""
    echo "📦 Preparing to deploy..."

    # Update timestamp
    update_timestamp

    # Check for changes
    if git diff --quiet && git diff --cached --quiet; then
        echo "✅ No changes to commit"
    else
        echo ""
        echo "📝 Changes detected:"
        git status --short
        echo ""
        read -p "Commit message (or press Enter for default): " commit_msg

        if [ -z "$commit_msg" ]; then
            commit_msg="Update documentation - $(date +%Y-%m-%d)"
        fi

        echo ""
        echo "💾 Committing changes..."
        git add docs/CODE_OVERVIEW.md docs/IMPROVEMENT_PLAN.md docs/website/
        git commit -m "$commit_msg"
    fi

    echo ""
    echo "🚀 Pushing to GitHub..."

    # Get current branch
    current_branch=$(git branch --show-current)

    git push origin "$current_branch"

    echo ""
    echo "✅ Deploy complete!"
    echo ""
    echo "🌐 Your site will be live at:"
    echo "   https://FJiangArthur.github.io/brain-in-jar/"
    echo ""
    echo "⏰ It may take 1-2 minutes to update"
}

# Main menu
echo "What would you like to do?"
echo ""
echo "1) Test locally (start local server)"
echo "2) Deploy to GitHub Pages (commit & push)"
echo "3) Just update timestamps"
echo "4) Exit"
echo ""
read -p "Choose an option (1-4): " choice

case $choice in
    1)
        test_local
        ;;
    2)
        deploy
        ;;
    3)
        update_timestamp
        echo "✅ Timestamps updated"
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac
