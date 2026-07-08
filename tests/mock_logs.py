import httpx
import asyncio

async def test_self_healing_flow():
    url = "http://127.0.0.1:8000/api/v1/intercept"
    
    mock_payload = {
        "repo_url": "https://github.com/apurba-labs/app-service",
        "branch": "main",
        "commit_sha": "a4f892c900e1215db84f",
        "error_log": "Traceback (most recent call last):\nFile 'main.py', line 2\nfrom app.utils.helpers import parse\nModuleNotFoundError: No module named 'httpx'"
    }
    
    print("[TEST] Sending simulated pipeline error log payload to engine...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=mock_payload, timeout=5.0)
            print(f"[RESPONSE STATUS] {response.status_code}")
            print("[RESPONSE JSON OUTPUT]:")
            print(response.text)
        except Exception as e:
            print(f"[TEST FAILED] Engine server offline. Run 'python -m app.main' first. Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_self_healing_flow())