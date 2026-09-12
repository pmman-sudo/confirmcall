from services.calendar_service import (
    get_confirmcall_appointments,
    update_calendar_event,
)
from services.decision_service import (
    CallResult,
    apply_call_result,
)


appointments = get_confirmcall_appointments(hours=48)

if not appointments:
    raise RuntimeError(
        "No ConfirmCall appointments found."
    )

appointment = appointments[0]

print("BEFORE")
print(f"Status: {appointment.status.value}")

fake_result = CallResult(
    outcome="confirmed",
    call_id="demo-call-001",
)

updated_appointment = apply_call_result(
    appointment,
    fake_result,
)

update_calendar_event(updated_appointment)

print("\nAFTER")
print(f"Status: {updated_appointment.status.value}")
print("Google Calendar updated successfully.")