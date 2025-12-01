# Contributing to Physical AI & Humanoid Robotics Textbook

Thank you for contributing to this educational resource! This guide will help you create high-quality content that follows our standards and conventions.

## Prerequisites

- **Node.js 18+** installed
- Repository cloned and dependencies installed: `npm install` in the `book/` directory
- Familiarity with Markdown and basic Docusaurus concepts

## Content Structure

The textbook is organized into 6 Parts, each covering a major theme:

```
book/docs/
├── part-01-physical-ai/
├── part-02-ros2/
├── part-03-simulation/
├── part-04-isaac/
├── part-05-humanoid-robot-development/
└── part-06-conversational-robotics/
```

Each Part contains:
- `_category_.json` - Part metadata for sidebar navigation
- `intro.md` - Part introduction
- `chapter-XX-topic-slug/index.md` - Individual chapters
- `assessment.md` - End-of-part assessment (where applicable)

## Adding a New Chapter

### Step 1: Identify the Target Part

Navigate to `book/docs/` and identify the correct `part-XX` folder based on your content's topic.

### Step 2: Create Chapter Directory

Create a new folder following the naming convention: `chapter-YY-topic-slug`

**Example**: `book/docs/part-02-ros2/chapter-05-first-node`

**Naming Guidelines**:
- Use sequential numbering (`chapter-01`, `chapter-02`, etc.)
- Use lowercase kebab-case for slugs
- Keep slugs concise but descriptive (2-4 words)

### Step 3: Create Index File

Inside the chapter folder, create `index.md`.

### Step 4: Add Required Frontmatter

Every chapter **MUST** include the following YAML frontmatter:

```yaml
---
title: "Your Chapter Title"
description: "A one-sentence summary of what this chapter covers (for SEO and preview cards)."
sidebar_position: 5
tags: [ros2, python, sensors]
---
```

**Frontmatter Requirements** (validated by schema):
- `title` (string, required): The H1 title of the chapter
- `description` (string, required): Short summary for SEO and card previews
- `sidebar_position` (integer, required): Order in the sidebar menu (minimum: 1)
- `tags` (array of strings, optional): Docusaurus search tags

### Step 5: Structure Your Content

Follow this standard chapter structure:

```markdown
---
title: "Chapter Title"
description: "Brief summary"
sidebar_position: 1
tags: [relevant, tags]
---

# Chapter Title

## Learning Objectives

- By the end of this chapter, you will be able to...
- Objective 2
- Objective 3

## Introduction

Brief overview of the chapter content and its relevance.

## Main Content

### Section 1: Topic Name

Content goes here...

### Section 2: Another Topic

More content...

## Practical Example

Step-by-step walkthrough with code examples.

## Common Issues & Troubleshooting

- **Issue**: Description
  - **Solution**: Fix instructions

## Summary

- Key takeaway 1
- Key takeaway 2
- Key takeaway 3

## Further Reading

- [Resource Title](URL) - Brief description
- [Another Resource](URL) - Brief description

## Exercises

1. **Exercise 1**: Description and instructions
2. **Exercise 2**: Description and instructions
```

## Code Examples

### Inline Code

Use single backticks for inline code references:
```markdown
The `rclpy.init()` function initializes the ROS 2 Python client library.
```

### Code Blocks

Use triple backticks with language identifier for syntax highlighting:

````markdown
```python
import rclpy
from rclpy.node import Node

class MinimalNode(Node):
    def __init__(self):
        super().__init__('minimal_node')
        self.get_logger().info('Node started!')

def main():
    rclpy.init()
    node = MinimalNode()
    rclpy.spin(node)
    rclpy.shutdown()
```
````

**Supported Languages**: `python`, `cpp`, `bash`, `xml`, `yaml`, `json`, `markdown`

### Code Block Titles

Add titles to code blocks for better context:

````markdown
```python title="minimal_publisher.py"
# Code content here
```
````

### Complete vs. Illustrative Code

- **Complete Code**: Fully runnable, self-contained examples (preferred)
- **Illustrative Snippets**: Partial code marked with comments like `# ... (previous code)` or `# Excerpt`

### Downloadable Code Examples

For complete working code, place source files in `book/static/code/part-XX/chapter-YY/` and link to them:

```markdown
Download the complete source code: [minimal_publisher.py](/code/part-02/chapter-05/minimal_publisher.py)
```

## Local vs. Cloud Setup Instructions

When providing setup instructions that differ for local and cloud environments, use Docusaurus Tabs:

```jsx
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="local" label="💻 Local Setup">

For local installation on Ubuntu 22.04:

```bash
sudo apt update
sudo apt install ros-humble-desktop
```

  </TabItem>
  <TabItem value="cloud" label="☁️ Cloud Setup">

For cloud environments (Google Colab, AWS Cloud9):

```bash
# Cloud-specific instructions
```

  </TabItem>
</Tabs>
```

## Images and Diagrams

### Adding Images

1. Create an `img/` folder inside your chapter directory
2. Place images there (PNG, JPG, SVG)
3. Reference using relative paths:

```markdown
![Robot Architecture](./img/architecture-diagram.png)
```

### Image Guidelines

