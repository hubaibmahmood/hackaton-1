# Data Model: Book Infrastructure

**Feature**: 001-book-infrastructure
**Date**: 2025-11-30
**Phase**: 1 - Design & Contracts

## Overview

This document defines the content structure, configuration entities, and their relationships for the Docusaurus book infrastructure. While this is a static site (no database), the "data model" represents the structured content, configuration files, and metadata that define the book's organization.

## Core Entities

### 1. Part (Top-Level Organization)

**Purpose**: Represents one of six learning outcomes from the constitution

**Location**: `book/docs/part-XX-{slug}/`

**Attributes**:
- `id`: String, kebab-case identifier (e.g., "part-01-physical-ai")
- `title`: String, display name (e.g., "Understanding Physical AI Principles")
- `description`: String, learning outcome summary
- `position`: Integer (1-6), display order
- `icon`: Optional string, emoji or icon identifier
- `learningOutcome`: String, maps to constitution principle

**File Representation** (`_category_.json`):
```json
{
  "label": "Part 1: Understanding Physical AI Principles",
  "position": 1,
  "link": {
    "type": "generated-index",
    "description": "Learn the fundamental principles of Physical AI and embodied intelligence."
  }
}
```

**Relationships**:
- Contains: Multiple Chapters (1:N)
- Maps to: Learning Outcome from Constitution (1:1)

**Validation Rules**:
- Exactly 6 parts must exist
- Each part maps to distinct learning outcome
- Position values 1-6, no duplicates

**State/Lifecycle**: Static (created during initial scaffold)

---

### 2. Chapter

**Purpose**: Major topical section within a Part

**Location**: `book/docs/part-XX-{slug}/chapter-YY-{slug}/`

**Attributes**:
- `id`: String, kebab-case (e.g., "chapter-01-introduction")
- `title`: String, display name
- `description`: Optional string, chapter summary
- `position`: Integer within part
- `prerequisites`: Optional array of chapter IDs
- `estimatedTime`: Optional string (e.g., "45 minutes")

**File Representation** (`_category_.json` or frontmatter in `index.md`):
```json
{
  "label": "Chapter 1: Introduction to ROS 2",
  "position": 1,
  "link": {
    "type": "doc",
    "id": "part-02-ros2/chapter-01-introduction/index"
  }
}
```

**Relationships**:
- Belongs to: Part (N:1)
- Contains: Multiple Sections (1:N)
- References: Other Chapters (N:N via prerequisites)

**Validation Rules**:
- Must belong to exactly one Part
- Position unique within Part
- Prerequisites must reference existing chapters

**State/Lifecycle**: Created by content authors, version-controlled via git

---

### 3. Section (Content Page)

**Purpose**: Individual markdown page covering specific subtopic

**Location**: `book/docs/part-XX-{slug}/chapter-YY-{slug}/section-ZZ-{slug}.md`

**Attributes** (Markdown Frontmatter):
```yaml
---
id: section-01-overview
title: ROS 2 Architecture Overview
sidebar_label: Architecture Overview
sidebar_position: 1
description: Understanding the core components of ROS 2
keywords:
  - ros2
  - architecture
  - middleware
tags:
  - fundamentals
  - ros2
---
```

**Fields**:
- `id`: Unique identifier within docs
- `title`: Page title (H1)
- `sidebar_label`: Shorter nav label
- `sidebar_position`: Display order in sidebar
- `description`: SEO meta description
- `keywords`: Array, search optimization
- `tags`: Array, categorization
- `last_update`: Automatic, git timestamp
- `authors`: Optional array of contributor IDs

**Relationships**:
- Belongs to: Chapter (N:1)
- References: Media Assets (N:N)
- Links to: Other Sections (N:N)

**Validation Rules**:
- Valid markdown syntax
- All image references exist in `static/`
- All internal links resolve
- Heading hierarchy (single H1, H2-H6 nested properly)

**State/Lifecycle**: Actively updated by authors, version history via git

---

### 4. Media Asset

**Purpose**: Images, diagrams, videos stored in static folder

