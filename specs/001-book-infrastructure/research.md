# Research & Technology Decisions: Book Infrastructure

**Feature**: 001-book-infrastructure
**Date**: 2025-11-30
**Phase**: 0 - Outline & Research

## Overview

This document consolidates research findings and technology decisions for the Docusaurus book infrastructure feature, resolving all technical unknowns and establishing best practices for implementation.

## Technology Stack Decisions

### 1. Static Site Generator: Docusaurus 3.x

**Decision**: Use Docusaurus 3.x (latest stable version)

**Rationale**:
- **Hackathon Requirement**: Explicitly mandated in project requirements
- **Documentation-First**: Purpose-built for technical documentation and educational content
- **Built-in Features**: Search, versioning, i18n, responsive design, dark mode out-of-the-box
- **React Ecosystem**: Enables future RAG chatbot integration via React components
- **Active Maintenance**: Meta-backed project with strong community support
- **Performance**: Static generation ensures fast load times and SEO benefits
- **GitHub Pages Native**: First-class support for GH Pages deployment

**Alternatives Considered**:
- **VuePress**: Good documentation tool but smaller ecosystem than Docusaurus
- **GitBook**: Commercial product with usage limits; not open-source
- **MkDocs**: Python-based, less suitable for React chatbot integration
- **Nextra**: Next.js-based, newer with less mature plugin ecosystem

**Best Practices**:
- Use TypeScript for `docusaurus.config.ts` for type safety
- Leverage MDX for interactive content (embed React components in markdown)
- Enable `docs-only` mode if no blog is needed
- Use `@docusaurus/preset-classic` for standard features

### 2. Content Structure: Learning Outcomes-Based Organization

**Decision**: 6-part structure mapping to constitution's learning outcomes

**Rationale**:
- **Pedagogical Alignment**: Directly supports educational objectives
- **Clear Navigation**: Students understand "where am I?" and "what am I learning?"
- **Modular Design**: Parts can be developed/updated independently
- **Searchability**: Well-organized taxonomy improves search relevance

**Structure Mapping**:
```
Part 1: Understanding Physical AI Principles
Part 2: Mastering ROS 2 for Robotic Systems
Part 3: Simulating Robots with Gazebo and Unity
Part 4: Developing with NVIDIA Isaac
Part 5: Designing Humanoid Robots for Natural Interactions
Part 6: Integrating GPT Models for Conversational Robotics
```

**Alternatives Considered**:
- **Chronological**: Start-to-finish project approach (less modular)
- **Technology-First**: Organize by tool (ROS 2, Gazebo, Isaac) - less pedagogically clear
- **Difficulty-Based**: Beginner→Advanced (harder to map to outcomes)

**Best Practices**:
- Use `_category_.json` in each part directory for metadata
- Include learning objectives at start of each part
- Cross-reference related concepts across parts
- Provide "Prerequisites" section for each chapter

### 3. Asset Management: Repository-Based with Limits

**Decision**: Store all assets in `book/static/` with 2MB/file, 100MB total limits

**Rationale**:
- **Self-Contained**: No external dependencies (CDN, cloud storage)
- **Simplicity**: Single git repository for all content
- **Version Control**: Images tracked alongside content changes
- **GitHub Pages Compatible**: Static folder served directly
- **Performance**: Limits prevent bloat and ensure fast loading

**Implementation Strategy**:
- Pre-commit hook validates file sizes
- Build script checks total static folder size
- Compress images (WebP, optimized PNG/JPG)
- Use SVG for diagrams and icons where possible
- Reference external videos (YouTube) rather than embedding large files

**Alternatives Considered**:
- **External CDN** (Cloudinary, imgix): Adds complexity, external dependency
- **Git LFS**: Complicates clone/setup, GitHub LFS has storage costs
- **Submodule for Assets**: Overcomplicated for small-to-medium content

**Best Practices**:
- Naming convention: `kebab-case-descriptive-name.ext`
- Organize by content area: `static/img/part-02-ros2/`
- Provide alt text for all images (accessibility)
- Use `@site/static/` imports in React components

### 4. Accessibility: WCAG 2.1 Level AA Compliance

**Decision**: Implement WCAG 2.1 AA standards with automated validation

**Rationale**:
- **Educational Content Standard**: AA is baseline for academic institutions
- **Legal Compliance**: Many regions require AA for public educational materials
- **Inclusive Design**: Ensures content accessible to students with disabilities
- **Docusaurus Support**: Framework provides good accessibility foundations