- Use descriptive filenames: `ros2-node-graph.png` (not `image1.png`)
- Include alt text for accessibility
- Prefer SVG for diagrams when possible
- Keep file sizes reasonable (<500KB for photos, <100KB for diagrams)

## Admonitions (Callout Boxes)

Use Docusaurus admonitions for important notes, tips, warnings, and cautions:

```markdown
:::note
This is a note with useful information.
:::

:::tip
Pro tip: This shortcut will save you time!
:::

:::warning
Be careful with this command as it can overwrite files.
:::

:::danger
This operation is irreversible. Make backups first!
:::

:::info
Additional context or background information.
:::
```

## Writing Style Guidelines

### Tone and Voice

- **Instructional and clear**: Use active voice and imperative mood for instructions
- **Encouraging**: Assume the reader can succeed with proper guidance
- **Concise**: Target 20-30 minutes of reading time per chapter
- **Inclusive**: Use "we" when exploring concepts together, "you" for instructions

### Technical Writing Best Practices

1. **Define terms on first use**: Introduce acronyms and technical terms before using them extensively
2. **Use concrete examples**: Abstract concepts should be illustrated with real-world scenarios
3. **Step-by-step instructions**: Break complex procedures into numbered steps
4. **Consistent terminology**: Use the same term for the same concept throughout (e.g., "node" not alternating between "node" and "process")
5. **Code before explanation**: Show working code first, then explain how it works

### Accessibility

- Provide alt text for all images
- Use descriptive link text (not "click here")
- Ensure code examples are properly formatted for screen readers
- Use heading hierarchy correctly (don't skip levels)

## Target Audience

The textbook is designed for:
- **Python developers** transitioning to robotics
- **Undergraduate/graduate students** in computer science or engineering
- **Hobbyists and makers** with programming experience

**Assumed Prerequisites**:
- Python 3 basics (functions, classes, imports)
- Command line familiarity (cd, ls, mkdir)
- Basic understanding of object-oriented programming

**NOT Assumed**:
- ROS 2 experience
- C++ knowledge (it's introduced where needed)
- Robotics background
- Linux administration expertise

## Content Quality Requirements

Each chapter must include:
- ✅ **Learning Objectives** (2-5 clear, measurable outcomes)
- ✅ **Code Examples** (at least one complete runnable example)
- ✅ **Summary** (key takeaways, 3-5 bullet points)
- ✅ **Troubleshooting Section** (common issues and solutions)
- ✅ **Further Reading** (2-4 external resources with descriptions)

Optional but encouraged:
- Diagrams and visual aids
- Exercises for hands-on practice
- Real-world use cases
- Performance considerations
- Security best practices (where applicable)

## Testing Your Content

### Local Preview

Run the development server to preview your changes:

```bash
cd book/
npm start
```

This opens a browser at `http://localhost:3000` with live reload.

### Verification Checklist

Before submitting your content:

- [ ] Frontmatter is complete and valid (title, description, sidebar_position, tags)
- [ ] Chapter appears in the sidebar at the correct position
- [ ] All code blocks have language identifiers
- [ ] All code examples are tested and run correctly
- [ ] All links are working (no 404s)
- [ ] Images load and have alt text
- [ ] No markdown lint errors (`npm run lint` if configured)
- [ ] Reading time is 20-30 minutes
- [ ] All required sections are present (objectives, summary, troubleshooting, further reading)

### Testing Code Examples

All complete code examples should be:
1. **Tested locally**: Run the code on Ubuntu 22.04 with ROS 2 Humble (or stated environment)
2. **Documented**: Include necessary dependencies, environment setup, and expected output
3. **Reproducible**: Another person should be able to copy-paste and run successfully

## Academic Integrity

### Citations

When referencing external sources:
- Provide clear citations with URLs
- Use quotes for verbatim text
- Paraphrase with attribution when adapting content
- Link to official documentation for API references

### Original Work

- Write original explanations and examples
- Don't copy-paste from other tutorials without permission
- When building on open-source examples, provide attribution and license info

## File and Folder Naming Conventions

- **Folders**: `lowercase-kebab-case` (e.g., `chapter-03-sensors`)
- **Markdown files**: `lowercase-kebab-case.md` (e.g., `intro.md`, `assessment.md`)
- **Code files**: Follow language conventions (e.g., `snake_case.py`, `PascalCase.cpp`)
- **Images**: `descriptive-name.png` (e.g., `robot-sensor-diagram.png`)

## Version Control

- Create a feature branch for your changes
- Use descriptive commit messages
- Reference issue numbers if applicable
- Keep commits focused (one logical change per commit)

## Need Help?

- Check existing chapters for examples
- Review the [Docusaurus documentation](https://docusaurus.io/docs)
- Refer to the project specification: `specs/002-textbook-content/spec.md`
- Ask questions in project discussions or issues

## Related Resources

- **Feature Specification**: `specs/002-textbook-content/spec.md`
- **Implementation Plan**: `specs/002-textbook-content/plan.md`
- **Data Model**: `specs/002-textbook-content/data-model.md`
- **Quickstart Guide**: `specs/002-textbook-content/quickstart.md`
- **Frontmatter Schema**: `specs/002-textbook-content/contracts/chapter-frontmatter.schema.json`

---

Thank you for contributing to this educational resource! Your efforts help students worldwide learn Physical AI and Humanoid Robotics.
