---
sidebar_position: 1
title: Deployment Guide
---

# Deployment Guide

This document outlines the automated deployment process for the Physical AI & Humanoid Robotics Textbook.

## Overview

The textbook is deployed automatically to GitHub Pages whenever changes are merged into the `main` branch. This process is managed by a GitHub Actions workflow.

## Deployment Workflow

The deployment workflow is defined in `.github/workflows/deploy.yml`. It performs the following steps:

1.  **Checkout Code**: Retrieves the latest code from the repository.
2.  **Setup Node.js**: Configures the environment with the required Node.js version.
3.  **Install Dependencies**: Installs project dependencies using `npm ci`.
4.  **Lint Markdown**: Runs `markdownlint` to ensure content quality.
5.  **Validate Asset Sizes**: Checks that individual image files are under 2MB and total static assets are under 100MB.
6.  **Build Docusaurus Site**: Generates the static HTML, CSS, and JavaScript files for the book.
7.  **Run Accessibility Tests**: Executes `pa11y-ci` to ensure WCAG 2.1 AA compliance.
8.  **Deploy to GitHub Pages**: Publishes the built site to GitHub Pages using `actions/deploy-pages`.

## Triggers

The deployment workflow is triggered by:
*   **Pushes to the `main` branch**: Any direct push or merge into `main` will initiate a deployment.
*   **Manual trigger**: You can manually trigger the workflow from the "Actions" tab in GitHub.

## Monitoring Deployments

You can monitor the status of deployments by:
*   **GitHub Actions Tab**: Navigate to the "Actions" tab in your repository. Each workflow run will show its progress and status (success, failure).
*   **Deployment Status Badge**: The `README.md` includes a status badge that shows the current health of the deployment workflow.

## Atomic Deployments

The deployment process is atomic. If a new build fails (e.g., due to build errors, asset validation failures, or accessibility issues), the **previous successful version of the book remains live** on GitHub Pages. The new, broken version will not be deployed until all issues are resolved and a successful build occurs. This ensures continuous availability of the textbook.

## Troubleshooting

If a deployment fails:

1.  **Check GitHub Actions Logs**: The first step is to review the logs of the failed workflow run in the "Actions" tab. The logs will provide details on which step failed and why (e.g., build error, linting issue, accessibility violation).
2.  **Local Reproduction**: Try to reproduce the issue locally by running `npm run build`, `npm run lint:md`, `npm run validate:assets`, and `cd book && npm run serve -- --port 3000 && npm run test:a11y` in your `book` directory.
3.  **Fix and Re-push**: Address the identified issues, commit your fixes, and push to the `main` branch (or your feature branch and then merge to `main` via PR). A new deployment will be triggered automatically.
4.  **Common Failures**:
    *   **"Minimum Node.js version not met"**: Ensure your `NODE_VERSION` in `.github/workflows/deploy.yml` matches `book/package.json` `engines.node` requirement.
    *   **"Asset size limit exceeded"**: Check `scripts/validate-assets.js` output in logs for oversized files. Optimize or remove them.
    *   **"Accessibility tests failed"**: Review `pa11y-ci` output in logs for specific contrast or accessibility errors. Adjust `book/src/css/custom.css` or content as needed.
    *   **Broken links/markdown**: Docusaurus build will often fail if internal links are broken or markdown has critical errors.

## Further Reading

*   [GitHub Pages Documentation](https://docs.github.com/en/pages)
*   [GitHub Actions Documentation](https://docs.github.com/en/actions)
*   [Docusaurus Deployment](https://docusaurus.io/docs/deployment)
