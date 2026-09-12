from services.calendar_service import get_confirmcall_appointments


appointments = get_confirmcall_appointments(hours=48)

print(
    f"\nFound {len(appointments)} ConfirmCall appointment(s).\n"
)

for appointment in appointments:

    print(f"Event ID: {appointment.event_id}")
    print(f"Customer: {appointment.customer_name}")
    print(f"Phone: {appointment.customer_phone}")
    print(f"Service: {appointment.service_name}")
    print(f"Time: {appointment.start_time}")
    print(f"Status: {appointment.status.value}")
    print(
        f"Requested Time: "
        f"{appointment.requested_time or '-'}"
    )
    print(
        f"Call ID: "
        f"{appointment.call_id or '-'}"
    )
    print("-" * 50)