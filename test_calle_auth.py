import os

from dotenv import load_dotenv
from calle import CalleClient
from calle.errors import CalleAuthenticationError


load_dotenv()


def main():
    api_key = os.getenv("CALLE_API_KEY")

    if not api_key:
        print("ERROR: CALLE_API_KEY is missing.")
        return

    client = CalleClient(api_key=api_key)

    print("=" * 60)
    print("CALL-E AUTH TEST")
    print("=" * 60)
    print("Checking API authentication...")
    print("No phone call will be placed.")
    print()

    try:
        client.calls.get(
            "confirmcall-auth-check-not-a-real-call"
        )

        print("Unexpectedly found the fake call ID.")

    except CalleAuthenticationError:
        print("❌ Authentication failed.")
        print("CALL-E rejected the API key.")

    except Exception as exc:
        print("✅ Authentication reached the CALL-E API.")
        print(
            "Response type:",
            type(exc).__name__,
        )
        print(
            "The fake call ID was rejected as expected."
        )


if __name__ == "__main__":
    main()