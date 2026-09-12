from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from app import process_appointment

from models.appointment import AppointmentStatus
from services.calendar_service import (
    get_confirmcall_appointments,
    reset_demo_appointments,
)


DISPLAY_TIMEZONE = ZoneInfo("Africa/Lagos")


st.set_page_config(
    page_title="ConfirmCall",
    page_icon="☎️",
    layout="wide",
)


st.title("☎️ ConfirmCall")
st.subheader("AI Appointment Confirmation Agent")

st.caption(
    "Autonomous appointment confirmation and recovery "
    "for service businesses."
)

st.info(
    "Google Calendar → CALL-E Voice Agent → "
    "Structured Decision → Calendar Writeback"
)

appointments = get_confirmcall_appointments(hours=48)


confirmed_count = sum(
    1
    for appointment in appointments
    if appointment.status == AppointmentStatus.CONFIRMED
)

cancelled_count = sum(
    1
    for appointment in appointments
    if appointment.status == AppointmentStatus.CANCELLED
)

needs_action_count = sum(
    1
    for appointment in appointments
    if appointment.status
    in {
        AppointmentStatus.RESCHEDULE_REQUESTED,
        AppointmentStatus.NEEDS_HUMAN,
        AppointmentStatus.NO_ANSWER,
    }
)

pending_count = sum(
    1
    for appointment in appointments
    if appointment.status == AppointmentStatus.PENDING
)

processed_count = (
    confirmed_count
    + cancelled_count
    + needs_action_count
)

# Demo estimate only.
AVERAGE_APPOINTMENT_VALUE = 100

estimated_revenue_protected = (
    confirmed_count * AVERAGE_APPOINTMENT_VALUE
)

confirmation_rate = (
    (confirmed_count / processed_count) * 100
    if processed_count
    else 0
)


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Appointments",
    len(appointments),
)

col2.metric(
    "Confirmed",
    confirmed_count,
)

col3.metric(
    "Cancelled",
    cancelled_count,
)

col4.metric(
    "Pending",
    pending_count,
)

col5.metric(
    "Needs Action",
    needs_action_count,
)

st.subheader("Business Impact")

impact1, impact2, impact3 = st.columns(3)

impact1.metric(
    "Appointments Protected",
    confirmed_count,
)

impact2.metric(
    "Estimated Revenue Protected",
    f"${estimated_revenue_protected:,}",
)

impact3.metric(
    "Confirmation Rate",
    f"{confirmation_rate:.0f}%",
)

st.caption(
    "Revenue protected is a demo estimate based on "
    f"${AVERAGE_APPOINTMENT_VALUE} average appointment value."
)

st.divider()

st.subheader("Upcoming Appointments")


STATUS_LABELS = {
    AppointmentStatus.PENDING: "⏳ Pending",
    AppointmentStatus.CONFIRMED: "✅ Confirmed",
    AppointmentStatus.CANCELLED: "❌ Cancelled",
    AppointmentStatus.RESCHEDULE_REQUESTED: "🟡 Reschedule Requested",
    AppointmentStatus.NO_ANSWER: "⚪ No Answer",
    AppointmentStatus.NEEDS_HUMAN: "🔴 Needs Human",
}


rows = []

for appointment in appointments:

    local_time = appointment.start_time.astimezone(
        DISPLAY_TIMEZONE
    )

    rows.append(
        {
            "Customer": appointment.customer_name,
            "Service": appointment.service_name,
            "Date": local_time.strftime("%b %d, %Y"),
            "Time": local_time.strftime("%I:%M %p"),
            "Status": STATUS_LABELS.get(
                appointment.status,
                appointment.status.value,
            ),
            "Requested Time": (
                appointment.requested_time
                or "-"
            ),
        }
    )


if rows:

    dataframe = pd.DataFrame(rows)

    st.dataframe(
        dataframe,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No ConfirmCall appointments found "
        "in the next 48 hours."
    )


st.divider()


left, right = st.columns(2)

with left:

    st.subheader("Automation")

    st.write(
        "ConfirmCall scans upcoming appointments, "
        "contacts customers through CALL-E, "
        "and writes the outcome back to Google Calendar."
    )


with right:

    st.subheader("Current Demo")

    st.write(
        "The Calendar and decision engine are live. "
        "Phone outcomes are currently simulated while "
        "the live CALL-E test number is being resolved."
    )


st.divider()

st.subheader("Demo Controls")

st.write(
    "Reset the demo appointments to pending, then run "
    "ConfirmCall to process them."
)

reset_col, run_col = st.columns(2)


with reset_col:

    if st.button(
        "🔄 Reset Demo",
        width="stretch",
    ):

        with st.spinner(
            "Resetting demo appointments..."
        ):

            count = reset_demo_appointments()

        st.success(
            f"Reset {count} demo appointment(s) to pending."
        )

        st.rerun()


with run_col:

    if st.button(
        "☎️ Run ConfirmCall",
        type="primary",
        width="stretch",
    ):

        pending = [
            appointment
            for appointment in appointments
            if appointment.status == AppointmentStatus.PENDING
        ]

        if not pending:

            st.info(
                "There are no pending appointments to process."
            )

        else:

            progress = st.progress(0)

            status_box = st.empty()

            total = len(pending)

            for index, appointment in enumerate(
                pending,
                start=1,
            ):

                status_box.info(
                    f"Processing "
                    f"{appointment.customer_name} — "
                    f"{appointment.service_name}"
                )

                process_appointment(
                    appointment
                )

                progress.progress(
                    index / total
                )

            status_box.success(
                f"Processed {total} appointment(s)."
            )

            st.success(
                "Google Calendar updated successfully."
            )

            st.rerun()