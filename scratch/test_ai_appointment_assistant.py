import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import unittest
from ai.assistant import recovery_assistant
import ai.appointment_tools as apt_tools

class TestAIAppointmentAssistant(unittest.TestCase):
    def test_symptom_triage_specialist(self):
        """Test symptom matching with General Physician."""
        res = recovery_assistant.respond("I have been having fever and cough for three days. I want to see a doctor tomorrow evening.", language="en")
        self.assertEqual(res["status"], "success")
        self.assertIn("General Physician", res["response"])
        self.assertIn("action_type", res)
        self.assertEqual(res["action_type"], "slots_list")
        self.assertTrue(len(res["action_data"]) > 0)

    def test_hindi_appointment_booking(self):
        """Test Hindi appointment booking query."""
        res = recovery_assistant.respond("Mujhe kal evening mein doctor se appointment chahiye.", language="hi")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["language"], "hi")
        self.assertIn("स्लॉट्स", res["response"])
        self.assertEqual(res["action_type"], "slots_list")

    def test_upcoming_appointments_query(self):
        """Test retrieving upcoming appointment details."""
        res = recovery_assistant.respond("When is my next appointment?", language="en")
        self.assertEqual(res["status"], "success")
        self.assertIn("Upcoming Appointment", res["response"])
        self.assertIn("Dr. Vikramaditya Rao", res["response"])
        self.assertEqual(res["action_type"], "upcoming_list")

    def test_medication_records_query(self):
        """Test asking about active prescribed medications."""
        res = recovery_assistant.respond("What medicines am I currently taking?", language="en")
        self.assertEqual(res["status"], "success")
        self.assertIn("Paracetamol", res["response"])
        self.assertIn("Cefuroxime", res["response"])

    def test_reschedule_flow(self):
        """Test rescheduling appointment."""
        res = recovery_assistant.respond("I can't attend my appointment. Move it to next Monday evening.", language="en")
        self.assertEqual(res["status"], "success")
        self.assertIn("Reschedule", res["response"])
        self.assertEqual(res["action_type"], "slots_list")

    def test_cancel_flow_prompt(self):
        """Test cancellation prompt with confirmation requirement."""
        res = recovery_assistant.respond("Cancel my appointment with Dr. Rao", language="en")
        self.assertEqual(res["status"], "success")
        self.assertIn("Confirm Cancellation", res["response"])
        self.assertEqual(res["action_type"], "confirm_cancel")

    def test_controlled_booking_and_cancel_tools(self):
        """Test controlled backend tools directly."""
        # 1. Check slots
        slots = apt_tools.check_available_slots(specialty="Orthopedic Surgeon", time_preference="evening")
        self.assertTrue(len(slots) > 0)
        self.assertTrue(slots[0]["recommended"])

        # 2. Book appointment
        book_res = apt_tools.create_appointment(
            patient_id="P-101",
            doctor_id="DOC-02",
            appointment_date="2026-09-05",
            appointment_time="06:00 PM",
            reason="Knee follow-up"
        )
        self.assertEqual(book_res["status"], "success")
        new_id = book_res["appointment"]["id"]

        # 3. Reschedule
        resched_res = apt_tools.reschedule_appointment(new_id, "2026-09-06", "07:00 PM")
        self.assertEqual(resched_res["status"], "success")
        self.assertEqual(resched_res["appointment"]["status"], "rescheduled")

        # 4. Cancel
        cancel_res = apt_tools.cancel_appointment(new_id)
        self.assertEqual(cancel_res["status"], "success")
        self.assertEqual(cancel_res["appointment"]["status"], "cancelled")

    def test_emergency_red_flag_guardrail(self):
        """Test that severe emergency symptoms trigger immediate red-flag alert."""
        res = recovery_assistant.respond("I am having acute chest pain and cannot breathe", language="en")
        self.assertEqual(res["status"], "emergency_alert")
        self.assertTrue(res["is_emergency"])
        self.assertIn("CRITICAL MEDICAL ALERT", res["response"])

if __name__ == "__main__":
    unittest.main()
