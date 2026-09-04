"""
AI Appointment Assistant — Controlled Backend Tools & Slot Management
----------------------------------------------------------------------
Provides secure, deterministic functions for:
- Doctor and specialist discovery
- Slot searching with ranking (preferred date, time, distance, earliest slot)
- Appointment creation, rescheduling, and cancellation
- Health record and medication retrieval
- Symptom-to-specialist routing with strict non-diagnostic guardrails
"""

import re
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from db import db_save_appointment, db_get_appointments, db_cancel_appointment

# Doctor Directory with hospitals, specialties, distance, and schedule
DOCTORS_DIRECTORY: List[Dict[str, Any]] = [
    {
        "id": "DOC-01",
        "name": "Dr. Vikramaditya Rao",
        "title": "M.S. Ortho, Fellow Joint Replacement",
        "specialty": "Orthopedic Surgeon",
        "department": "Orthopedics & Joint Surgery",
        "hospital": "Apollo Joint Replacement Institute",
        "address": "Apollo Hospitals, Sector 12, Navi Mumbai",
        "distance_km": 2.4,
        "rating": 4.9,
        "experience_years": 18,
        "consultation_fee": 1200,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "slots": ["09:30 AM", "11:00 AM", "04:30 PM", "05:30 PM", "06:30 PM"]
    },
    {
        "id": "DOC-02",
        "name": "Dr. Arvind Sharma",
        "title": "M.D. Internal Medicine",
        "specialty": "General Physician",
        "department": "General Medicine",
        "hospital": "City Care Polyclinic & Wellness",
        "address": "City Care Clinic, Main Road, Navi Mumbai",
        "distance_km": 1.2,
        "rating": 4.8,
        "experience_years": 14,
        "consultation_fee": 600,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "slots": ["10:00 AM", "11:30 AM", "05:00 PM", "05:30 PM", "06:00 PM", "07:00 PM", "08:00 PM"]
    },
    {
        "id": "DOC-03",
        "name": "Dr. Meera Nambiar",
        "title": "M.S. General & Laparoscopic Surgery",
        "specialty": "General Surgeon",
        "department": "General & Laparoscopic Surgery",
        "hospital": "Fortis Healthcare Superspecialty",
        "address": "Fortis Hospital, Mulund West, Mumbai",
        "distance_km": 4.8,
        "rating": 4.9,
        "experience_years": 16,
        "consultation_fee": 1000,
        "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
        "slots": ["11:00 AM", "03:00 PM", "05:00 PM", "06:00 PM"]
    },
    {
        "id": "DOC-04",
        "name": "Dr. Rajesh Gupta",
        "title": "M.Ch. Cardio-Thoracic Surgery",
        "specialty": "Cardiologist",
        "department": "Cardiology & Cardiac Sciences",
        "hospital": "Asian Heart Institute",
        "address": "Bandra-Kurla Complex (BKC), Mumbai",
        "distance_km": 8.5,
        "rating": 5.0,
        "experience_years": 22,
        "consultation_fee": 1500,
        "available_days": ["Tuesday", "Thursday", "Saturday"],
        "slots": ["10:30 AM", "02:30 PM", "04:30 PM", "06:00 PM"]
    },
    {
        "id": "DOC-05",
        "name": "Dr. Priya Nair",
        "title": "M.D. PMR, Senior Physiatrist",
        "specialty": "Physiotherapist",
        "department": "Physical Medicine & Rehabilitation",
        "hospital": "ActiveLife Sports & Post-Op Rehab Centre",
        "address": "ActiveLife Rehab, Palm Beach Road, Vashi",
        "distance_km": 3.1,
        "rating": 4.9,
        "experience_years": 11,
        "consultation_fee": 700,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "slots": ["09:00 AM", "10:30 AM", "04:00 PM", "05:00 PM", "06:30 PM"]
    },
    {
        "id": "DOC-06",
        "name": "Dr. Sunita Deshmukh",
        "title": "M.D. Respiratory Medicine (Pulmonology)",
        "specialty": "Pulmonologist",
        "department": "Pulmonology & Chest Medicine",
        "hospital": "BreathEasy Chest Care Center",
        "address": "Sector 17, Vashi, Navi Mumbai",
        "distance_km": 3.6,
        "rating": 4.7,
        "experience_years": 15,
        "consultation_fee": 900,
        "available_days": ["Monday", "Tuesday", "Thursday", "Friday"],
        "slots": ["11:00 AM", "04:00 PM", "05:30 PM", "07:00 PM"]
    }
]

