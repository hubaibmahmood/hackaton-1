/**
 * Main ChatBot component with ChatKit integration
 */
import React, { useState, useRef, useEffect } from 'react';
import { FloatingButton } from './FloatingButton';
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    setError(null);
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

    try {
      // Use streaming for better UX
      let assistantMessage = '';
      const citations: Citation[] = [];

      for await (const event of chatService.sendMessageStreaming({
        message: userMessage.content,
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

  if (!isOpen) {
    return <FloatingButton onClick={handleToggle} isOpen={isOpen} />;
  }

  return (
    <>
      <FloatingButton onClick={handleToggle} isOpen={isOpen} />

      <div className="chatbot-container">
        <div className="chatbot-header">
          <h3 className="chatbot-title">Physical AI Assistant</h3>
          <p className="chatbot-subtitle">Ask questions about the book</p>
        </div>

        <div className="chatbot-messages">
          {messages.length === 0 && (
            <div className="chatbot-welcome">
              <p>👋 Hi! I'm your Physical AI assistant.</p>
              <p>Ask me anything about robotics, ROS2, sensors, or topics covered in this textbook.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`chatbot-message chatbot-message--${message.role}`}
            >
              <div className="chatbot-message-content">
                {message.content}
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

        <div className="chatbot-input-container">
          <textarea
            className="chatbot-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question..."
            rows={1}
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
    </>
  );
};
