/**
 * Chat API service for backend communication
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp?: string;
}

export interface Citation {
  text: string;
  url: string;
  chapter?: string;
  section?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  selected_text?: string;
  current_page_url?: string;
}

export interface ChatResponse {
  message: string;
  citations: Citation[];
  session_id: string;
  timestamp: string;
}

export interface StreamEvent {
  type: 'session' | 'content' | 'citation' | 'tool_call' | 'done' | 'error';
  content?: string;
  citation?: Citation;
  tool_name?: string;
  session_id?: string;
  citations?: Citation[];
  full_content?: string;
  error?: string;
}

/**
 * Chat service for API communication
 */
export class ChatService {
  private apiUrl: string;

  constructor(apiUrl: string = '/api/chat') {
    this.apiUrl = apiUrl;
  }

  /**
   * Send a chat message (non-streaming)
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(this.apiUrl, {
      method: 'POST',
      credentials: 'include', // Include cookies for session management
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Send a chat message with streaming (Server-Sent Events)
   */
  async *sendMessageStreaming(
    request: ChatRequest,
  ): AsyncGenerator<StreamEvent, void, unknown> {
    const response = await fetch(`${this.apiUrl}/stream`, {
      method: 'POST',
      credentials: 'include', // Include cookies for session management
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); // Remove 'data: ' prefix

            if (data.trim()) {
              try {
                const event: StreamEvent = JSON.parse(data);
                yield event;
              } catch (e) {
                console.error('Failed to parse SSE data:', data, e);
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Get current page URL for context
   */
  getCurrentPageUrl(): string {
    if (typeof window !== 'undefined') {
      return window.location.pathname;
    }
    return '';
  }
}

// Default instance
export const chatService = new ChatService(
  process.env.NODE_ENV === 'production'
    ? 'https://rag-chatbot-backend-21qb.onrender.com/api/chat'
    : 'http://localhost:8000/api/chat',
);