# In-Memory Appointments Store with preloaded sample for Rahul Sharma P-101
APPOINTMENTS_STORE: List[Dict[str, Any]] = [
    {
        "id": "APT-1001",
        "patientId": "P-101",
        "patientName": "Rahul Sharma",
        "doctorId": "DOC-01",
        "doctorName": "Dr. Vikramaditya Rao",
        "specialty": "Orthopedic Surgeon",
        "hospital": "Apollo Joint Replacement Institute",
        "distanceKm": 2.4,
        "date": (date.today() + timedelta(days=2)).isoformat(),
        "time": "05:30 PM",
        "status": "confirmed",
        "type": "in_person",
        "reason": "Post-Op Knee Replacement Day 10 Suture Inspection & X-Ray Review",
        "createdAt": datetime.now().isoformat()
    }
]

# Sync initial seed appointment into MySQL if available
try:
    db_save_appointment(APPOINTMENTS_STORE[0])
except Exception:
    pass

# Symptom to Specialist Mapping for Intelligent Triage Routing
SYMPTOM_ROUTING_MAP = [
    {
        "keywords": ["fever", "cough", "cold", "bukhar", "khansi", "sardi", "throat", "gala", "weakness", "vomiting", "headache", "sar dard"],
        "specialist": "General Physician",
        "reason": "General evaluation and primary symptom management"
    },
    {
        "keywords": ["knee", "joint", "bone", "ghutna", "pain in leg", "swelling in knee", "ortho", "fracture", "stiffness", "mobility", "walk"],
        "specialist": "Orthopedic Surgeon",
        "reason": "Specialized orthopedic assessment for post-op joints and bones"
    },
    {
        "keywords": ["chest pain", "palpitation", "heart", "dil", "bp", "blood pressure", "hypertension"],
        "specialist": "Cardiologist",
        "reason": "Cardiovascular evaluation and vital monitoring"
    },
    {
        "keywords": ["exercise", "flexion", "stretch", "rehab", "physio", "physiotherapy", "kसरत", "kasrat", "stretching"],
        "specialist": "Physiotherapist",
        "reason": "Range of motion, gait training, and muscle rehabilitation"
    },
    {
        "keywords": ["breathing", "shortness of breath", "asthma", "saans", "chest congestion", "coughing"],
        "specialist": "Pulmonologist",
        "reason": "Pulmonary and respiratory health consultation"
    },
    {
        "keywords": ["wound", "stitches", "dressing", "surgery", "tankey", "stich", "pus", "incision"],
        "specialist": "General Surgeon",
        "reason": "Surgical wound care and post-operative review"
    }
]


