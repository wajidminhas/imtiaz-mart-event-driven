import httpx
import asyncio
import sys

async def test_dapr_connectivity():
    """Test Dapr service invocation from within Order Service container"""
    
    tests = [
        ("Dapr Metadata", "http://localhost:3503/v1.0/metadata"),
        ("Product Service via Dapr", "http://localhost:3503/v1.0/invoke/product-service/method/health"),
        ("Product Service Direct", "http://product-service:8001/health"),
    ]
    
    for name, url in tests:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                print(f"✅ {name}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ {name}: {type(e).__name__}: {str(e)}")
        print()

if __name__ == "__main__":
    asyncio.run(test_dapr_connectivity())
