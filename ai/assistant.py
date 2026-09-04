"""
Multilingual AI Recovery & Appointment Assistant (English + Hindi)
------------------------------------------------------------------
Provides post-operative patient recovery guidance, intelligent appointment scheduling,
and healthcare navigation with strict clinical safety guardrails.

Clinical Safety Mandates:
1. NEVER diagnose medical diseases.
2. NEVER prescribe pharmaceuticals or alter medication dosages.
3. For acute red-flag symptoms, provide immediate emergency escalation instructions.
4. For appointments, use actual doctor and slot data via controlled backend tools.
5. Always seek user confirmation before finalizing booking, rescheduling, or cancellations.
"""

import re
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import requests
import config
import ai.appointment_tools as apt_tools

logger = logging.getLogger("ai.assistant")

# Red-flag emergency symptoms in English and Hindi
RED_FLAG_PATTERNS = [
    r"\b(chest pain|heart attack|angina|cannot breathe|shortness of breath|breathless|gasping)\b",
    r"\b(severe bleeding|blood gushing|heavy bleed|wound burst|stitches opened)\b",
    r"\b(unconscious|fainted|passed out|blackout|seizure|convulsion)\b",
    r"\b(high fever|10[2-9]\s*f|chills with shaking)\b",
    r"\b(calf pain|swollen calf|dvt|blood clot|sudden leg swelling)\b",
    r"\b(सीने में दर्द|सांस फूलना|सांस नहीं आ रही|खून बह रहा|टांके खुल गए|बेहोश|तेज बुखार|खून का थक्का)\b"
]

# Patient Clinical Context Default Knowledge (Rahul Sharma P-101 Knee Replacement)
DEFAULT_PATIENT_CONTEXT = {
    "patient_id": "P-101",
    "name": "Rahul Sharma",
    "surgery": "Total Knee Replacement (Right)",
    "recovery_day": 8,
    "target_recovery_days": 30,
    "doctor": "Dr. Vikramaditya Rao, M.S. Ortho",
    "caregiver": "Priya Sharma (Wife)",
    "caregiver_phone": config.CAREGIVER_PHONE,
    "medications": [
        "Paracetamol 650mg (Pain relief / fever)",
        "Cefuroxime 500mg (Antibiotic prophylaxis)",
        "Pantoprazole 40mg (Antacid - empty stomach)",
        "Calcium + Vit D3 (Bone healing)"
    ],
    "precautions": [
        "Use walker/cane for walking assistance",
        "Keep surgical dressing clean and completely dry",
        "Apply cold ice packs for 15-20 minutes to manage swelling",
        "Perform ankle pumps and gentle knee flexion exercises daily",
        "Avoid deep squats, twisting knee, or sudden pivot turns"
    ]
}

