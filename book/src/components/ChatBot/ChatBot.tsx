/**
 * Main ChatBot component with ChatKit integration
 */
import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useLocation } from '@docusaurus/router';
import { FloatingButton } from './FloatingButton';
import { SelectionMenu } from './SelectionMenu';
import { useTextSelection } from '../../hooks/useTextSelection';
import { chatService, type ChatMessage, type Citation } from '../../services/chatService';
import './ChatBot.css';

export interface ChatBotProps {
  apiUrl?: string;
}

export const ChatBot: React.FC<ChatBotProps> = ({ apiUrl }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedContext, setSelectedContext] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null); // Ref for textarea
  const location = useLocation();
  
  const { text: selectedText, rect: selectionRect } = useTextSelection();

  // Page context for display
  const [pageContext, setPageContext] = useState<string>('');

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height to recalculate
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]); // Auto-resize when input changes

  useEffect(() => {
    if (isOpen && typeof window !== 'undefined') {
      const path = window.location.pathname;
      // Extract readable context
      // Expected format: .../docs/part-XX-name/chapter-YY-name
      const parts = path.split('/').filter(p => p && p !== 'docs');
      
      const relevant = parts.filter(p => p.startsWith('part-') || p.startsWith('chapter-'));
      if (relevant.length > 0) {
           const ctx = relevant.map(p => {
               // Remove prefix numbering for cleaner display if needed, or just format
               // part-01-physical-ai -> Part 01 Physical Ai
               return p.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
           }).join(' > ');
           setPageContext(ctx);
      } else {
           setPageContext('');
      }
    }
  }, [isOpen, location]);

  // Scroll to bottom when chat opens (instant)
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
      }, 0);
    }
  }, [isOpen]);

  // Scroll to bottom when messages change (smooth)
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    setError(null);
  };

  const handleAskSelection = (text: string) => {
    setIsOpen(true);
    setSelectedContext(text);
    // Pre-fill input or send immediately?
    // Usually prompt user: "Ask about this..."
    setInput(`What does this mean: "${text.substring(0, 50)}..."?`);
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);
    
    // Capture and clear context for this message
    const context = selectedContext;
    setSelectedContext(null);

    try {
      // Use streaming for better UX
      let assistantMessage = '';
      const citations: Citation[] = [];

      for await (const event of chatService.sendMessageStreaming({
        message: userMessage.content,
        selected_text: context || undefined, // Send selection if available
        current_page_url: chatService.getCurrentPageUrl(),
      })) {
        if (event.type === 'content' && event.content) {
          assistantMessage += event.content;

          // Update the last message with accumulated content
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];

            if (lastMessage && lastMessage.role === 'assistant') {
              // Update existing assistant message
              lastMessage.content = assistantMessage;
            } else {
              // Add new assistant message
              newMessages.push({
                role: 'assistant',
                content: assistantMessage,
                citations: [],
              });
            }

            return newMessages;
          });
        } else if (event.type === 'citation' && event.citation) {
          citations.push(event.citation);
        } else if (event.type === 'done') {
          // Final update with all citations
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];

            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.citations = event.citations || citations;
            }

            return newMessages;
          });
        } else if (event.type === 'error') {
          throw new Error(event.error || 'Unknown error occurred');
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');

      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      <SelectionMenu 
        text={selectedText} 
        rect={selectionRect} 
        onAsk={handleAskSelection} 
      />
      <FloatingButton onClick={handleToggle} isOpen={isOpen} />

      {isOpen && (
        <div className="chatbot-container">
          <div className="chatbot-header">
            <h3 className="chatbot-title">Physical AI Assistant</h3>
            {pageContext && (
              <p className="chatbot-context-badge" style={{ fontSize: '0.75rem', opacity: 0.9, margin: '4px 0', background: 'rgba(255,255,255,0.2)', padding: '2px 6px', borderRadius: '4px', display: 'inline-block' }}>
                {pageContext}
              </p>
            )}
            <p className="chatbot-subtitle">Ask questions about the book</p>
          </div>

                  <div className="chatbot-messages">
                    {messages.length === 0 && (
                      <div className="chatbot-welcome">
                        <p>👋 Hi! I'm your Physical AI assistant.</p>
                        <p>Ask me anything about robotics, ROS2, sensors, or topics covered in this textbook.</p>
                      </div>
                    )}
                    
                    {messages.map((message, index) => (              <div
                key={index}
                className={`chatbot-message chatbot-message--${message.role}`}
              >
                <div className="chatbot-message-content">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {message.citations && message.citations.length > 0 && (
                  <div className="chatbot-citations">
                    <p className="chatbot-citations-title">Sources:</p>
                    {message.citations.map((citation, idx) => (
                      <a
                        key={idx}
                        href={citation.url}
                        className="chatbot-citation-link"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {citation.text || `${citation.chapter}, ${citation.section}`}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="chatbot-message chatbot-message--assistant">
                <div className="chatbot-loading">
                  <span className="chatbot-loading-dot"></span>
                  <span className="chatbot-loading-dot"></span>
                  <span className="chatbot-loading-dot"></span>
                </div>
              </div>
            )}

            {error && (
              <div className="chatbot-error">
                <p>{error}</p>
                <button onClick={() => setError(null)} className="chatbot-error-dismiss">
                  Dismiss
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {selectedContext && (
            <div className="chatbot-context-preview">
              <div className="chatbot-context-header">
                <span>Selected Context</span>
                <button onClick={() => setSelectedContext(null)}>×</button>
              </div>
              <p>"{selectedContext.substring(0, 100)}{selectedContext.length > 100 ? '...' : ''}"</p>
            </div>
          )}

          <div className="chatbot-input-container">
            <textarea
              ref={textareaRef} // Attach ref
              className="chatbot-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              // rows={1} // Removed for auto-sizing
              disabled={isLoading}
            />
            <button
              className="chatbot-send-button"
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              aria-label="Send message"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M2 10L18 2L10 18L8 11L2 10Z"
                  fill="currentColor"
                />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
};
