import os

from dotenv import load_dotenv
from calle import CalleClient


load_dotenv()

api_key = os.getenv("CALLE_API_KEY")

if not api_key:
    raise RuntimeError(
        "CALLE_API_KEY was not found. Check your .env file."
    )

client = CalleClient(api_key=api_key)

print("ConfirmCall environment loaded.")
print("CALL-E client initialized successfully.")
print("API key loaded: Yes")

client.close()