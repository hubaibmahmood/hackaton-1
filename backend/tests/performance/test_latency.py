"""Performance latency validation."""
import pytest
import time
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_latency_validation():
    """Measure response time latency (T090)."""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        latencies = []
        
        # Warmup
        await client.get("/health")
        
        # Measure 5 requests
        for _ in range(5):
            start = time.time()
            response = await client.post(
                "/api/chat/",
                json={"message": "Explain sensors"}
            )
            latencies.append(time.time() - start)
            assert response.status_code == 200
            
        latencies.sort()
        p50 = latencies[len(latencies)//2]
        p95 = latencies[int(len(latencies)*0.95)]
        
        print(f"P50: {p50:.3f}s, P95: {p95:.3f}s")
        
        # Success criteria SC-002: < 10s
        assert p95 < 10.0
