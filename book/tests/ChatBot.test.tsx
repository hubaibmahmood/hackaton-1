import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatBot } from '../src/components/ChatBot/ChatBot';
import { chatService } from '../src/services/chatService';

// Mock chatService
jest.mock('../src/services/chatService', () => ({
  chatService: {
    sendMessageStreaming: jest.fn(),
    getCurrentPageUrl: jest.fn().mockReturnValue('/docs/intro'),
  },
}));

describe('ChatBot Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders floating button initially', () => {
    render(<ChatBot />);
    const button = screen.getByLabelText(/open chatbot/i);
    expect(button).toBeInTheDocument();
    // Chat window should not be visible
    expect(screen.queryByText('Physical AI Assistant')).not.toBeInTheDocument();
  });

  test('opens chat window on button click', () => {
    render(<ChatBot />);
    const button = screen.getByLabelText(/open chatbot/i);
    
    fireEvent.click(button);
    
    expect(screen.getByText('Physical AI Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask a question...')).toBeInTheDocument();
  });

  test('sends message and displays response', async () => {
    // Mock streaming response
    const mockStream = (async function* () {
        yield { type: 'content', content: 'Hello ' };
        yield { type: 'content', content: 'World' };
        yield { type: 'done' };
    })();
    
    (chatService.sendMessageStreaming as jest.Mock).mockReturnValue(mockStream);

    render(<ChatBot />);
    
    // Open chat
    fireEvent.click(screen.getByLabelText(/open chatbot/i));
    
    // Type message
    const input = screen.getByPlaceholderText('Ask a question...');
    fireEvent.change(input, { target: { value: 'Hi' } });
    
    // Send
    const sendButton = screen.getByLabelText('Send message');
    fireEvent.click(sendButton);
    
    // Check user message
    expect(screen.getByText('Hi')).toBeInTheDocument();
    
    // Check assistant response (waits for stream)
    await waitFor(() => {
        expect(screen.getByText('Hello World')).toBeInTheDocument();
    });
  });
});
