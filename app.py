from zoneinfo import ZoneInfo

from models.appointment import AppointmentStatus

from services.calendar_service import (
    get_confirmcall_appointments,
    update_calendar_event,
)

from services.calle_service import make_confirmation_call

from services.decision_service import (
    CallResult,
    apply_call_result,
)


DRY_RUN = True

DISPLAY_TIMEZONE = ZoneInfo("Africa/Lagos")


DEMO_RESULTS = {
    "Alice Demo": CallResult(
        outcome="confirmed",
        customer_notes="Customer confirmed attendance.",
        call_id="demo-call-alice",
    ),

    "Brian Demo": CallResult(
        outcome="cancelled",
        customer_notes="Customer requested cancellation.",
        call_id="demo-call-brian",
    ),

    "Clara Demo": CallResult(
        outcome="reschedule_requested",
        requested_time="Monday at 2:00 PM",
        customer_notes="Customer requested a new appointment time.",
        call_id="demo-call-clara",
    ),
}


def get_demo_result(appointment):
    result = DEMO_RESULTS.get(appointment.customer_name)

    if result:
        return result

    return CallResult(
        outcome="unknown",
        customer_notes="No demo response configured.",
        call_id="demo-call-unknown",
    )


def process_appointment(appointment):
    local_time = appointment.start_time.astimezone(
        DISPLAY_TIMEZONE
    )

    print()
    print("=" * 60)
    print(f"Customer: {appointment.customer_name}")
    print(f"Service: {appointment.service_name}")
    print(
        f"Time: "
        f"{local_time.strftime('%A, %B %d at %I:%M %p')}"
    )
    print(f"Status: {appointment.status.value}")

    if appointment.status != AppointmentStatus.PENDING:
        print("Skipping: appointment already processed.")
        return

    if DRY_RUN:
        print("DRY RUN: simulating CALL-E conversation.")

        result = get_demo_result(appointment)

    else:
        print("Starting CALL-E call...")
        result = make_confirmation_call(appointment)

    print(f"Call outcome: {result.outcome}")

    if result.requested_time:
        print(f"Requested time: {result.requested_time}")

    updated = apply_call_result(
        appointment,
        result,
    )

    update_calendar_event(updated)

    print(
        f"Calendar updated: "
        f"{updated.status.value}"
    )


def main():
    print()
    print("CONFIRMCALL")
    print("AI Appointment Confirmation Agent")
    print("=" * 60)

    appointments = get_confirmcall_appointments(
        hours=48
    )

    print(
        f"Found {len(appointments)} "
        f"ConfirmCall appointment(s)."
    )

    for appointment in appointments:
        process_appointment(appointment)

    print()
    print("=" * 60)
    print("ConfirmCall run complete.")


if __name__ == "__main__":
    main()