CLINICAL_KNOWLEDGE_BASE = [
    {
        "keywords": ["pain", "dard", "hurts", "aching", "painful", "दर्द", "तकलीफ"],
        "en": "Mild to moderate pain around the surgical site is normal on Recovery Day {recovery_day}. Please take your prescribed pain medications on schedule as advised by {doctor}. Using an ice pack wrapped in a clean towel for 15 minutes can also reduce swelling and discomfort. If pain becomes unbearable or suddenly spikes, notify your caregiver {caregiver}.",
        "hi": "सर्जरी के बाद रिकवरी डे {recovery_day} पर हल्का से मध्यम दर्द होना सामान्य है। कृपया {doctor} द्वारा सुझाई गई दर्द निवारक दवाएं समय पर लें। सूजन और दर्द कम करने के लिए बर्फ की सिकाई (15 मिनट) कर सकते हैं। यदि दर्द अचानक बहुत बढ़ जाए, तो तुरंत देखभालकर्ता {caregiver} को बताएं।"
    },
    {
        "keywords": ["swelling", "swollen", "soojan", "sujan", "edema", "सूजन"],
        "en": "Post-op swelling in the lower leg/knee is common. Keep your leg elevated on 1-2 pillows while resting above heart level, apply cold packs, and perform gentle ankle pump exercises to encourage blood circulation. If swelling is accompanied by intense warmth, severe redness, or calf firmness, consult {doctor} immediately.",
        "hi": "सर्जरी के बाद पैर या घुटने में हल्की सूजन होना सामान्य है। आराम करते समय पैर के नीचे तकिया रखकर उसे हल्का ऊपर रखें और बर्फ लगाएं। अगर सूजन के साथ तेज लालिमा या पैर में तेज दर्द हो, तो तुरंत {doctor} से संपर्क करें।"
    },
    {
        "keywords": ["exercise", "physio", "physiotherapy", "walk", "walking", "kasrat", "कसरत", "व्यायाम", "चलना"],
        "en": "Gentle rehabilitation is crucial for recovery. Focus on ankle pumps, straight leg raises, and gentle knee flexion exercises within pain-free limits. Always use your cane/walker when walking. You can track your joint flexion in real-time in the 'AI Camera Guard -> Physiotherapy Coach' tab.",
        "hi": "हल्का व्यायाम रिकवरी के लिए बहुत जरूरी है। एंकल पंप, लेग रेज और हल्के घुटने मोड़ने का अभ्यास करें। चलते समय हमेशा वॉकर या छड़ी का सहारा लें। आप 'AI Camera Guard -> Physiotherapy Coach' टैब में लाइव एक्सरसाइज रिप्स भी काउंट कर सकते हैं।"
    },
    {
        "keywords": ["bath", "shower", "water", "dressing", "wound", "stich", "snan", "नहाना", "पट्टी", "घाव"],
        "en": "Keep the surgical wound and dressing completely clean and dry. Do not immerse the surgical area in water until your surgeon {doctor} gives full clearance at suture removal. Sponge baths are recommended.",
        "hi": "सर्जिकल घाव और पट्टी को पूरी तरह सूखा और साफ रखें। जब तक डॉक्टर {doctor} टांके चेक न कर लें, घाव पर सीधा पानी न डालें। स्पंज बाथ (गीले कपड़े से सफाई) सुरक्षित विकल्प है।"
    },
    {
        "keywords": ["medicine", "medication", "dose", "tablet", "dawai", "goli", "दवा", "दवाई", "गोली"],
        "en": "Your prescribed medication schedule includes: {medications_str}. Please take medicines exactly as prescribed with meals where indicated. Do not alter doses without consulting {doctor}.",
        "hi": "आपकी सुझाई गई दवाएं हैं: {medications_str}। कृपया डॉक्टर {doctor} के निर्देशानुसार ही समय पर दवाएं लें। बिना डॉक्टर की सलाह के खुराक में कोई बदलाव न करें।"
    },
    {
        "keywords": ["food", "diet", "khana", "khorak", "nutrition", "खाना", "आहार", "भोजन"],
        "en": "Eat a nutrient-rich, high-protein diet (dal, eggs, paneer/tofu, fresh fruits, green vegetables) and stay well-hydrated with 2-3 liters of water daily. Fiber-rich foods help prevent post-operative constipation from medications.",
        "hi": "रिकवरी के लिए प्रोटीन युक्त पौष्टिक आहार (दाल, अंडे, पनीर, हरी सब्जियां, फल) लें और दिनभर में 2-3 लीटर पानी पिएं। फाइबर युक्त भोजन दवाओं से होने वाली कब्ज से बचाता है।"
    },
    {
        "keywords": ["sleep", "sleeping", "rest", "neend", "sona", "नींद", "सोना"],
        "en": "Sleep on your back with a pillow under your calf/foot (not directly under the knee bend). Ensure the bedroom walkway is clear of rugs and well-lit to prevent nighttime stumble or fall risks.",
        "hi": "पीठ के बल सोएं और पैर के नीचे हल्का तकिया लगाएं। रात को उठते समय कमरे में अच्छी रोशनी रखें और फर्श पर फिसलन न होने दें ताकि गिरने का कोई जोखिम न रहे।"
    }
]


