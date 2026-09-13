import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# Project imports
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app import DRY_RUN, process_appointment

from models.appointment import Appointment, AppointmentStatus

from services.calendar_service import (
    get_confirmcall_appointments,
    reset_demo_appointments,
)

from services.decision_service import (
    CallResult,
    apply_call_result,
)


# Configuration

DISPLAY_TIMEZONE = ZoneInfo("Africa/Lagos")

# Streamlit Cloud does not contain credentials.json.
# That automatically activates the safe public demo.
PUBLIC_DEMO = (
    os.getenv("PUBLIC_DEMO", "").lower() == "true"
    or not (ROOT_DIR / "credentials.json").exists()
)

AVERAGE_APPOINTMENT_VALUE = 100

# Public demo data
def create_public_demo_appointments():
    """
    Create fictional appointments for the public Streamlit deployment.
    No real phone numbers, Calendar credentials, or live CALL-E calls are used.
    """

    tomorrow = datetime.now(DISPLAY_TIMEZONE) + timedelta(days=1)

    return [
        Appointment(
            event_id="public-demo-alice",
            customer_name="Alice Demo",
            customer_phone="+12025550123",
            service_name="Haircut Appointment",
            start_time=tomorrow.replace(
                hour=10,
                minute=0,
                second=0,
                microsecond=0,
            ),
            status=AppointmentStatus.PENDING,
        ),
        Appointment(
            event_id="public-demo-brian",
            customer_name="Brian Demo",
            customer_phone="+12025550124",
            service_name="Consultation",
            start_time=tomorrow.replace(
                hour=13,
                minute=0,
                second=0,
                microsecond=0,
            ),
            status=AppointmentStatus.PENDING,
        ),
        Appointment(
            event_id="public-demo-clara",
            customer_name="Clara Demo",
            customer_phone="+12025550125",
            service_name="Service Visit",
            start_time=tomorrow.replace(
                hour=16,
                minute=0,
                second=0,
                microsecond=0,
            ),
            status=AppointmentStatus.PENDING,
        ),
    ]


def get_public_demo_appointments():
    if "public_demo_appointments" not in st.session_state:
        st.session_state["public_demo_appointments"] = (
            create_public_demo_appointments()
        )

    return st.session_state["public_demo_appointments"]


def reset_public_demo():
    appointments = create_public_demo_appointments()

    st.session_state["public_demo_appointments"] = appointments

    return len(appointments)


def process_public_demo_appointment(appointment):
    """
    Feed fictional CALL-E outcomes through the real ConfirmCall
    decision engine.
    """

    demo_results = {
        "Alice Demo": CallResult(
            outcome="confirmed",
            customer_notes="Customer confirmed attendance.",
            call_id="demo-call-alice",
        ),
        "Brian Demo": CallResult(
            outcome="cancelled",
            customer_notes="Customer cancelled the appointment.",
            call_id="demo-call-brian",
        ),
        "Clara Demo": CallResult(
            outcome="reschedule_requested",
            requested_time="Monday at 2:00 PM",
            customer_notes="Customer requested another time.",
            call_id="demo-call-clara",
        ),
    }

    result = demo_results.get(appointment.customer_name)

    if result is None:
        result = CallResult(
            outcome="unknown",
            customer_notes="Demo outcome unavailable.",
            call_id="demo-call-unknown",
        )

    apply_call_result(
        appointment,
        result,
    )

    return {
        "success": True,
        "appointment": appointment,
    }


# Streamlit setup
st.set_page_config(
    page_title="ConfirmCall",
    page_icon="☎️",
    layout="wide",
)


if "last_action" not in st.session_state:
    st.session_state["last_action"] = (
        "No dashboard action has been run in this session."
    )


# Mode banner
if PUBLIC_DEMO:

    st.warning(
        "🟡 PUBLIC DEMO MODE — This deployment uses fictional "
        "appointments and simulated CALL-E outcomes. "
        "Live CALL-E runtime validation was completed separately "
        "with an authorized recipient."
    )

elif DRY_RUN:

    st.warning(
        "🟡 DEMO MODE — CALL-E outcomes are simulated. "
        "Google Calendar reads and writebacks are real."
    )

else:

    st.success(
        "🟢 LIVE MODE — ConfirmCall will place real CALL-E calls."
    )


# Header
st.title("☎️ ConfirmCall")

st.subheader(
    "AI Appointment Confirmation Agent"
)

st.caption(
    f"Last action: {st.session_state['last_action']}"
)

st.info(
    "Google Calendar → CALL-E Voice Agent → "
    "Structured Decision → Calendar Writeback → Dashboard"
)



# Load appointments
if PUBLIC_DEMO:

    appointments = get_public_demo_appointments()

else:

    appointments = get_confirmcall_appointments(
        hours=48
    )



# Metrics
confirmed_count = sum(
    1
    for appointment in appointments
    if appointment.status
    == AppointmentStatus.CONFIRMED
)

cancelled_count = sum(
    1
    for appointment in appointments
    if appointment.status
    == AppointmentStatus.CANCELLED
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
    if appointment.status
    == AppointmentStatus.PENDING
)

processed_count = (
    confirmed_count
    + cancelled_count
    + needs_action_count
)