**Implementation Tools**:
- **axe-core**: Automated accessibility testing library
- **Pa11y**: CI-integrated accessibility checker
- **Lighthouse**: Performance and accessibility audits
- **WAVE**: Manual testing tool for development

**Key Requirements**:
- Color contrast ratio ≥4.5:1 for normal text, ≥3:1 for large text
- Keyboard navigation for all interactive elements
- ARIA labels for custom components
- Semantic HTML heading hierarchy (h1→h2→h3)
- Alt text for all informative images
- Skip navigation links
- Focus indicators

**Alternatives Considered**:
- **AAA Compliance**: More stringent but overkill for this use case
- **No Formal Standard**: Risky for educational content
- **A Level Only**: Insufficient for modern accessibility expectations

**Best Practices**:
- Run `pa11y` in CI/CD pipeline, fail build on errors
- Include accessibility checklist in content contribution guide
- Use Docusaurus color mode with accessible color palettes
- Test with screen readers (NVDA, JAWS, VoiceOver)

### 5. Deployment: GitHub Actions + GitHub Pages

**Decision**: Automated deployment via GitHub Actions on main branch pushes

**Rationale**:
- **Zero Cost**: GitHub Actions free for public repos
- **Native Integration**: GitHub Pages designed for GitHub repos
- **Atomic Deployments**: Previous version stays live until new build succeeds
- **Simple Workflow**: Standard Docusaurus build → GH Pages deploy pattern

**Workflow Strategy**:
- Trigger: `push` to `main` branch only
- Build: `npm run build` (Docusaurus static generation)
- Test: Run accessibility checks before deploy
- Deploy: Use `peaceiris/actions-gh-pages@v3` action
- Notifications: Fail loudly on errors (GitHub notifications)

**Deployment Resilience**:
- Previous deployment remains live if build fails (FR-021)
- Build logs accessible in GitHub Actions UI (FR-015)
- Deployment completes within 5-minute SLA (SC-003)

**Alternatives Considered**:
- **Netlify**: Excellent platform but adds external dependency
- **Vercel**: Similar to Netlify, commercial service
- **Manual Deployment**: Error-prone, doesn't scale
- **Self-Hosted**: Unnecessary complexity for static site

**Best Practices**:
- Use concurrency groups to prevent duplicate deployments
- Cache node_modules to speed up builds
- Set `CNAME` for custom domain support (future)
- Include build status badge in README

### 6. Search: Built-in Docusaurus Search

**Decision**: Use Docusaurus's built-in client-side search (Algolia optional later)

**Rationale**:
- **Zero Setup**: Works out-of-box with no configuration
- **Offline-Capable**: Search works in local development
- **Privacy**: No third-party service, no data sent externally
- **Performance**: Client-side search is fast for documentation-sized content
- **Meets Requirements**: SC-006 requires <1s results (client-side achieves this)

**Future Migration Path**:
- If content grows beyond ~500 pages, migrate to Algolia DocSearch
- Algolia free for open-source documentation
- Minimal config change in Docusaurus

**Alternatives Considered**:
- **Algolia from Start**: Overkill for initial content volume
- **Lunr.js**: More complex setup than Docusaurus built-in
- **No Search**: Violates FR-011

**Best Practices**:
- Use descriptive headings (improve search relevance)
- Include keywords in page frontmatter
- Test common search queries during QA

### 7. Syntax Highlighting: Prism.js with Custom Languages

**Decision**: Use Prism.js (Docusaurus default) with ROS 2 XML/YAML support

**Rationale**:
- **Built-in**: Comes with Docusaurus, zero additional setup
- **Extensible**: Easy to add custom language definitions
- **Performance**: Lightweight, fast highlighting
- **Themes**: Dark/light mode support via Docusaurus themes

**Required Languages** (FR-009):
- Python (built-in)
- JavaScript (built-in)
- YAML (built-in)
- XML (for URDF and ROS 2 launch files)
- Bash/Shell (for command examples)

**Custom Highlighting**:
- Add ROS 2-specific keywords to XML highlighting
- Consider custom grammar for URDF if needed

**Alternatives Considered**:
- **Highlight.js**: Alternative syntax highlighter, no advantage over Prism
- **Shiki**: More accurate but slower, overkill for this use case

