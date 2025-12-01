"""RAG Agent using OpenAI Agents SDK."""
import logging
from typing import Optional, AsyncGenerator

from agents import Agent, Runner, RunConfig, SQLiteSession

from src.config import settings
from src.agents.tools import search_book_content

logger = logging.getLogger(__name__)


class RAGAgent:
    """RAG Agent for answering questions about the Physical AI textbook using OpenAI Agents SDK."""

    def __init__(self) -> None:
        """Initialize the RAG agent with OpenAI Agents SDK."""

        # Agent instructions
        self.instructions = """You are a helpful assistant for the Physical AI textbook.

Your role:
- Answer questions about Physical AI, robotics, ROS2, LIDAR, sensors, and related topics
- ALWAYS cite sources with chapter and section references from the search results
- Use the search_book_content tool to find relevant information before answering
- Stay within the book's scope - acknowledge when questions are outside the book

How to use the search tool:
1. When a user asks a question, ALWAYS call search_book_content first
2. Use the search results to formulate your answer
3. Include specific citations from the results

Citation format:
- Include chapter, section, and URL for every fact from the search results
- Format: "According to [Citation Source]: [fact] ([URL])"
- Provide multiple citations when relevant
- ALWAYS include URLs from the search results

Out-of-scope handling:
- If search returns "No relevant content found", say: "This question appears to be outside the book's scope. I can only answer questions about Physical AI, robotics, ROS2, sensors, and topics covered in the textbook."
- If search results have low relevance (< 0.7 similarity), acknowledge uncertainty

Conversation style:
- Be concise but complete
- Use technical terminology appropriately from the book
- Provide examples from search results when helpful
- Maintain context from previous messages in the conversation
- Always prioritize information from the search results over general knowledge
"""

        # Create agent with tools
        self.agent = Agent(
            name="Physical AI Assistant",
            instructions=self.instructions,
            model=settings.chat_model,  # gpt-4o-mini for cost optimization
            tools=[search_book_content],
        )

    async def run(
        self,
        user_message: str,
        session_id: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> dict:
        """Run the agent with a user message.

        Args:
            user_message: User's question
            session_id: Session identifier for conversation tracking
            conversation_history: Previous conversation messages (optional)

        Returns:
            Agent response with answer and citations
        """
        try:
            # Create session for conversation history
            # Note: We could integrate with our Postgres sessions here
            session = SQLiteSession(session_id)

            # If conversation history provided, populate session
            if conversation_history:
                for msg in conversation_history:
                    # Session will be auto-populated by Runner
                    pass

            # Run agent
            result = await Runner.run(
                starting_agent=self.agent,
                input=user_message,
                session=session,
                config=RunConfig(
                    model=settings.chat_model,
                    max_turns=10,
                ),
            )

            # Extract answer and citations
            answer = result.final_output or "No response generated."

            # Extract citations from tool results if available
            citations = []
            if hasattr(result, 'items'):
                for item in result.items:
                    if hasattr(item, 'type') and item.type == 'tool_call':
                        # Citations are embedded in the agent's response
                        # We'll parse them from the final output
                        pass

            return {
                "answer": answer,
                "citations": citations,  # Will be extracted from answer text
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"Error running agent: {e}", exc_info=True)
            raise

    async def run_streaming(
        self,
        user_message: str,
        session_id: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> AsyncGenerator[dict, None]:
        """Run the agent with streaming responses.

        Args:
            user_message: User's question
            session_id: Session identifier
            conversation_history: Previous conversation messages (optional)

        Yields:
            Chunks of the response with type indicators
        """
        try:
            # Create session for conversation history
            session = SQLiteSession(session_id)

            # If conversation history provided, populate session
            if conversation_history:
                for msg in conversation_history:
                    # Session will be auto-populated by Runner
                    pass

            # Run agent with streaming
            result = await Runner.run_streamed(
                starting_agent=self.agent,
                input=user_message,
                session=session,
                config=RunConfig(
                    model=settings.chat_model,
                    max_turns=10,
                ),
            )

            # Stream events
            citations = []
            accumulated_content = ""

            async for event in result.stream_events():
                # Token-by-token text deltas
                if event.type == "raw_response_event":
                    # Check if it's a text delta
                    if hasattr(event, 'delta') and event.delta:
                        accumulated_content += event.delta
                        yield {
                            "type": "content",
                            "content": event.delta,
                        }

                # Tool call events
                elif event.type == "run_item_event":
                    if hasattr(event.item, 'type'):
                        if event.item.type == "tool_call_item":
                            tool_name = getattr(event.item, 'name', 'unknown')
                            logger.info(f"Tool called: {tool_name}")
                            yield {
                                "type": "tool_call",
                                "tool_name": tool_name,
                            }
                        elif event.item.type == "message":
                            # Message completed
                            pass

                # Agent handoff events (for multi-agent scenarios)
                elif event.type == "agent_updated":
                    logger.info(f"Agent changed to: {event.agent.name}")

            # Yield final message
            yield {
                "type": "done",
                "citations": citations,
                "full_content": accumulated_content,
            }

        except Exception as e:
            logger.error(f"Error in streaming agent: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e),
            }


# Global RAG agent instance
rag_agent = RAGAgent()
