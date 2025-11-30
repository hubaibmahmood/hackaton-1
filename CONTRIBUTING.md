# Contributing to the Physical AI & Humanoid Robotics Textbook

We welcome contributions to this textbook! Please follow these guidelines to ensure a smooth collaboration.

## Getting Started

1.  **Fork** the repository on GitHub.
2.  **Clone** your forked repository to your local machine.
3.  **Install dependencies**:
    ```bash
    cd book
    npm install
    ```
4.  **Start the development server**:
    ```bash
    npm start
    ```
    This will open the book in your browser at `http://localhost:3000` with live-reloading.

## Making Changes

*   **Create a new branch** for your feature or fix: `git checkout -b feature/my-awesome-feature`
*   **Content is written in Markdown** (`.md` files) in the `book/docs/` directory.
*   **Images** should be placed in `book/static/img/` or `book/static/diagrams/`.
    *   Images must be under 2MB.
    *   Total static assets should be under 100MB.
*   **Refer to the `quickstart.md`** for more detailed instructions on creating new chapters, sections, and adding media.

## Markdown Style Guide

*   **Headings**: Use `#` for H1, `##` for H2, etc. (only one H1 per page, which is the title from frontmatter).
*   **Code Blocks**: Always specify the language for syntax highlighting (e.g., `` ```python ``).
*   **Links**: Use relative paths for internal links.
*   **Images**: Always include descriptive alt text: `![Alt text for image](/img/path/to/image.png)`
*   **Lists**: Use hyphens (`-`) for unordered lists and numbers (`1.`) for ordered lists.

## Submitting Your Changes

1.  **Commit your changes** with a clear and concise message.
2.  **Push your branch** to your forked repository.
3.  **Create a Pull Request** (PR) to the `main` branch of the original repository.
    *   Ensure your PR title is descriptive.
    *   Include a summary of your changes in the PR description.
    *   Link to any relevant issues.

## Style & Quality Checks

Before submitting your PR, ensure your changes pass the following checks (these will also run in CI):
*   **Markdown Linting**: `cd book && npm run lint:md`
*   **Asset Validation**: `npm run validate:assets`
*   **Accessibility**: (automated in CI)
*   **Build**: `cd book && npm run build`

Thank you for contributing!
