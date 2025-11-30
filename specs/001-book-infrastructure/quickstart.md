# Quickstart Guide: Book Infrastructure Development

**Feature**: 001-book-infrastructure
**Date**: 2025-11-30
**For**: Developers and Content Authors

## Overview

This guide helps you set up, run, and contribute to the Physical AI & Humanoid Robotics textbook infrastructure built with Docusaurus.

## Prerequisites

### Required
- **Node.js**: 18.x or later (LTS recommended)
- **npm**: 9.x or later (comes with Node.js)
- **Git**: 2.x or later

### Recommended
- **VS Code** with extensions:
  - `davidanson.vscode-markdownlint` - Markdown linting
  - `yzhang.markdown-all-in-one` - Markdown productivity
  - `esbenp.prettier-vscode` - Code formatting

### Check Your Environment

```bash
node --version   # Should be v18.x or higher
npm --version    # Should be 9.x or higher
git --version    # Should be 2.x or higher
```

## Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd book-generation

# Navigate to book directory
cd book

# Install dependencies
npm install
```

### 2. Run Development Server

```bash
# Start local dev server
npm start

# Server runs at http://localhost:3000
# Opens automatically in your browser
# Hot reload enabled - changes appear within 3 seconds
```

### 3. Make Your First Edit

```bash
# Open any markdown file in book/docs/
# Example: book/docs/part-01-physical-ai/chapter-01-introduction/index.md

# Edit the content
# Save the file
# Browser auto-refreshes with changes
```

## Project Structure

```
book/
├── docs/                      # 📝 Content (edit here!)
│   ├── part-01-physical-ai/
│   │   ├── _category_.json   # Part metadata
│   │   └── chapter-01-*/
│   ├── part-02-ros2/
│   ├── part-03-simulation/
│   ├── part-04-isaac/
│   ├── part-05-human-robot-interaction/
│   └── part-06-conversational-robotics/
├── static/                    # 🖼️ Images and assets
│   ├── img/
│   └── diagrams/
├── src/                       # ⚛️ React components (advanced)
│   ├── components/
│   ├── css/
│   └── pages/
├── docusaurus.config.js       # ⚙️ Main configuration
├── sidebars.js                # 🗂️ Navigation structure
└── package.json               # 📦 Dependencies
```

## Common Tasks

### Creating New Content

#### Add a New Chapter

```bash
# 1. Create chapter directory
mkdir -p book/docs/part-XX-slug/chapter-YY-title

# 2. Create _category_.json
cat > book/docs/part-XX-slug/chapter-YY-title/_category_.json << 'EOF'
{
  "label": "Chapter Y: Title",
  "position": Y,
  "link": {
    "type": "generated-index",
    "description": "Chapter description"
  }
}
EOF

# 3. Create index.md
cat > book/docs/part-XX-slug/chapter-YY-title/index.md << 'EOF'
---
id: introduction
title: Chapter Title
sidebar_label: Short Title
sidebar_position: 1
---

# Chapter Title

Your content here...
EOF
```

#### Add a New Section (Page)

```bash
# Create markdown file in chapter directory
# Filename: section-name.md

cat > book/docs/part-XX-slug/chapter-YY-title/section-name.md << 'EOF'
---
id: section-name
title: Section Title
sidebar_position: 2
---

# Section Title

Content here...
EOF
```

### Adding Images

```bash
# 1. Place image in appropriate static directory
cp my-diagram.png book/static/img/part-02-ros2/

# 2. Reference in markdown
# Relative path from static/
![Diagram description](/img/part-02-ros2/my-diagram.png)

# 3. Verify size limits
ls -lh book/static/img/part-02-ros2/my-diagram.png
# Must be ≤ 2MB
```

### Code Blocks with Syntax Highlighting

```markdown
<!-- Python example -->
```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
\```

<!-- YAML example -->
\```yaml
version: "3.9"
services:
  ros2:
    image: ros:humble
\```

<!-- Bash example -->
\```bash
ros2 run demo_nodes_cpp talker
\```
```

### Internal Links

```markdown
<!-- Link to another page -->
See [ROS 2 Introduction](../part-02-ros2/chapter-01-introduction/index.md)

<!-- Link to section on same page -->
See [Prerequisites](#prerequisites)

<!-- Link using doc ID -->
import Link from '@docusaurus/Link';
<Link to="/docs/part-02-ros2/chapter-01-introduction">ROS 2 Intro</Link>
```

## Development Workflow

### 1. Before Starting Work

```bash
# Update your local repository
git checkout main
git pull origin main

# Create feature branch
git checkout -b update-chapter-03
```

### 2. During Development

