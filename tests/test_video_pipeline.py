"""
Comprehensive Test Suite for Video Upload Pipeline and Fall Reporting in RecoverAI.
Validates:
1. Video containing confirmed fall -> CONFIRMED_FALL, max_fall_confidence > 0, incident created, screenshot saved, NTFY attempted on Healthnest topic.
2. Video containing normal movement -> No fall, max_fall_confidence = 0%, NTFY Not Triggered.
3. Video analysis report contains truthful status, proper banner, and proper evidence gallery.
4. NTFY HTTP 429 quota handling for video upload pipeline.
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock
import cv2
import numpy as np

# Ensure root path is included
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config
from ai.video_analyzer import analyze_video_file
from ai.activity_rules import ActivityAnalyzer
from ai.detector import pose_detector
from ai.notifications import send_fall_alert, NTFYNotifier


class TestVideoUploadPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def _create_synthetic_video(self, has_fall: bool = True, num_frames: int = 45, fps: int = 30) -> str:
        """Create a synthetic MP4 video file with realistic standing, sitting, or falling frames."""
        video_path = os.path.join(self.temp_dir, f"test_video_{'fall' if has_fall else 'normal'}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(video_path, fourcc, float(fps), (640, 480))

        for f_idx in range(num_frames):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (30, 30, 30)

            # Draw simple synthetic person representation
            if has_fall and f_idx >= 15:
                # Horizontal fallen posture on floor (x: 200..500, y: 380..440)
                cv2.rectangle(frame, (180, 380), (520, 440), (200, 200, 200), -1)
                cv2.circle(frame, (190, 410), 18, (240, 240, 240), -1)
            else:
                # Upright standing/sitting posture (x: 280..360, y: 80..420)
                cv2.rectangle(frame, (280, 80), (360, 420), (200, 200, 200), -1)
                cv2.circle(frame, (320, 70), 20, (240, 240, 240), -1)

            writer.write(frame)

        writer.release()
        return video_path

    # TEST A: Video with Fall Analysis & Reporting
    @patch("ai.detector.pose_detector.detect")
    @patch("requests.post")
    def test_video_with_fall(self, mock_ntfy_post, mock_detect):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_ntfy_post.return_value = mock_response

        # Synthetic detection for first 5 frames: standing, next 10 frames: fall
        def mock_detect_side_effect(frame, draw_overlay=True):
            # Check frame color / mean or frame call count
            if not hasattr(mock_detect_side_effect, "call_count"):
                mock_detect_side_effect.call_count = 0
            mock_detect_side_effect.call_count += 1
            
            # First 3 sampled frames -> standing
            if mock_detect_side_effect.call_count <= 3:
                kpts = [[320.0, 50.0]] * 17
                kpts[5] = [300.0, 80.0]
                kpts[6] = [340.0, 80.0]
                kpts[11] = [305.0, 200.0]
                kpts[12] = [335.0, 200.0]
                kpts[15] = [305.0, 420.0]
                kpts[16] = [335.0, 420.0]
                bbox = [280, 30, 360, 440]
            else:
                # Horizontal posture on floor outside bed zone
                kpts = [[450.0, 380.0]] * 17
                kpts[5] = [380.0, 375.0]
                kpts[6] = [380.0, 395.0]
                kpts[11] = [500.0, 370.0]
                kpts[12] = [500.0, 390.0]
                kpts[15] = [580.0, 370.0]
                kpts[16] = [580.0, 390.0]
                bbox = [360, 350, 600, 420]

            return {
                "detected": True,
                "person_count": 1,
                "keypoints": kpts,
                "keypoints_conf": [0.88] * 17,
                "bbox": bbox,
                "confidence": 0.88,
                "annotated_frame": frame
            }

        mock_detect.side_effect = mock_detect_side_effect

        video_path = self._create_synthetic_video(has_fall=True, num_frames=30, fps=30)
        res = analyze_video_file(video_path, patient_id="P-101")

        self.assertEqual(res["status"], "success")
        self.assertTrue(res["fall_detected"], "Fall must be detected in video")
        self.assertGreater(res["fall_confidence"], 0.0, "Max fall confidence must be > 0%")
        self.assertEqual(res["fall_confidence"], 0.88)
        self.assertEqual(res["ntfy_status"], "Delivered (Priority 5)")
        self.assertIsNotNone(res["alert"])
        self.assertEqual(res["alert"]["eventType"], "CONFIRMED_FALL")
        self.assertEqual(res["alert"]["ntfyTopic"], "Healthnest")
        self.assertGreater(len(res["evidence_screenshots"]), 0)

        # Verify HTML report metadata
        self.assertIn("report", res)
        self.assertTrue(os.path.exists(res["report"]["report_path"]))

    # TEST B: Video without Fall (Normal Activities)
    @patch("ai.detector.pose_detector.detect")
    def test_video_without_fall(self, mock_detect):
        # Always upright standing detection
        kpts = [[320.0, 50.0]] * 17
        kpts[5] = [300.0, 80.0]
        kpts[6] = [340.0, 80.0]
        kpts[11] = [305.0, 200.0]
        kpts[12] = [335.0, 200.0]
        kpts[15] = [305.0, 420.0]
        kpts[16] = [335.0, 420.0]
        bbox = [280, 30, 360, 440]

        mock_detect.return_value = {
            "detected": True,
            "person_count": 1,
            "keypoints": kpts,
            "keypoints_conf": [0.85] * 17,
            "bbox": bbox,
            "confidence": 0.85,
            "annotated_frame": np.zeros((480, 640, 3), dtype=np.uint8)
        }

        video_path = self._create_synthetic_video(has_fall=False, num_frames=30, fps=30)
        res = analyze_video_file(video_path, patient_id="P-101")

        self.assertEqual(res["status"], "success")
        self.assertFalse(res["fall_detected"], "No fall should be detected in normal video")
        self.assertEqual(res["fall_confidence"], 0.0)
        self.assertEqual(res["ntfy_status"], "Not Triggered")
        self.assertIsNone(res["alert"])
        self.assertEqual(len(res["evidence_screenshots"]), 0)

    # TEST C: Video Fall with NTFY HTTP 429 (Daily Quota Reached)
    @patch("ai.detector.pose_detector.detect")
    @patch("requests.post")
    def test_video_fall_ntfy_429(self, mock_ntfy_post, mock_detect):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "daily quota reached"
        mock_ntfy_post.return_value = mock_response

        def mock_detect_side_effect(frame, draw_overlay=True):
            kpts = [[450.0, 380.0]] * 17
            kpts[5] = [380.0, 375.0]
            kpts[6] = [380.0, 395.0]
            kpts[11] = [500.0, 370.0]
            kpts[12] = [500.0, 390.0]
            kpts[15] = [580.0, 370.0]
            kpts[16] = [580.0, 390.0]
            bbox = [360, 350, 600, 420]
            return {
                "detected": True,
                "person_count": 1,
                "keypoints": kpts,
                "keypoints_conf": [0.88] * 17,
                "bbox": bbox,
                "confidence": 0.88,
                "annotated_frame": frame
            }

        mock_detect.side_effect = mock_detect_side_effect

        video_path = self._create_synthetic_video(has_fall=True, num_frames=20, fps=30)
        res = analyze_video_file(video_path, patient_id="P-101")

        self.assertEqual(res["status"], "success")
        self.assertTrue(res["fall_detected"])
        self.assertEqual(res["fall_confidence"], 0.88)
        self.assertEqual(res["ntfy_status"], "Quota Exceeded (HTTP 429)")
        self.assertIsNotNone(res["alert"])
        self.assertEqual(res["alert"]["ntfyStatus"], "failed")
        self.assertGreater(len(res["evidence_screenshots"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
