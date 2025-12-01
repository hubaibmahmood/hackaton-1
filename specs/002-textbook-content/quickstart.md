# Quickstart: Adding a New Chapter

## Prerequisites
- Node.js 18+ installed
- Repo cloned and dependencies installed (`npm install` in `book/` directory)

## Steps

1. **Identify the Target Part**
   Navigate to `book/docs/`. Identify the correct `part-XX` folder.

2. **Create Chapter Directory**
   Create a new folder following the naming convention: `chapter-YY-topic-slug`.
   *Example*: `book/docs/part-02-ros2/chapter-05-first-node`

3. **Create Index File**
   Inside that folder, create `index.md`.

4. **Add Frontmatter**
   Paste the standard header:
   ```md
   ---
   title: "Your Chapter Title"
   description: "A one-sentence summary of what this chapter covers."
   sidebar_position: 5
   tags: [relevant, tags]
   ---

   # Your Chapter Title

   ## Learning Objectives
   - Objective 1
   - Objective 2
   ```

5. **Write Content**
   - Use standard Markdown.
   - For code, use triple backticks with language: ```python ... ```.
   - For "Local vs Cloud" choices, use Tabs:
     ```jsx
     import Tabs from '@theme/Tabs';
     import TabItem from '@theme/TabItem';

     <Tabs>
       <TabItem value="local" label="💻 Local Setup">
         Local instructions...
       </TabItem>
       <TabItem value="cloud" label="☁️ Cloud Setup">
         Cloud instructions...
       </TabItem>
     </Tabs>
     ```

6. **Verify**
   Run `npm start` in the `book/` directory.
   Verify the chapter appears in the sidebar and renders correctly.