**Location**: `book/static/img/{category}/{filename}`

**Attributes**:
- `path`: Relative path from `static/` (e.g., "img/part-02-ros2/node-graph.png")
- `filename`: String with extension
- `size`: Integer bytes (max 2MB per file)
- `type`: String (image/png, image/jpeg, image/svg+xml, etc.)
- `altText`: Required string (from markdown `![alt](path)`)
- `category`: Directory structure (by part or content area)

**File Organization**:
```
static/
├── img/
│   ├── part-01-physical-ai/
│   ├── part-02-ros2/
│   ├── part-03-simulation/
│   ├── part-04-isaac/
│   ├── part-05-human-robot-interaction/
│   ├── part-06-conversational-robotics/
│   └── shared/               # Cross-part assets
└── diagrams/
    └── {same structure}
```

**Relationships**:
- Referenced by: Sections (N:N)
- Grouped by: Category/Part (N:1)

**Validation Rules**:
- File size ≤2MB
- Total static folder ≤100MB
- Supported formats: PNG, JPG, WebP, SVG, GIF
- Alt text required for all images in content

**State/Lifecycle**: Created with content, immutable (updates create new file or version)

---

### 5. Navigation Item

**Purpose**: Entry in sidebar navigation

**Location**: Generated from `book/sidebars.js` and `_category_.json` files

**Attributes**:
- `type`: String ("category", "doc", "link", "ref")
- `label`: String, display text
- `href`: Optional string (for external links)
- `docId`: Optional string (for doc type)
- `items`: Optional array (for category type, nested navigation)
- `position`: Integer, sort order

**Configuration Example** (`sidebars.js`):
```javascript
module.exports = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Part 1: Understanding Physical AI',
      collapsed: false,
      items: [
        'part-01-physical-ai/chapter-01-introduction/index',
        'part-01-physical-ai/chapter-02-embodied-intelligence/index',
        // ... more chapters
      ],
    },
    // ... more parts
  ],
};
```

**Relationships**:
- Represents: Part, Chapter, or Section (1:1)
- Hierarchical: Parent-Child (tree structure, 3+ levels)

**Validation Rules**:
- All referenced `docId` values must exist
- No circular references
- Maximum nesting depth: unlimited (but 3-4 recommended per UX)

**State/Lifecycle**: Auto-generated from directory structure and `_category_.json` files

---

### 6. Configuration (Docusaurus Config)

**Purpose**: Main site configuration

**Location**: `book/docusaurus.config.js` (or `.ts`)

**Attributes**:
```typescript
{
  title: string,              // "Physical AI & Humanoid Robotics"
  tagline: string,
  url: string,                // GitHub Pages URL
  baseUrl: string,            // "/" for root domain
  organizationName: string,   // GitHub org/user
  projectName: string,        // GitHub repo name
  themeConfig: {
    navbar: {...},
    footer: {...},
    prism: {
      theme: object,
      additionalLanguages: string[],
    },
    colorMode: {
      defaultMode: 'light' | 'dark',
      respectPrefersColorScheme: boolean,
    },
    algolia?: object,         // Future: Algolia search config
  },
  presets: array,             // [@docusaurus/preset-classic]
  plugins: array,             // Additional plugins
}
```

**Relationships**:
- Configures: Entire site (1:1)
- References: Theme, Plugins, Presets

**Validation Rules**:
- Valid JavaScript/TypeScript syntax
- Required fields present
- URLs well-formed

**State/Lifecycle**: Modified during infrastructure setup, rarely changed afterward

---

### 7. Build Artifact

**Purpose**: Generated static files for deployment

**Location**: `book/build/` (generated, not tracked in git)

**Attributes**:
- `timestamp`: Build time
- `commit`: Git SHA that triggered build
- `files`: Array of generated HTML/CSS/JS files
- `size`: Total build output size
- `duration`: Build time in seconds

**Generated Structure**:
```
build/
├── index.html
├── assets/
│   ├── css/
│   ├── js/
│   └── images/        # Optimized copies from static/
├── part-01-physical-ai/
│   └── chapter-01-introduction/
│       └── index.html
└── sitemap.xml
```

