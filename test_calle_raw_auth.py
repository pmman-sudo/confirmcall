import os

import httpx
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("CALLE_API_KEY", "").strip()

print("=" * 60)
print("CALL-E RAW AUTH TEST")
print("=" * 60)

print("Key present:", bool(api_key))
print(
    "Whitespace clean:",
    api_key == api_key.strip()
    and not any(char.isspace() for char in api_key)
)

response = httpx.get(
    "https://api.heycall-e.com/v1/calls/call_confirmcall_authcheck",
    headers={
        "Authorization": f"Bearer {api_key}",
    },
    timeout=20,
)

print("HTTP status:", response.status_code)

if response.status_code == 401:
    print("❌ CALL-E rejected the API key.")

elif response.status_code == 403:
    print("⚠️ Key was recognized, but access was forbidden.")

elif response.status_code == 404:
    print("✅ Authentication succeeded.")
    print("The fake call ID does not exist, which is expected.")

else:
    print("Response:", response.text[:300])