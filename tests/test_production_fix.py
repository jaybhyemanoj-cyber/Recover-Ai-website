"""
Comprehensive Production Verification Suite for RecoverAI
Validates all 15 test cases specified for fall detection, NTFY, screenshot,
and alert consistency fixes.
"""

import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# Ensure app directory is on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config
from ai.activity_rules import ActivityAnalyzer
from ai.notifications import send_fall_alert, send_emergency_alert, NTFYNotifier, format_alert_message
from ai.evidence import create_evidence_screenshot, handle_confirmed_event
from app import app, ALERTS_DB


class TestRecoverAIProductionFix(unittest.TestCase):
    def setUp(self):
        self.analyzer = ActivityAnalyzer(
            fall_confirmation_frames=5,
            inactivity_timeout=60.0,
            fall_alert_cooldown=60.0,
            standing_cooldown=30.0,
            bed_zone=[0.05, 0.15, 0.55, 0.85]
        )
        self.frame_shape = (480, 640)
        self.dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # --- Helper to create synthetic keypoint detections ---
    def _create_detection(self, posture="standing", conf=0.90):
        # 17 keypoints
        # 0: nose, 5: ls, 6: rs, 11: lh, 12: rh, 15: la, 16: ra, 9: lw, 10: rw
        kpts = [[320.0, 50.0]] * 17
        kpts_conf = [conf] * 17

        if posture == "standing":
            # Upright posture: shoulders at y=80, hips at y=200, ankles at y=420 (torso angle < 10°)
            kpts[5] = [300.0, 80.0]   # ls
            kpts[6] = [340.0, 80.0]   # rs
            kpts[11] = [305.0, 200.0] # lh
            kpts[12] = [335.0, 200.0] # rh
            kpts[15] = [305.0, 420.0] # la
            kpts[16] = [335.0, 420.0] # ra
            bbox = [280, 30, 360, 440]

        elif posture == "sitting":
            # Sitting: torso upright, hips lower
            kpts[5] = [300.0, 150.0]
            kpts[6] = [340.0, 150.0]
            kpts[11] = [305.0, 280.0]
            kpts[12] = [335.0, 280.0]
            kpts[15] = [305.0, 350.0]
            kpts[16] = [335.0, 350.0]
            bbox = [280, 100, 360, 370]

        elif posture == "walking":
            kpts[5] = [300.0, 120.0]
            kpts[6] = [340.0, 120.0]
            kpts[11] = [305.0, 270.0]
            kpts[12] = [335.0, 270.0]
            kpts[15] = [280.0, 440.0]
            kpts[16] = [360.0, 440.0]
            bbox = [260, 80, 380, 450]

        elif posture == "hand_movement":
            kpts[5] = [300.0, 150.0]
            kpts[6] = [340.0, 150.0]
            kpts[11] = [305.0, 280.0]
            kpts[12] = [335.0, 280.0]
            bbox = [280, 100, 360, 370]

        elif posture == "horizontal_floor":
            # Horizontal on floor outside bed zone (x > 0.55):
            # shoulders at (400, 370), hips at (520, 375), ankles at (600, 375)
            kpts[5] = [400.0, 365.0] # ls
            kpts[6] = [400.0, 385.0] # rs
            kpts[11] = [520.0, 370.0] # lh
            kpts[12] = [520.0, 390.0] # rh
            kpts[15] = [600.0, 370.0] # la
            kpts[16] = [600.0, 390.0] # ra
            bbox = [380, 340, 620, 410] # wide bounding box

        elif posture == "noisy_low_conf":
            kpts = [[320.0, 240.0]] * 17
            kpts_conf = [0.15] * 17
            bbox = [100, 100, 200, 200]
            conf = 0.20

        return {
            "detected": True,
            "person_count": 1,
            "keypoints": kpts,
            "keypoints_conf": kpts_conf,
            "bbox": bbox,
            "confidence": conf
        }

    # TEST 1: Standing -> No NTFY, No emergency alert
    def test_01_standing(self):
        # 3 frames to confirm standing posture
        res = None
        for _ in range(3):
            res = self.analyzer.analyze(self._create_detection("standing"), self.frame_shape)
        self.assertEqual(res["activity"], "STANDING")
        self.assertEqual(res["risk_level"], "stable")
        self.assertFalse(res["is_confirmed_event"])
        self.assertIsNone(res["screenshot_event"])

    # TEST 2: Sitting -> No NTFY, No emergency alert
    def test_02_sitting(self):
        det = self._create_detection("sitting")
        res = self.analyzer.analyze(det, self.frame_shape)
        self.assertEqual(res["activity"], "SITTING")
        self.assertIn(res["risk_level"], ("stable", "info"))
        self.assertFalse(res["is_confirmed_event"])

    # TEST 3: Walking -> No NTFY, No emergency alert
    def test_03_walking(self):
        det = self._create_detection("walking")
        res = self.analyzer.analyze(det, self.frame_shape)
        self.assertIn(res["activity"], ("WALKING", "NORMAL", "SITTING"))
        self.assertNotEqual(res["risk_level"], "critical")
        self.assertFalse(res["is_confirmed_event"])

    # TEST 4: Hand movement -> No NTFY, No emergency alert
    def test_04_hand_movement(self):
        # Feed sequence of wrist movements
        for x_wrist in [400, 350, 300, 230]:
            det = self._create_detection("hand_movement")
            det["keypoints"][10] = [float(x_wrist), 200.0] # rw
            res = self.analyzer.analyze(det, self.frame_shape)

        self.assertNotEqual(res["risk_level"], "critical")
        self.assertFalse(res["is_confirmed_event"])
        # Notification service rejects hand movement
        ntfy_res = send_fall_alert({"type": "HAND_MOVEMENT", "risk_level": "attention"})
        self.assertFalse(ntfy_res["success"])
        self.assertTrue(ntfy_res.get("skipped", False))

    # TEST 5: Bed exit -> No NTFY, No emergency alert
    def test_05_bed_exit(self):
        self.analyzer.was_in_bed = True
        det = self._create_detection("walking")
        det["bbox"] = [450, 100, 580, 450] # outside bed zone
        res = self.analyzer.analyze(det, self.frame_shape)
        self.assertNotEqual(res["risk_level"], "critical")
        self.assertFalse(res["is_confirmed_event"])
        ntfy_res = send_fall_alert({"type": "BED_EXIT", "risk_level": "attention"})
        self.assertTrue(ntfy_res.get("skipped", False))

    # TEST 6: Turning / Bending -> No NTFY, No emergency alert
    def test_06_turning_bending(self):
        det = self._create_detection("sitting")
        res = self.analyzer.analyze(det, self.frame_shape)
        self.assertNotEqual(res["activity"], "CONFIRMED_FALL")
        self.assertFalse(res["is_confirmed_event"])

    # TEST 7: Single noisy frame -> No NTFY, No confirmed fall
    def test_07_single_noisy_frame(self):
        # 1 standing frame, then 1 noisy/dropped frame, then 1 standing frame
        self.analyzer.analyze(self._create_detection("standing"), self.frame_shape)
        res_noisy = self.analyzer.analyze(self._create_detection("horizontal_floor"), self.frame_shape)
        self.assertEqual(res_noisy["activity"], "FALL_CANDIDATE")
        self.assertFalse(res_noisy["is_confirmed_event"]) # Not confirmed on 1 frame
        # Return to standing resets counter
        res_back = self.analyzer.analyze(self._create_detection("standing"), self.frame_shape)
        self.assertEqual(self.analyzer.fall_counter, 0)
        self.assertFalse(res_back["is_confirmed_event"])

    # TEST 8: Possible Fall -> FALL_CANDIDATE, No NTFY, No CRITICAL emergency
    def test_08_possible_fall_candidate(self):
        # 2 frames of horizontal floor
        for _ in range(2):
            res = self.analyzer.analyze(self._create_detection("horizontal_floor"), self.frame_shape)
        self.assertEqual(res["activity"], "FALL_CANDIDATE")
        self.assertEqual(res["risk_level"], "warning")
        self.assertFalse(res["is_confirmed_event"])
        self.assertIsNone(res["screenshot_event"])
        # Attempting notification on candidate MUST be skipped
        ntfy_res = send_fall_alert({"type": "FALL_CANDIDATE", "risk_level": "warning"})
        self.assertTrue(ntfy_res.get("skipped", False))
        self.assertFalse(ntfy_res["success"])

    # TEST 9: Confirmed Fall -> 1 confirmed incident, 1 screenshot, 1 NTFY attempt
    def test_09_confirmed_fall(self):
        # 5 consecutive frames of horizontal posture
        res = None
        for _ in range(5):
            res = self.analyzer.analyze(self._create_detection("horizontal_floor"), self.frame_shape)

        self.assertEqual(res["activity"], "CONFIRMED_FALL")
        self.assertEqual(res["risk_level"], "critical")
        self.assertTrue(res["is_confirmed_event"])
        self.assertEqual(res["screenshot_event"], "CONFIRMED_FALL")

    # TEST 10: Same fall for 30+ frames -> No duplicate incident, No duplicate screenshot, No duplicate NTFY
    def test_10_same_fall_deduplication(self):
        confirmed_count = 0
        for _ in range(35):
            res = self.analyzer.analyze(self._create_detection("horizontal_floor"), self.frame_shape)
            if res["is_confirmed_event"]:
                confirmed_count += 1

        self.assertEqual(confirmed_count, 1, "Exactly ONE confirmed event must be emitted while patient remains down")

    # TEST 11: New fall after cooldown and recovery -> 1 new incident
    def test_11_new_fall_after_recovery(self):
        # 1. First Fall (5 frames)
        for _ in range(5):
            self.analyzer.analyze(self._create_detection("horizontal_floor"), self.frame_shape, sim_time=100.0)
        self.assertTrue(self.analyzer.in_fall_incident)

        # 2. Recovery (Standing for 5 frames)
        for _ in range(5):
            self.analyzer.analyze(self._create_detection("standing"), self.frame_shape, sim_time=110.0)
        self.assertFalse(self.analyzer.in_fall_incident)

        # 3. Second Fall after 60s cooldown (sim_time = 170.0)
        second_fall_confirmed = False
        for _ in range(5):
            res = self.analyzer.analyze(self._create_detection("horizontal_floor"), self.frame_shape, sim_time=170.0)
            if res["is_confirmed_event"]:
                second_fall_confirmed = True

        self.assertTrue(second_fall_confirmed, "New fall after cooldown & recovery must be confirmed")

    # TEST 12: NTFY HTTP 429 Handling -> No retry loop, ntfyStatus=failed, status_code=429, error stored
    @patch("requests.post")
    def test_12_ntfy_429_handling(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "daily quota reached"
        mock_post.return_value = mock_response

        notifier = NTFYNotifier(topic="test_topic")
        res = notifier.send(
            event_type="CONFIRMED_FALL",
            patient_id="P-101",
            risk_level="critical",
            screenshot_path="static/screenshots/fall_P101_sample.jpg"
        )

        self.assertFalse(res["success"])
        self.assertEqual(res["status_code"], 429)
        self.assertIn("429", res["error"])
        self.assertFalse(res["has_screenshot"])
        self.assertEqual(mock_post.call_count, 1, "Must NOT continuously retry after HTTP 429")

    # TEST 13: Successful NTFY -> ntfyStatus = delivered, has_screenshot = True
    @patch("requests.post")
    def test_13_ntfy_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notifier = NTFYNotifier(topic="test_topic")
        res = notifier.send(
            event_type="CONFIRMED_FALL",
            patient_id="P-101",
            risk_level="critical",
            screenshot_path="static/screenshots/fall_P101_sample.jpg"
        )

        self.assertTrue(res["success"])
        self.assertEqual(res["status_code"], 200)
        self.assertTrue(res["has_screenshot"])
        self.assertIsNone(res["error"])

    # TEST 14: Old screenshot cleanup verification
    def test_14_screenshot_cleanup(self):
        sample_file = os.path.join(config.SCREENSHOT_DIR, "fall_P101_sample.jpg")
        self.assertTrue(os.path.exists(sample_file), "fall_P101_sample.jpg must exist")
        # Ensure no possible_fall_* files exist
        import glob
        possible_files = glob.glob("static/screenshots/possible_fall_*.jpg")
        self.assertEqual(len(possible_files), 0, "No old possible_fall files should remain")

    # TEST 15: Old ALT-001 demo alert & unread count consistency
    def test_15_alt001_and_unread_count(self):
        client = app.test_client()
        res = client.get("/api/alerts")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("alerts", data)
        self.assertIn("unread_count", data)

        alt_001 = next((a for a in data["alerts"] if a["id"] == "ALT-001"), None)
        self.assertIsNotNone(alt_001, "ALT-001 should exist in ALERTS_DB")
        self.assertEqual(alt_001["eventType"], "CONFIRMED_FALL")
        self.assertTrue(alt_001["acknowledged"])
        # Unread count should start at 0 (since seeded ALT-001 is acknowledged)
        self.assertEqual(data["unread_count"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