**Relationships**:
- Generated from: Parts, Chapters, Sections, Assets
- Deployed to: GitHub Pages

**Validation Rules**:
- Build size reasonable (< GitHub Pages 1GB limit)
- All pages accessible (no 404s)
- WCAG AA compliance (checked via Pa11y)

**State/Lifecycle**: Generated during build, deployed to GitHub Pages, ephemeral locally

---

### 8. Deployment

**Purpose**: GitHub Actions workflow execution

**Location**: `.github/workflows/deploy.yml`

**Attributes**:
- `trigger`: Event (push to main, workflow_dispatch)
- `status`: pending | success | failure
- `buildId`: GitHub Actions run ID
- `commit`: Git SHA being deployed
- `timestamp`: Deployment time
- `deployUrl`: GitHub Pages URL
- `logs`: GitHub Actions logs URL

**Workflow Steps**:
1. Checkout code
2. Setup Node.js
3. Install dependencies
4. Run tests (markdown lint, accessibility checks)
5. Build site (`npm run build`)
6. Deploy to gh-pages branch
7. Notify on failure

**Relationships**:
- Triggered by: Git commits to main
- Produces: Build Artifact
- Updates: GitHub Pages hosting

**Validation Rules**:
- Build must succeed before deploy
- Accessibility tests must pass
- Previous deployment remains live on failure (atomic)

**State/Lifecycle**: Triggered automatically, logs retained by GitHub Actions

---

## Entity Relationship Diagram (Textual)

```
Constitution (1)
  └── Learning Outcomes (6)
        └── Parts (6) [1:1 mapping]
              └── Chapters (N)
                    └── Sections (N)
                          ├── References → Media Assets (N:N)
                          └── Links to → Other Sections (N:N)

Configuration (1)
  ├── Configures → Site (1)
  └── Defines → Theme, Navbar, Footer

Navigation Items (tree)
  ├── Represents → Parts, Chapters, Sections
  └── Hierarchical structure (parent-child)

Build Process
  Input: Parts + Chapters + Sections + Media Assets + Configuration
  Output: Build Artifact
  Deploys to: GitHub Pages via Deployment workflow
```

## Data Constraints Summary

| Entity | Key Constraint | Validation |
|--------|---------------|------------|
| Part | Exactly 6 parts | Pre-commit check |
| Chapter | Unique position within part | Build-time validation |
| Section | Valid markdown, resolved links | Build-time (Docusaurus) |
| Media Asset | ≤2MB per file, ≤100MB total | Pre-commit + CI |
| Navigation | No broken links | Build-time (Docusaurus) |
| Build Artifact | WCAG AA compliance | CI (Pa11y) |
| Deployment | Previous version on failure | GitHub Actions atomic deploy |

## Metadata Schema

### Part Metadata (`_category_.json`)
```json
{
  "$schema": "https://docusaurus.io/schemas/category.json",
  "label": "Part N: Title",
  "position": 1-6,
  "link": {
    "type": "generated-index",
    "description": "Learning outcome description",
    "slug": "part-XX-slug"
  },
  "customProps": {
    "learningOutcome": "Aligned to Constitution Principle X"
  }
}
```

### Section Frontmatter (Markdown)
```yaml
---
id: unique-section-id
title: Display Title
sidebar_label: Nav Label
sidebar_position: integer
description: SEO and preview text
keywords: [array, of, keywords]
tags: [array, of, tags]
# Optional
authors: [author-id-1, author-id-2]
hide_table_of_contents: boolean
---
```

## Implementation Notes

1. **No Database**: All "data" is files (markdown, JSON, YAML)
2. **Version Control**: Git is the source of truth
3. **Build-Time Validation**: Docusaurus build fails on broken links, missing assets
4. **Runtime**: Static HTML/CSS/JS, no backend API
5. **Search Index**: Generated at build time from all content

---

**Data Model Complete**: All entities defined, ready for contract generation.
