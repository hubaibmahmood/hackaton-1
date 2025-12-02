---
sidebar_position: 10
---

# Chatbot Integration Guide

This guide explains how to integrate and customize the AI Chatbot in the Docusaurus book.

## Overview

The chatbot is implemented as a global React component (`ChatBot`) injected into the Docusaurus theme via `src/theme/Root.tsx`. This ensures it persists across page navigation.

## Configuration

The chatbot uses the `ChatProvider` (internal logic) and communicates with the backend API.

### Environment Variables

The frontend determines the backend API URL based on the build environment:

- **Development**: Defaults to `http://localhost:8000/api/chat`
- **Production**: You must configure the production URL in `book/src/services/chatService.ts` or via build-time environment variables.

Currently, the production URL is hardcoded in `chatService.ts` as a fallback. To change it:

1. Open `book/src/services/chatService.ts`
2. Update the URL in the default instance creation:

```typescript
export const chatService = new ChatService(
  process.env.NODE_ENV === 'production'
    ? 'https://your-backend-url.onrender.com/api/chat'
    : 'http://localhost:8000/api/chat'
);
```

## Customization

### Styling

The chatbot styles are defined in `book/src/components/ChatBot/ChatBot.css`. It uses CSS variables for easy theming.

**Key Variables:**

```css
:root {
  --chatbot-primary: #2563eb; /* Main brand color */
  --chatbot-width: 400px;     /* Width of the chat window */
  --chatbot-height: 650px;    /* Height of the chat window */
  --chatbot-radius: 20px;     /* Border radius */
}
```

To override these, you can edit the file directly or add overrides in your Docusaurus `custom.css`.

### Context Injection

The chatbot automatically detects the current page context (Part/Chapter) using the URL structure. This is handled in `ChatBot.tsx` via the `useLocation` hook.

If you change the URL structure of the book (e.g., not using `part-XX/chapter-YY`), you may need to update the parsing logic in the `useEffect` hook in `ChatBot.tsx`.

## Disabling the Chatbot

To disable the chatbot on specific pages, you can modify `book/src/components/ChatBot/FloatingButton.tsx` to check the current path and return `null` if it matches an exclusion list.

## Troubleshooting

- **CORS Errors**: Ensure the `FRONTEND_ORIGIN` environment variable in the backend matches your book's deployed URL.
- **Connection Failed**: Check if the backend service is running and the `apiUrl` in `chatService.ts` is correct.
