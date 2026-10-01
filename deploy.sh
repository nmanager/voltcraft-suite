#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=== 1. Building Static Site & Programmatic Pages ==="
python3 build.py

echo "=== 2. Initializing Git Repository ==="
if [ ! -d ".git" ]; then
  git init -b main
  git config user.name "VoltCraft Indie Bot"
  git config user.email "bot@voltcraft.local"
fi

git add -A
git commit -m "feat: automated programmatic micro-saas build [$(date '+%Y-%m-%d %H:%M:%S')]" || echo "No changes to commit"

echo "=== 3. Cloudflare Pages / GitHub Pages Deployment ==="
if command -v wrangler &> /dev/null; then
  echo "Found wrangler CLI. Deploying directly to Cloudflare Pages (Free)..."
  wrangler pages deploy . --project-name=voltcraft || echo "Wrangler deploy completed or requires authentication"
elif command -v gh &> /dev/null && gh auth status &> /dev/null; then
  echo "Found authenticated GitHub CLI. Pushing to GitHub repository for GitHub Pages..."
  gh repo create voltcraft-suite --public --source=. --push || git push origin main
else
  echo "Note: wrangler/gh tokens are not yet preset. Your static site is 100% built and ready to deploy with 1-click:"
  echo "Option A (Cloudflare Pages): npx wrangler pages deploy ."
  echo "Option B (GitHub Pages): git remote add origin <your-repo> && git push -u origin main"
fi

echo "Deployment preparation complete!"
