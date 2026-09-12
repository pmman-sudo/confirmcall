# ☎️ ConfirmCall

> AI-powered appointment confirmation calls that turn customer conversations into structured calendar actions.

ConfirmCall helps appointment-based businesses reduce no-shows by automatically contacting customers before upcoming appointments, understanding whether they will attend, cancel, or request another time, and writing the result back to Google Calendar.

Built for the **CALL-E: Your Code Is Calling** hackathon.

---

## The Problem

No-shows cost appointment-based businesses time and revenue.

Salons, consultants, clinics, repair services, tutors, and other service businesses often depend on staff manually calling customers to confirm appointments.

That process is:

- repetitive,
- difficult to scale,
- easy to forget,
- and expensive when customers simply do not show up.

ConfirmCall turns that manual workflow into an AI-powered automation.

---

## The Solution

ConfirmCall connects:

**Google Calendar → CALL-E → Decision Engine → Calendar Writeback → Dashboard**

The system:

1. Reads upcoming appointments from Google Calendar.
2. Identifies appointments configured for ConfirmCall.
3. Builds a personalized confirmation conversation.
4. Uses CALL-E to contact the customer.
5. Extracts a structured outcome from the conversation.
6. Classifies the appointment.
7. Updates Google Calendar automatically.
8. Displays the results in a Streamlit dashboard.

---

## Supported Outcomes

ConfirmCall understands the following appointment states:

- ✅ **Confirmed**
- ❌ **Cancelled**
- 🟡 **Reschedule Requested**
- ⚪ **No Answer**
- 🔴 **Needs Human Review**
- ⏳ **Pending**

For reschedule requests, ConfirmCall records the customer's preferred time without automatically promising that the new slot is available.

---

## Architecture

```mermaid
flowchart TD
    A[Google Calendar] --> B[Appointment Scanner]
    B --> C[ConfirmCall Orchestrator]
    C --> D[CALL-E Voice Agent]
    D --> E[Structured Call Result]
    E --> F[Decision Engine]
    F --> G[Google Calendar Writeback]
    G --> H[Streamlit Dashboard]

    E -->|Confirmed| I[Confirmed]
    E -->|Cancelled| J[Cancelled]
    E -->|Reschedule| K[Human Review / New Time Request]
    E -->|No Answer| L[Follow-up Required]


confirmcall/
│
├── app.py
├── live_call_test.py
├── seed_demo_events.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── dashboard/
│   └── dashboard.py
│
├── models/
│   ├── __init__.py
│   └── appointment.py
│
├── services/
│   ├── __init__.py
│   ├── calendar_service.py
│   ├── calle_service.py
│   └── decision_service.py
│
├── tests/
│   ├── __init__.py
│   └── test_decision.py
│
├── test_calendar.py
├── test_calle.py
└── test_writeback.py    