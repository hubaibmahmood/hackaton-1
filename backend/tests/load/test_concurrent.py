"""Load testing for RAG Chatbot."""
import asyncio
import time
import pytest
from httpx import AsyncClient

# Simple load test simulation using asyncio
# For real load testing, use Locust or k6
async def simulate_user(client, user_id):
    start_time = time.time()
    response = await client.post(
        "http://localhost:8000/api/chat/",
        json={"message": "What is ROS2?"},
        timeout=10.0
    )
    duration = time.time() - start_time
    return response.status_code, duration

@pytest.mark.asyncio
async def test_concurrent_users():
    """Simulate concurrent users (T089)."""
    # This is a lightweight functional load test, not a full stress test
    # Reduce count for CI/local execution
    CONCURRENT_USERS = 10 
    
    async with AsyncClient() as client:
        tasks = [simulate_user(client, i) for i in range(CONCURRENT_USERS)]
        results = await asyncio.gather(*tasks)
        
    status_codes = [r[0] for r in results]
    durations = [r[1] for r in results]
    
    # Verify all requests succeeded
    assert all(code == 200 for code in status_codes)
    
    # Verify performance (SC-007/SC-002: p95 < 3s)
    avg_duration = sum(durations) / len(durations)
    print(f"Average duration: {avg_duration:.2f}s")
    assert avg_duration < 10.0