estimated_revenue_protected = (
    confirmed_count
    * AVERAGE_APPOINTMENT_VALUE
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



# Business impact
st.subheader(
    "Business Impact"
)

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



# Appointment table
st.subheader(
    "Upcoming Appointments"
)


STATUS_LABELS = {
    AppointmentStatus.PENDING:
        "⏳ Pending",

    AppointmentStatus.CONFIRMED:
        "✅ Confirmed",

    AppointmentStatus.CANCELLED:
        "❌ Cancelled",

    AppointmentStatus.RESCHEDULE_REQUESTED:
        "🟡 Reschedule Requested",

    AppointmentStatus.NO_ANSWER:
        "⚪ No Answer",

    AppointmentStatus.NEEDS_HUMAN:
        "🔴 Needs Human",
}


rows = []

for appointment in appointments:

    local_time = appointment.start_time.astimezone(
        DISPLAY_TIMEZONE
    )

    rows.append(
        {
            "Customer":
                appointment.customer_name,

            "Service":
                appointment.service_name,

            "Date":
                local_time.strftime(
                    "%b %d, %Y"
                ),

            "Time":
                local_time.strftime(
                    "%I:%M %p"
                ),

            "Status":
                STATUS_LABELS.get(
                    appointment.status,
                    appointment.status.value,
                ),

            "Requested Time":
                appointment.requested_time
                or "-",
        }
    )


if rows:

    dataframe = pd.DataFrame(
        rows
    )

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



# Audit trail
st.divider()

st.subheader(
    "Automation Audit"
)

st.caption(
    "Call IDs provide traceability between appointment outcomes "
    "and the voice-agent execution that produced them. "
    "Public-demo IDs are fictional."
)

audit_rows = []

for appointment in appointments:

    audit_rows.append(
        {
            "Customer":
                appointment.customer_name,

            "Service":
                appointment.service_name,

            "Status":
                appointment.status.value,

            "Requested Time":
                appointment.requested_time
                or "-",

            "Call ID":
                appointment.call_id
                or "-",
        }
    )


if audit_rows:

    audit_df = pd.DataFrame(
        audit_rows
    )

    st.dataframe(
        audit_df,
        width="stretch",
        hide_index=True,
    )



# Explanation
left, right = st.columns(2)


with left:

    st.subheader(
        "How It Works"
    )

    st.write(
        "ConfirmCall discovers upcoming appointments, "
        "prepares a CALL-E confirmation task, converts the "
        "customer outcome into a structured decision, and "
        "updates the business workflow."
    )

    if PUBLIC_DEMO:

        st.caption(
            "This public deployment uses fictional appointments "
            "and feeds simulated CALL-E outcomes through the real "
            "ConfirmCall decision engine."
        )


with right:

    st.subheader(
        "Current Demo Status"
    )

    st.write(
        "Live CALL-E runtime validation has been completed "
        "with an authorized recipient in a supported region. "
        "Real outbound calls rang, connected, executed the "
        "voice agent, and returned structured runtime results."
    )

    st.write(
        "This public deployment uses safe simulated outcomes "
        "so judges can repeatedly explore the workflow without "
        "placing unnecessary phone calls."
    )



# Demo controls
st.divider()

st.subheader(
    "Demo Controls"
)

st.write(
    "Reset the appointments to pending, then run "
    "ConfirmCall to process them."
)


reset_col, run_col = st.columns(2)



# Reset

with reset_col:

    if st.button(
        "🔄 Reset Demo",
        width="stretch",
    ):

        with st.spinner(
            "Resetting demo appointments..."
        ):

            if PUBLIC_DEMO:

                count = reset_public_demo()

            else:

                count = reset_demo_appointments()

        st.session_state["last_action"] = (
            f"Reset {count} demo appointment(s) "
            "to pending."
        )

        st.rerun()



# Run ConfirmCall
with run_col:

    if st.button(
        "☎️ Run ConfirmCall",
        type="primary",
        width="stretch",
    ):

        pending = [
            appointment
            for appointment in appointments
            if appointment.status
            == AppointmentStatus.PENDING
        ]

        if not pending:

            st.info(
                "There are no pending appointments "
                "to process."
            )

        else:

            progress = st.progress(0)

            status_box = st.empty()

            total = len(pending)

            successful = 0
            failed = 0


            for index, appointment in enumerate(
                pending,
                start=1,
            ):

                status_box.info(
                    f"Processing "
                    f"{appointment.customer_name} — "
                    f"{appointment.service_name}"
                )


                if PUBLIC_DEMO:

                    result = (
                        process_public_demo_appointment(
                            appointment
                        )
                    )

                else:

                    result = process_appointment(
                        appointment
                    )


                if (
                    result
                    and result.get("success")
                ):

                    successful += 1

                else:

                    failed += 1


                progress.progress(
                    index / total
                )


            if failed == 0:

                st.session_state[
                    "last_action"
                ] = (
                    f"Processed {successful} "
                    "appointment(s) successfully."
                )

            else:

                st.session_state[
                    "last_action"
                ] = (
                    f"Processed {successful} "
                    "successfully. "
                    f"{failed} require human review."
                )


            st.rerun()