def find_doctors(
    specialty: Optional[str] = None,
    name: Optional[str] = None,
    department: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Controlled doctor search by specialty, name, or department."""
    results = []
    spec_clean = (specialty or "").lower().strip()
    name_clean = (name or "").lower().strip()
    dept_clean = (department or "").lower().strip()

    for doc in DOCTORS_DIRECTORY:
        doc_spec = doc["specialty"].lower()
        doc_name = doc["name"].lower()
        doc_dept = doc["department"].lower()

        match = True
        if spec_clean and (spec_clean not in doc_spec and spec_clean not in doc_dept):
            match = False
        if name_clean and name_clean not in doc_name:
            match = False
        if dept_clean and dept_clean not in doc_dept:
            match = False

        if match:
            results.append(dict(doc))

    return results if results else DOCTORS_DIRECTORY[:3]


def suggest_specialist_for_symptoms(symptoms_text: str) -> Dict[str, Any]:
    """Suggest appropriate medical specialist category based on patient symptoms."""
    lower = symptoms_text.lower()
    for route in SYMPTOM_ROUTING_MAP:
        if any(kw in lower for kw in route["keywords"]):
            doctors = find_doctors(specialty=route["specialist"])
            return {
                "suggested_specialist": route["specialist"],
                "reason": route["reason"],
                "doctors": doctors,
                "matched": True
            }

    # Default to General Physician
    doctors = find_doctors(specialty="General Physician")
    return {
        "suggested_specialist": "General Physician",
        "reason": "Comprehensive primary medical consultation",
        "doctors": doctors,
        "matched": False
    }


def check_available_slots(
    doctor_id: Optional[str] = None,
    specialty: Optional[str] = None,
    target_date: Optional[str] = None,
    time_preference: Optional[str] = None  # "morning", "afternoon", "evening", or specific
) -> List[Dict[str, Any]]:
    """
    Find and rank actual available doctor slots based on preferences.
    """
    matched_doctors = []
    if doctor_id:
        matched_doctors = [d for d in DOCTORS_DIRECTORY if d["id"] == doctor_id]
    elif specialty:
        matched_doctors = find_doctors(specialty=specialty)
    else:
        matched_doctors = DOCTORS_DIRECTORY

    if not target_date:
        target_date = (date.today() + timedelta(days=1)).isoformat()

    # Determine day name
    try:
        dt = datetime.fromisoformat(target_date)
        day_name = dt.strftime("%A")
    except Exception:
        day_name = "Tomorrow"

    available_slots = []
    for doc in matched_doctors:
        # Check if doctor practices on this day
        if day_name not in doc.get("available_days", []) and day_name != "Tomorrow":
            continue

        for slot_time in doc["slots"]:
            # Check if this specific slot is already booked
            is_booked = any(
                a["doctorId"] == doc["id"] and
                a["date"] == target_date and
                a["time"] == slot_time and
                a["status"] == "confirmed"
                for a in APPOINTMENTS_STORE
            )

            if not is_booked:
                # Rank score based on time preference and proximity
                score = 100 - (doc["distance_km"] * 2)
                is_evening = any(h in slot_time for h in ["04:", "05:", "06:", "07:", "08:", "PM"])
                is_morning = "AM" in slot_time

                if time_preference == "evening" and is_evening:
                    score += 50
                elif time_preference == "morning" and is_morning:
                    score += 50

                available_slots.append({
                    "doctor_id": doc["id"],
                    "doctor_name": doc["name"],
                    "specialty": doc["specialty"],
                    "hospital": doc["hospital"],
                    "distance_km": doc["distance_km"],
                    "date": target_date,
                    "day_name": day_name,
                    "time": slot_time,
                    "fee": doc["consultation_fee"],
                    "score": score,
                    "recommended": False
                })

    # Sort slots by score (highest first)
    available_slots.sort(key=lambda x: x["score"], reverse=True)

    if available_slots:
        available_slots[0]["recommended"] = True

    return available_slots[:6]


def create_appointment(
    patient_id: str,
    doctor_id: str,
    appointment_date: str,
    appointment_time: str,
    reason: str = "Consultation & Health Review",
    patient_name: str = "Rahul Sharma",
    consultation_type: str = "in_person"
) -> Dict[str, Any]:
    """Create a new confirmed appointment in the system."""
    doc = next((d for d in DOCTORS_DIRECTORY if d["id"] == doctor_id), None)
    if not doc:
        # Match by name if doctor_id wasn't exact
        doc = next((d for d in DOCTORS_DIRECTORY if doctor_id.lower() in d["name"].lower()), DOCTORS_DIRECTORY[0])

    new_apt = {
        "id": f"APT-{1000 + len(APPOINTMENTS_STORE) + 1}",
        "patientId": patient_id,
        "patientName": patient_name,
        "doctorId": doc["id"],
        "doctorName": doc["name"],
        "specialty": doc["specialty"],
        "hospital": doc["hospital"],
        "distanceKm": doc["distance_km"],
        "date": appointment_date,
        "time": appointment_time,
        "status": "confirmed",
        "type": consultation_type,
        "reason": reason,
        "createdAt": datetime.now().isoformat()
    }

    APPOINTMENTS_STORE.append(new_apt)
    db_save_appointment(new_apt)

    return {
        "status": "success",
        "message": f"Appointment booked successfully with {doc['name']} for {appointment_date} at {appointment_time}",
        "appointment": new_apt
    }


def get_upcoming_appointments(patient_id: str = "P-101") -> List[Dict[str, Any]]:
    """Retrieve all active upcoming appointments for a patient."""
    db_apts = db_get_appointments(patient_id)
    if db_apts is not None:
        return [a for a in db_apts if a.get("status") in ("confirmed", "rescheduled")]

    return [
        dict(a) for a in APPOINTMENTS_STORE
        if a.get("patientId") == patient_id and a.get("status") in ("confirmed", "rescheduled")
    ]


def reschedule_appointment(
    appointment_id: str,
    new_date: str,
    new_time: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """Reschedule an existing appointment."""
    for apt in APPOINTMENTS_STORE:
        if apt["id"] == appointment_id:
            old_date = apt["date"]
            old_time = apt["time"]
            apt["date"] = new_date
            apt["time"] = new_time
            apt["status"] = "rescheduled"
            apt["rescheduledAt"] = datetime.now().isoformat()
            if reason:
                apt["rescheduleReason"] = reason

            db_save_appointment(apt)
            return {
                "status": "success",
                "message": f"Appointment {appointment_id} moved from {old_date} {old_time} to {new_date} at {new_time}",
                "appointment": apt
            }

    return {
        "status": "error",
        "message": f"Appointment {appointment_id} not found."
    }


def cancel_appointment(appointment_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """Cancel an existing appointment."""
    db_cancel_appointment(appointment_id)
    for apt in APPOINTMENTS_STORE:
        if apt["id"] == appointment_id:
            apt["status"] = "cancelled"
            apt["cancelledAt"] = datetime.now().isoformat()
            if reason:
                apt["cancellationReason"] = reason

            return {
                "status": "success",
                "message": f"Appointment {appointment_id} with {apt['doctorName']} has been cancelled.",
                "appointment": apt
            }

    return {
        "status": "error",
        "message": f"Appointment {appointment_id} not found."
    }


def get_patient_medications(patient_id: str = "P-101") -> List[Dict[str, Any]]:
    """Retrieve prescribed medications securely from health records."""
    return [
        {
            "name": "Paracetamol 650mg",
            "dosage": "1 tablet",
            "timing": "After food (as needed for pain/fever)",
            "prescribedBy": "Dr. Vikramaditya Rao"
        },
        {
            "name": "Cefuroxime 500mg",
            "dosage": "1 tablet twice daily",
            "timing": "After food (Antibiotic course)",
            "prescribedBy": "Dr. Vikramaditya Rao"
        },
        {
            "name": "Pantoprazole 40mg",
            "dosage": "1 tablet in morning",
            "timing": "Before food (Empty stomach)",
            "prescribedBy": "Dr. Vikramaditya Rao"
        },
        {
            "name": "Calcium + Vitamin D3",
            "dosage": "1 tablet at night",
            "timing": "With milk / dinner",
            "prescribedBy": "Dr. Vikramaditya Rao"
        }
    ]


def get_health_records(patient_id: str = "P-101") -> Dict[str, Any]:
    """Retrieve authorized summary of patient health records."""
    return {
        "patient_id": patient_id,
        "name": "Rahul Sharma",
        "surgery": "Total Knee Replacement (Right)",
        "surgery_date": "2026-08-21",
        "recovery_day": 8,
        "vitals": {
            "temperature": "98.6 °F (Normal)",
            "bp": "120/80 mmHg (Normal)",
            "heart_rate": "72 bpm (Normal)",
            "spO2": "98% (Normal)",
            "pain_score": "2/10 (Mild)"
        },
        "allergies": ["Penicillin", "Sulfa drugs"],
        "active_appointments_count": len(get_upcoming_appointments(patient_id))
    }