```bash
# Run dev server
cd book
npm start

# Edit content in docs/
# Check browser for live updates

# Validate markdown
npm run lint:md

# Check build (important!)
npm run build
```

### 3. Before Committing

```bash
# Check file sizes
npm run validate:assets

# Run full build
npm run build

# Check accessibility (if implemented)
npm run test:a11y

# Stage changes
git add .

# Commit with descriptive message
git commit -m "docs: update chapter 3 with ROS 2 examples"
```

### 4. Push and Deploy

```bash
# Push to your branch
git push origin update-chapter-03

# Create PR (via GitHub UI)
# Once merged to main, automatic deployment triggers
```

## NPM Scripts Reference

```bash
# Development
npm start              # Start dev server (hot reload)
npm run build          # Production build
npm run serve          # Serve production build locally

# Quality Checks
npm run lint:md        # Lint markdown files
npm run validate:assets  # Check image sizes
npm run test:a11y      # Accessibility tests (if configured)

# Utilities
npm run clear          # Clear cache
npm run write-translations  # Extract i18n strings (future)
```

## Troubleshooting

### Dev Server Won't Start

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Build Fails with "Broken Links"

```bash
# Check error message for specific file
# Common issues:
# - Typo in link path
# - File doesn't exist
# - Wrong file extension (.md vs .mdx)

# Fix the link or create missing file
```

### Images Not Displaying

```bash
# Check:
# 1. Image path starts with / (absolute from static/)
#    ✅ ![Alt](/img/part-01/diagram.png)
#    ❌ ![Alt](img/part-01/diagram.png)

# 2. Image exists in static/ directory
ls book/static/img/part-01/diagram.png

# 3. Image size ≤ 2MB
ls -lh book/static/img/part-01/diagram.png
```

### "Asset Size Limit Exceeded"

```bash
# Check individual files
find book/static -type f -size +2M

# Optimize large images
# - Use WebP format
# - Compress with tools like ImageOptim, TinyPNG
# - Resize to reasonable dimensions (max 1920px width)

# Check total folder size
du -sh book/static
# Must be ≤ 100MB
```

## Content Guidelines

### Markdown Best Practices

1. **One H1 per page** (title frontmatter generates H1)
2. **Heading hierarchy**: H1 → H2 → H3 (no skipping)
3. **Alt text for images**: Always provide descriptive alt text
4. **Link text**: Use descriptive text, avoid "click here"
5. **Code language**: Always specify language for syntax highlighting

### Accessibility Checklist

- ✅ Descriptive alt text for all images
- ✅ Proper heading hierarchy (no skipped levels)
- ✅ Descriptive link text (not "click here")
- ✅ Color not sole indicator (use text/icons too)
- ✅ Tables have headers (`<th>`)
- ✅ Lists use proper markup (not manual bullets)

### Performance Tips

1. **Optimize images before adding**:
   - Max width: 1920px
   - Use WebP for photos, SVG for diagrams
   - Compress with ImageOptim or similar

2. **Split long pages**: Prefer multiple short pages over one very long page

3. **Lazy load heavy content**: Use `import()` for React components

## GitHub Pages Deployment

### Automatic Deployment (Main Branch)

```
Commit to main → GitHub Actions runs →
  ├── Install dependencies
  ├── Lint markdown
  ├── Validate assets
  ├── Build site
  ├── Run accessibility tests
  └── Deploy to GitHub Pages

✅ Site live at https://<username>.github.io/<repo>/
```

### Manual Deployment

```bash
# Build locally
npm run build

# Deploy to gh-pages branch (if configured)
GIT_USER=<username> npm run deploy
```

### Deployment Troubleshooting

- **Build fails**: Check GitHub Actions logs
- **Site not updating**: Clear browser cache, wait 2-5 minutes
- **404 errors**: Check `baseUrl` in `docusaurus.config.js`

## Getting Help

### Resources

- **Docusaurus Docs**: https://docusaurus.io/docs
- **Markdown Guide**: https://www.markdownguide.org/
- **Project Spec**: See `specs/001-book-infrastructure/spec.md`
- **Implementation Plan**: See `specs/001-book-infrastructure/plan.md`

### Common Questions

**Q: How do I preview the production build locally?**
```bash
npm run build
npm run serve
# Opens at http://localhost:3000
```

**Q: Can I use React components in markdown?**
Yes! Use `.mdx` extension and import React components.

**Q: How do I change the theme colors?**
Edit `src/css/custom.css` and modify CSS variables.

**Q: What if I need a new syntax highlighting language?**
Add it to `additionalLanguages` in `docusaurus.config.js` under `prism`.

---

**Ready to contribute?** Start with `npm start` and begin editing content in `book/docs/`!
