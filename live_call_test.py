import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from models.appointment import Appointment
from services.calle_service import make_confirmation_call


load_dotenv()


def main():
    phone = os.getenv("CALLE_TEST_PHONE")

    if not phone:
        print("ERROR: CALLE_TEST_PHONE is missing from .env")
        print(
            "Add an authorized CALL-E-supported test number "
            "before running this script."
        )
        return

    appointment = Appointment(
        event_id="live-test-001",
        customer_name="Test Customer",
        customer_phone=phone,
        service_name="Demo Consultation",
        start_time=(
            datetime.now(timezone.utc)
            + timedelta(days=1)
        ),
    )

    print("=" * 60)
    print("CONFIRMCALL LIVE TEST")
    print("=" * 60)
    print("This WILL place one real CALL-E phone call.")
    print("Use only a number you own or have permission to call.")
    print()

    confirmation = input(
        "Type CALL to continue: "
    )

    if confirmation != "CALL":
        print("Live test cancelled.")
        return

    print()
    print("Starting CALL-E call...")

    result = make_confirmation_call(
        appointment
    )

    print()
    print("=" * 60)
    print("CALL RESULT")
    print("=" * 60)
    print(f"Outcome: {result.outcome}")
    print(
        f"Requested time: "
        f"{result.requested_time or '-'}"
    )
    print(
        f"Customer notes: "
        f"{result.customer_notes or '-'}"
    )
    print(
        f"Call ID: "
        f"{result.call_id or '-'}"
    )


if __name__ == "__main__":
    main()