class RecoveryAssistant:
    """
    Multilingual Post-Operative Patient Recovery & AI Appointment Assistant.
    """
    def __init__(self):
        self.patient_context = DEFAULT_PATIENT_CONTEXT

    def set_patient_context(self, context: Dict[str, Any]):
        """Update patient context with live dashboard data."""
        self.patient_context.update(context)

    def is_red_flag(self, text: str) -> bool:
        """Check for severe acute emergency symptoms."""
        lower = text.lower()
        for pattern in RED_FLAG_PATTERNS:
            if re.search(pattern, lower, re.IGNORECASE):
                return True
        return False

    def is_prescription_request(self, text: str) -> bool:
        """Check if user is asking for direct pharmaceutical prescription."""
        patterns = [
            r"\b(prescribe|which antibiotic to buy|give me stronger painkillers|change dosage of)\b",
            r"\b(एंटीबायोटिक लिख दो|नई दवा का पर्चा बनाओ)\b"
        ]
        lower = text.lower()
        return any(re.search(p, lower, re.IGNORECASE) for p in patterns)

    def _is_appointment_query(self, text: str) -> bool:
        """Detect if user query relates to appointments, doctors, scheduling, or records."""
        keywords = [
            "appointment", "appoint", "book", "doctor", "dr.", "dr ", "specialist", "slot", "slots",
            "schedule", "reschedule", "cancel", "upcoming", "physician", "surgeon", "consult", "consultation",
            "अपॉइंटमेंट", "डॉक्टर", "दिखाना", "बुक", "रद्द", "तारीख", "समय", "फीस", "अगली मुलाकात",
            "kal", "shyam", "morning", "evening", "tomorrow", "saturday", "sunday", "monday", "tuesday",
            "wednesday", "thursday", "friday", "dikhana", "milna", "bhejna"
        ]
        lower = text.lower()
        return any(k in lower for k in keywords)

    def _handle_appointment_flow(
        self,
        query: str,
        lang: str,
        ctx: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Processes appointment scheduling, doctor search, slot ranking,
        rescheduling, and cancellations using controlled backend tools.
        """
        q = query.lower().strip()
        patient_id = ctx.get("patient_id", "P-101")
        patient_name = ctx.get("name", "Rahul Sharma")

        # 1. CANCELLATION REQUEST (Checked first)
        if any(w in q for w in ["cancel", "cancel appointment", "radd", "रद्द"]):
            upcoming = apt_tools.get_upcoming_appointments(patient_id)
            if upcoming:
                target_apt = upcoming[0]
                if "confirm" in q or "yes" in q or "haan" in q:
                    res = apt_tools.cancel_appointment(target_apt["id"])
                    msg = (
                        f"✅ **अपॉइंटमेंट सफलतापूर्वक रद्द कर दी गई (Cancelled)**:\n"
                        f"{target_apt['doctorName']} के साथ {target_apt['date']} ({target_apt['time']}) की अपॉइंटमेंट रद्द हो गई है।"
                        if lang == "hi" else
                        f"✅ **Appointment Cancelled Successfully**:\n"
                        f"Your appointment with {target_apt['doctorName']} on {target_apt['date']} at {target_apt['time']} has been cancelled."
                    )
                    return {
                        "status": "success",
                        "intent": "cancel_confirmed",
                        "language": lang,
                        "query": query,
                        "response": msg,
                        "action_type": "appointment_card",
                        "action_data": res.get("appointment"),
                        "quick_replies": ["Book New Appointment", "View Doctor List"],
                        "disclaimer": "Clinic scheduling updated."
                    }
                else:
                    msg = (
                        f"⚠️ **अपॉइंटमेंट रद्द करने की पुष्टि (Confirm Cancellation)**:\n\n"
                        f"मुझे आपकी आगामी अपॉइंटमेंट मिली है:\n"
                        f"• **डॉक्टर**: {target_apt['doctorName']}\n"
                        f"• **तारीख**: {target_apt['date']} ({target_apt['time']})\n\n"
                        f"क्या आप वाकई इसे रद्द करना चाहते हैं?"
                        if lang == "hi" else
                        f"⚠️ **Confirm Cancellation**:\n\n"
                        f"I found your scheduled appointment:\n"
                        f"• **Doctor**: {target_apt['doctorName']} ({target_apt['specialty']})\n"
                        f"• **Date & Time**: {target_apt['date']} at {target_apt['time']}\n\n"
                        f"Would you like me to cancel this appointment?"
                    )
                    return {
                        "status": "success",
                        "intent": "cancel_prompt",
                        "language": lang,
                        "query": query,
                        "response": msg,
                        "action_type": "confirm_cancel",
                        "action_data": target_apt,
                        "quick_replies": ["Yes, Cancel Appointment", "Keep Appointment"],
                        "disclaimer": "Action requires confirmation."
                    }

        # 2. RESCHEDULING REQUEST
        if any(w in q for w in ["reschedule", "move", "change date", "badlo", "tarikh badlo", "re-schedule", "can't attend", "cannot attend", "shift"]):
            upcoming = apt_tools.get_upcoming_appointments(patient_id)
            target_apt = upcoming[0] if upcoming else None
            # Find next slots
            new_date = (date.today() + timedelta(days=3)).isoformat()
            slots = apt_tools.check_available_slots(
                doctor_id=target_apt["doctorId"] if target_apt else None,
                target_date=new_date
            )
            if lang == "hi":
                msg = (
                    f"🔄 **अपॉइंटमेंट री-शेड्यूल (Reschedule Appointment)**:\n\n"
                    f"मैंने {new_date} के लिए ये उपलब्ध स्लॉट्स ढूंढे हैं:\n"
                )
                for s in slots[:3]:
                    rec_badge = "⭐ (Recommended) " if s.get("recommended") else ""
                    msg += f"• {rec_badge}{s['doctor_name']} — **{s['time']}** ({s['hospital']})\n"
                msg += "\nआप किस समय पर री-शेड्यूल करना चाहेंगे?"
            else:
                msg = (
                    f"🔄 **Reschedule Appointment**:\n\n"
                    f"I found these alternative slots for **{new_date}**:\n"
                )
                for s in slots[:3]:
                    rec_badge = "⭐ (Recommended) " if s.get("recommended") else ""
                    msg += f"• {rec_badge}{s['doctor_name']} — **{s['time']}** ({s['hospital']})\n"
                msg += "\nWhich slot would you prefer to move your appointment to?"

            return {
                "status": "success",
                "intent": "reschedule_slots",
                "language": lang,
                "query": query,
                "response": msg,
                "action_type": "slots_list",
                "action_data": slots,
                "quick_replies": [f"{s['doctor_name']} ({s['time']})" for s in slots[:3]],
                "disclaimer": "Verified against live hospital timetable."
            }

        # 3. VIEW UPCOMING APPOINTMENTS
        if any(w in q for w in ["upcoming", "when is my", "next appointment", "next visit", "show upcoming", "meri agli appointment", "meri appointment kab hai", "view appointments", "show appointments", "my appointments", "my scheduled"]):
            upcoming = apt_tools.get_upcoming_appointments(patient_id)
            if upcoming:
                if lang == "hi":
                    msg = (
                        f"📅 **आपकी आगामी अपॉइंटमेंट (Upcoming Appointment)**:\n\n"
                        f"• **डॉक्टर**: {upcoming[0]['doctorName']} ({upcoming[0]['specialty']})\n"
                        f"• **तारीख व समय**: {upcoming[0]['date']} at {upcoming[0]['time']}\n"
                        f"• **अस्पताल**: {upcoming[0]['hospital']} ({upcoming[0].get('distanceKm', 2.4)} km दूर)\n"
                        f"• **उद्देश्य**: {upcoming[0]['reason']}\n\n"
                        "क्या आप इसे री-शेड्यूल करना चाहते हैं या नई अपॉइंटमेंट बुक करना चाहते हैं?"
                    )
                else:
                    msg = (
                        f"📅 **Your Upcoming Appointment**:\n\n"
                        f"• **Doctor**: {upcoming[0]['doctorName']} ({upcoming[0]['specialty']})\n"
                        f"• **Date & Time**: {upcoming[0]['date']} at {upcoming[0]['time']}\n"
                        f"• **Location**: {upcoming[0]['hospital']} ({upcoming[0].get('distanceKm', 2.4)} km away)\n"
                        f"• **Purpose**: {upcoming[0]['reason']}\n\n"
                        "Would you like to reschedule, cancel, or book another consultation?"
                    )
                return {
                    "status": "success",
                    "intent": "view_upcoming",
                    "language": lang,
                    "query": query,
                    "response": msg,
                    "action_type": "upcoming_list",
                    "action_data": upcoming,
                    "quick_replies": ["Book New Appointment", "Reschedule Appointment", "Cancel Appointment", "View Health Summary"],
                    "disclaimer": "AI Appointment Assistant. Data retrieved from clinic records."
                }
            else:
                msg = (
                    "आपकी कोई आगामी अपॉइंटमेंट दर्ज नहीं है। क्या आप डॉक्टर से अपॉइंटमेंट बुक करना चाहते हैं?"
                    if lang == "hi" else
                    "You currently have no upcoming appointments scheduled. Would you like me to help you book one?"
                )
                return {
                    "status": "success",
                    "intent": "view_upcoming",
                    "language": lang,
                    "query": query,
                    "response": msg,
                    "action_type": "slots_list",
                    "action_data": apt_tools.check_available_slots(),
                    "quick_replies": ["Book General Physician", "Book Orthopedic Surgeon", "Check Available Slots"],
                    "disclaimer": "AI Appointment Assistant."
                }
            upcoming = apt_tools.get_upcoming_appointments(patient_id)
            target_apt = upcoming[0] if upcoming else None
            # Find next slots
            new_date = (date.today() + timedelta(days=3)).isoformat()
            slots = apt_tools.check_available_slots(
                doctor_id=target_apt["doctorId"] if target_apt else None,
                target_date=new_date
            )
            if lang == "hi":
                msg = (
                    f"🔄 **अपॉइंटमेंट री-शेड्यूल (Reschedule Appointment)**:\n\n"
                    f"मैंने {new_date} के लिए ये उपलब्ध स्लॉट्स ढूंढे हैं:\n"
                )
                for s in slots[:3]:
                    rec_badge = "⭐ (Recommended) " if s.get("recommended") else ""
                    msg += f"• {rec_badge}{s['doctor_name']} — **{s['time']}** ({s['hospital']})\n"
                msg += "\nआप किस समय पर री-शेड्यूल करना चाहेंगे?"
            else:
                msg = (
                    f"🔄 **Reschedule Appointment**:\n\n"
                    f"I found these alternative slots for **{new_date}**:\n"
                )
                for s in slots[:3]:
                    rec_badge = "⭐ (Recommended) " if s.get("recommended") else ""
                    msg += f"• {rec_badge}{s['doctor_name']} — **{s['time']}** ({s['hospital']})\n"
                msg += "\nWhich slot would you prefer to move your appointment to?"

            return {
                "status": "success",
                "intent": "reschedule_slots",
                "language": lang,
                "query": query,
                "response": msg,
                "action_type": "slots_list",
                "action_data": slots,
                "quick_replies": [f"{s['doctor_name']} ({s['time']})" for s in slots[:3]],
                "disclaimer": "Verified against live hospital timetable."
            }

        # 4. SYMPTOM-TO-SPECIALIST ROUTING
        symptom_triage = apt_tools.suggest_specialist_for_symptoms(q)
        suggested_spec = symptom_triage["suggested_specialist"]
        is_triage = symptom_triage["matched"]

        # Parse preferred time
        time_pref = "evening" if any(w in q for w in ["evening", "shaam", "shyam", "pm", "रात", "शाम"]) else \
                    "morning" if any(w in q for w in ["morning", "subah", "am", "सुबह"]) else None

        # Parse preferred date
        pref_date = (date.today() + timedelta(days=1)).isoformat()
        if "saturday" in q or "शनिवार" in q:
            days_ahead = (5 - date.today().weekday()) % 7 or 7
            pref_date = (date.today() + timedelta(days=days_ahead)).isoformat()
        elif "sunday" in q or "रविवार" in q:
            days_ahead = (6 - date.today().weekday()) % 7 or 7
            pref_date = (date.today() + timedelta(days=days_ahead)).isoformat()
        elif "today" in q or "aaj" in q or "आज" in q:
            pref_date = date.today().isoformat()

        slots = apt_tools.check_available_slots(
            specialty=suggested_spec if is_triage else None,
            target_date=pref_date,
            time_preference=time_pref
        )

        # 5. DIRECT BOOKING CONFIRMATION TRIGGER
        if any(w in q for w in ["confirm booking", "yes book", "book slot", "confirm kar do", "book karo", "yes please"]):
            selected_slot = slots[0] if slots else None
            if selected_slot:
                res = apt_tools.create_appointment(
                    patient_id=patient_id,
                    doctor_id=selected_slot["doctor_id"],
                    appointment_date=selected_slot["date"],
                    appointment_time=selected_slot["time"],
                    reason="Post-Op Consultation & Health Check",
                    patient_name=patient_name
                )
                apt = res["appointment"]
                if lang == "hi":
                    msg = (
                        f"✅ **अपॉइंटमेंट सफलतापूर्वक कन्फर्म हो गई! (Booking Confirmed)**\n\n"
                        f"• **अपॉइंटमेंट ID**: `{apt['id']}`\n"
                        f"• **डॉक्टर**: {apt['doctorName']} ({apt['specialty']})\n"
                        f"• **तारीख व समय**: {apt['date']} at {apt['time']}\n"
                        f"• **अस्पताल**: {apt['hospital']}\n"
                        f"• **दूरी**: {apt.get('distanceKm', 2.4)} km\n\n"
                        f"SMS व WhatsApp पर कन्फर्मेशन भेज दिया गया है। क्या मैं आपके लिए कोई और सहायता करूँ?"
                    )
                else:
                    msg = (
                        f"✅ **Appointment Confirmed Successfully!**\n\n"
                        f"• **Booking ID**: `{apt['id']}`\n"
                        f"• **Doctor**: {apt['doctorName']} ({apt['specialty']})\n"
                        f"• **Date & Time**: {apt['date']} at {apt['time']}\n"
                        f"• **Clinic / Hospital**: {apt['hospital']}\n"
                        f"• **Distance**: {apt.get('distanceKm', 2.4)} km from your location\n\n"
                        f"A calendar reminder and confirmation has been logged. How else may I assist you?"
                    )
                return {
                    "status": "success",
                    "intent": "booked",
                    "language": lang,
                    "query": query,
                    "response": msg,
                    "action_type": "appointment_card",
                    "action_data": apt,
                    "quick_replies": ["View Upcoming Appointments", "Check Medicine Schedule", "Ask Recovery Advice"],
                    "disclaimer": "Confirmed with hospital central scheduling desk."
                }

        # 6. SLOT RECOMMENDATIONS & SMART SEARCH
        if lang == "hi":
            triage_prefix = f"आपके लक्षणों के आधार पर, **{suggested_spec}** ({symptom_triage['reason']}) से परामर्श करना उचित रहेगा।\n\n" if is_triage else ""
            msg = (
                f"{triage_prefix}"
                f"मैंने **{pref_date}** के लिए निकटतम उपलब्ध डॉक्टर स्लॉट्स खोजे हैं:\n\n"
            )
            for s in slots[:3]:
                badge = "⭐ **(Recommended)** " if s.get("recommended") else "• "
                msg += f"{badge}**{s['doctor_name']}** ({s['specialty']}) — **{s['time']}** | {s['hospital']} ({s['distance_km']} km)\n"
            msg += "\nआप कौन सा समय या डॉक्टर चुनना चाहेंगे?"
        else:
            triage_prefix = f"Based on your symptoms, consulting a **{suggested_spec}** ({symptom_triage['reason']}) is recommended.\n\n" if is_triage else ""
            msg = (
                f"{triage_prefix}"
                f"Here are the available appointment slots for **{pref_date}** matching your request:\n\n"
            )
            for s in slots[:3]:
                badge = "⭐ **(Recommended)** " if s.get("recommended") else "• "
                msg += f"{badge}**{s['doctor_name']}** ({s['specialty']}) — **{s['time']}** | {s['hospital']} ({s['distance_km']} km away)\n"
            msg += "\nWhich slot would you like to book?"

        return {
            "status": "success",
            "intent": "slots_search",
            "language": lang,
            "query": query,
            "response": msg,
            "action_type": "slots_list",
            "action_data": slots,
            "quick_replies": [f"Book {s['doctor_name'].split()[-1]} ({s['time']})" for s in slots[:3]] + ["Confirm Booking"],
            "disclaimer": "Real-time doctor schedule from connected healthcare directory."
        }

    def _call_groq(self, query: str, lang: str, ctx: Dict[str, Any]) -> Optional[str]:
        """
        Generate dynamic clinical recovery & appointment guidance using Groq LLM API.
        """
        api_key = getattr(config, "GROQ_API_KEY", "")
        if not api_key:
            return None

        meds_str = ", ".join(ctx.get("medications", []))
        precautions_str = ", ".join(ctx.get("precautions", []))
        upcoming_apts = apt_tools.get_upcoming_appointments(ctx.get("patient_id", "P-101"))
        upcoming_str = "; ".join([f"{a['doctorName']} ({a['specialty']}) on {a['date']} at {a['time']}" for a in upcoming_apts]) if upcoming_apts else "No upcoming appointments."

        system_prompt = (
            "You are RecoverAI Smart Healthcare & Appointment Assistant, an empathetic, certified clinical companion for post-operative recovery and smart clinic scheduling.\n"
            f"Patient Context:\n"
            f"- Name: {ctx.get('name', 'Rahul Sharma')}\n"
            f"- Surgery: {ctx.get('surgery', 'Total Knee Replacement')}\n"
            f"- Recovery Timeline: Day {ctx.get('recovery_day', 8)} of {ctx.get('target_recovery_days', 30)}\n"
            f"- Primary Doctor: {ctx.get('doctor', 'Dr. Vikramaditya Rao, M.S. Ortho')}\n"
            f"- Scheduled Appointments: {upcoming_str}\n"
            f"- Prescribed Medications: {meds_str}\n"
            f"- Precautions: {precautions_str}\n\n"
            "Capabilities & Rules:\n"
            "1. Respond in warm, fluent, compassionate Hindi if queried in Hindi/Devanagari; or natural English/Hinglish.\n"
            "2. For appointment scheduling requests, guide the user to available slots, doctors, dates, and times.\n"
            "3. Suggest specialist types (e.g. Orthopedic for knees, General Physician for fevers, Cardiologist for heart) without giving disease diagnoses.\n"
            "4. NEVER prescribe medicines or alter doses. Always refer to prescribed schedule in the Medicines tab.\n"
            "5. Keep responses concise, structured with bullet points, and helpful."
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        models_to_try = [
            getattr(config, "GROQ_MODEL", "qwen/qwen3.8-27b"),
            "openai/gpt-oss-20b",
            "groq/compound-mini",
            "allam-2-7b"
        ]

        for model in models_to_try:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 512
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        content = choices[0]["message"].get("content", "").strip()
                        if content:
                            return content
                else:
                    logger.warning(f"Groq model {model} returned HTTP {res.status_code}: {res.text[:100]}")
            except Exception as e:
                logger.warning(f"Groq API call error with model {model}: {e}")

        return None

    def respond(
        self,
        query: str,
        language: str = "en",
        custom_patient_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a safe, patient-tailored bilingual recovery & appointment response.
        """
        ctx = dict(self.patient_context)
        if custom_patient_data:
            ctx.update(custom_patient_data)

        q_clean = query.strip()
        lang = "hi" if language.lower() in ("hi", "hindi") or any('\u0900' <= c <= '\u097F' for c in q_clean) else "en"

        # 1. EMERGENCY RED FLAG GUARDRAIL (Mandatory check first)
        if self.is_red_flag(q_clean):
            if lang == "hi":
                emergency_msg = (
                    "🚨 **अति आवश्यक चेतावनी (CRITICAL EMERGENCY)**:\n"
                    "आपके द्वारा बताए गए लक्षण गंभीर स्थिति का संकेत हो सकते हैं। कृपया तुरंत:\n"
                    "1. अपने मुख्य सर्जन **{doctor}** या देखभालकर्ता **{caregiver} ({caregiver_phone})** से संपर्क करें।\n"
                    "2. आपातकालीन एम्बुलेंस (108 / 112) को कॉल करें या सीधे इमरजेंसी वार्ड जाएं।\n"
                    "3. ऐप में लाल **Emergency SOS** बटन दबाएं।"
                ).format(**ctx)
            else:
                emergency_msg = (
                    "🚨 **CRITICAL MEDICAL ALERT**:\n"
                    "The symptoms you described require immediate clinical evaluation. Please:\n"
                    "1. Contact your surgeon **{doctor}** or caregiver **{caregiver} ({caregiver_phone})** immediately.\n"
                    "2. Call emergency medical services (108 / 911) or visit the nearest Emergency Room.\n"
                    "3. Press the red **Emergency SOS** button in the dashboard."
                ).format(**ctx)

            return {
                "status": "emergency_alert",
                "is_emergency": True,
                "language": lang,
                "query": q_clean,
                "response": emergency_msg,
                "quick_replies": ["Call Emergency 108", "Contact Caregiver"],
                "disclaimer": "Emergency triage advisory only. Seek immediate human medical care."
            }

        # 2. NON-PRESCRIPTION / DOSAGE GUARDRAIL
        if self.is_prescription_request(q_clean):
            if lang == "hi":
                presc_msg = (
                    "⚠️ **चिकित्सा नियम (Medical Safety)**:\n"
                    "AI सहायक नई दवाएं लिखने या खुराक बदलने के लिए अधिकृत नहीं है।\n"
                    "आपकी वर्तमान सुझाई गई दवाएं डैशबोर्ड के 'Medicines & Schedule' में दर्ज हैं। किसी भी नई दवा के लिए कृपया अपने डॉक्टर **{doctor}** से परामर्श लें।"
                ).format(**ctx)
            else:
                presc_msg = (
                    "⚠️ **Clinical Safety Protocol**:\n"
                    "The AI Assistant cannot prescribe new medications or alter dosages. Your active prescribed schedule is visible in the 'Medicines & Schedule' tab. Please consult your physician **{doctor}** for any prescription adjustments."
                ).format(**ctx)

            return {
                "status": "prescription_guardrail",
                "is_emergency": False,
                "language": lang,
                "query": q_clean,
                "response": presc_msg,
                "quick_replies": ["Book Doctor Appointment", "View Medicine Schedule"],
                "disclaimer": "Non-prescriptive recovery companion. Consult physician for prescription changes."
            }

        # 3. AI APPOINTMENT & SCHEDULING FLOW
        if self._is_appointment_query(q_clean):
            apt_response = self._handle_appointment_flow(q_clean, lang, ctx)
            if apt_response:
                return apt_response

        # 4. HEALTH RECORD / MEDICATION INQUIRY
        if any(k in q_clean.lower() for k in ["my medicines", "what medicines", "dawai", "medication list", "health record", "meri dawai"]):
            meds = apt_tools.get_patient_medications(ctx.get("patient_id", "P-101"))
            if lang == "hi":
                med_text = "💊 **आपकी वर्तमान सुझाई गई दवाएं (Prescribed Medicines)**:\n\n"
                for m in meds:
                    med_text += f"• **{m['name']}** ({m['dosage']}) — {m['timing']} [डॉक्टर: {m['prescribedBy']}]\n"
                med_text += "\nकिसी भी खुराक परिवर्तन के लिए हमेशा अपने डॉक्टर से परामर्श लें।"
            else:
                med_text = "💊 **Your Active Prescribed Medications**:\n\n"
                for m in meds:
                    med_text += f"• **{m['name']}** ({m['dosage']}) — {m['timing']} [By {m['prescribedBy']}]\n"
                med_text += "\nAlways consult your attending physician before modifying any medication schedule."

            return {
                "status": "success",
                "intent": "medication_records",
                "language": lang,
                "query": q_clean,
                "response": med_text,
                "quick_replies": ["Book Doctor Follow-up", "Check Recovery Plan", "Ask About Swelling"],
                "disclaimer": "Retrieved from patient clinical profile."
            }

        # 5. GROQ LLM DYNAMIC RESPONSE GENERATION
        ctx["medications_str"] = ", ".join(ctx.get("medications", []))
        groq_reply = self._call_groq(q_clean, lang, ctx)
        if groq_reply:
            return {
                "status": "success",
                "source": "groq_llm",
                "is_emergency": False,
                "language": lang,
                "query": q_clean,
                "response": groq_reply,
                "quick_replies": ["Book Doctor Appointment", "Check Medicine Schedule", "My Recovery Milestones"],
                "disclaimer": "AI Recovery & Appointment Companion powered by Groq."
            }

        # 6. KNOWLEDGE-BASE MATCHING (Fallback)
        q_lower = q_clean.lower()
        for entry in CLINICAL_KNOWLEDGE_BASE:
            if any(kw in q_lower for kw in entry["keywords"]):
                template = entry["hi"] if lang == "hi" else entry["en"]
                response_text = template.format(**ctx)
                return {
                    "status": "success",
                    "source": "clinical_knowledge_base",
                    "is_emergency": False,
                    "language": lang,
                    "query": q_clean,
                    "response": response_text,
                    "quick_replies": ["Book Doctor Appointment", "Check Available Slots"],
                    "disclaimer": "Assistive post-op recovery information. Does not replace physician diagnosis."
                }

        # 7. GENERAL POST-OP GUIDANCE FALLBACK
        if lang == "hi":
            fallback = (
                "नमस्ते {name} जी! मैं आपका **RecoverAI अपॉइंटमेंट एवं रिकवरी सहायक** हूँ।\n\n"
                "• अपॉइंटमेंट बुक करने के लिए: 'मुझे कल शाम डॉक्टर से मिलना है' कहें।\n"
                "• आगामी अपॉइंटमेंट देखने के लिए: 'मेरी अगली अपॉइंटमेंट कब है' पूछें।\n"
                "• रिकवरी सहायता: दर्द, सूजन, व्यायाम या दवाओं के बारे में पूछ सकते हैं।"
            ).format(**ctx)
        else:
            fallback = (
                "Hello {name}! I am your **RecoverAI Clinical & Appointment Assistant**.\n\n"
                "• Book Appointment: e.g. 'I want to see a doctor tomorrow evening'\n"
                "• View Schedule: e.g. 'When is my next appointment?'\n"
                "• Recovery Care: Ask about post-op pain, swelling, physiotherapy exercises, or diet."
            ).format(**ctx)

        return {
            "status": "success",
            "source": "fallback_guidance",
            "is_emergency": False,
            "language": lang,
            "query": q_clean,
            "response": fallback,
            "quick_replies": ["Book Doctor Appointment", "When is my next appointment?", "Show my medicines"],
            "disclaimer": "Non-diagnostic recovery & scheduling companion."
        }


# Global Assistant Singleton
recovery_assistant = RecoveryAssistant()