**Best Practices**:
- Always specify language in code fences: ```python
- Use line numbers for long code blocks
- Highlight specific lines for emphasis
- Provide runnable examples in separate files

### 8. Testing Strategy: Multi-Layer Validation

**Decision**: Combine build validation, accessibility tests, and markdown linting

**Testing Layers**:

1. **Build Validation** (every commit)
   - Docusaurus build must succeed
   - No broken links (docusaurus-plugin-content-docs validates)
   - Assets exist (images referenced in markdown)

2. **Accessibility Tests** (CI pipeline)
   - `pa11y-ci` scans all pages
   - Fail on WCAG AA violations
   - Lighthouse accessibility score ≥90

3. **Markdown Linting** (pre-commit)
   - `markdownlint` enforces consistent formatting
   - Catches common markdown errors
   - Configurable rules via `.markdownlint.json`

4. **Asset Validation** (pre-commit + CI)
   - Custom script checks file sizes (2MB limit)
   - Total static folder size check (100MB limit)

**Alternatives Considered**:
- **Manual Testing Only**: Insufficient, error-prone
- **Visual Regression**: Overkill for documentation site
- **E2E Tests** (Playwright): Not needed for static content

**Best Practices**:
- Fast-fail: Run quick checks (linting) before slow checks (build)
- Local pre-commit hooks prevent CI failures
- Clear error messages guide contributors

## Implementation Risks & Mitigations

### Risk 1: Asset Size Bloat

**Risk**: Authors upload large images, hitting 100MB limit
**Likelihood**: Medium
**Impact**: High (blocks new content)
**Mitigation**:
- Pre-commit hook rejects oversized files
- Documentation with image optimization guidelines
- Provide image compression tools/scripts
- Monitor static folder size in CI

### Risk 2: Accessibility Violations

**Risk**: Content authors introduce WCAG violations
**Likelihood**: Medium
**Impact**: Medium (fails build, blocks deployment)
**Mitigation**:
- Author guidelines with accessibility checklist
- Automated tests catch violations early
- Pre-commit hook runs basic accessibility checks
- Train authors on common issues (alt text, headings)

### Risk 3: Build Time Creep

**Risk**: As content grows, build time exceeds 5-minute SLA
**Likelihood**: Low (initially), Medium (long-term)
**Impact**: Medium (slower feedback loop)
**Mitigation**:
- Monitor build times in CI
- Enable Docusaurus incremental builds (future)
- Optimize assets (lazy loading, WebP)
- Consider build caching strategies

### Risk 4: Search Performance Degradation

**Risk**: Client-side search becomes slow with large content
**Likelihood**: Low (initially), High (500+ pages)
**Impact**: Low (annoying but not blocking)
**Mitigation**:
- Monitor search performance with large content
- Migration path to Algolia DocSearch documented
- Threshold: migrate at ~500 pages or when search >1s

### Risk 5: GitHub Pages Downtime

**Risk**: GitHub Pages unavailable during deployment
**Likelihood**: Very Low
**Impact**: Low (temporary, GitHub handles)
**Mitigation**:
- No action needed (FR-021 ensures previous version stays live)
- GitHub Pages SLA covers this scenario
- Monitor GitHub status page for planned maintenance

## Key Decisions Summary

| Decision Area | Choice | Why |
|---------------|--------|-----|
| **SSG** | Docusaurus 3.x | Hackathon requirement, React ecosystem, excellent docs support |
| **Content Structure** | 6-part learning outcomes | Pedagogical alignment, clear navigation, modular |
| **Assets** | Repo-based, 2MB/100MB limits | Self-contained, simple, version-controlled |
| **Accessibility** | WCAG 2.1 AA | Educational standard, inclusive, legally sound |
| **Deployment** | GitHub Actions + Pages | Free, integrated, atomic deployments |
| **Search** | Docusaurus built-in | Zero setup, fast, privacy-friendly |
| **Syntax Highlighting** | Prism.js | Built-in, extensible, performant |
| **Testing** | Multi-layer (build+a11y+lint) | Comprehensive, automated, fast-fail |

## Next Steps (Phase 1)

1. Generate `data-model.md` (content structure entities)
2. Create contracts (config schemas, workflow definitions)
3. Write `quickstart.md` (setup and development guide)
4. Update agent context with Docusaurus/Node.js technologies

---

**Research Complete**: All technical unknowns resolved, ready for Phase 1 design.
