import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

# Add subfolder to sys.path
root_dir = Path(__file__).resolve().parent.parent / "HackSprint--main"
sys.path.insert(0, str(root_dir))
os.chdir(str(root_dir))

import config
from ai.activity_rules import ActivityAnalyzer
from ai.notifications import send_fall_alert, send_ntfy_alert, format_alert_message, notification_service
from ai.evidence import handle_confirmed_event
import numpy as np

def make_detection(activity_type="NORMAL", conf=0.95, step=0):
    """Generate mock 17-keypoint detection results for various postures."""
    w, h = 640, 480
    
    if activity_type == "STANDING":
        # Upright tall standing posture: vertical_span > 0.6, aspect_ratio ~ 0.35
        kpts = [
            [320, 50],   # 0: Nose
            [315, 45], [325, 45], [310, 50], [330, 50],
            [290, 110], [350, 110], # 5, 6: Shoulders
            [280, 180], [360, 180], # 7, 8: Elbows
            [275, 240], [365, 240], # 9, 10: Wrists
            [300, 260], [340, 260], # 11, 12: Hips
            [300, 360], [340, 360], # 13, 14: Knees
            [300, 460], [340, 460], # 15, 16: Ankles
        ]
        bbox = [260, 40, 380, 470]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [conf] * 17,
            "bbox": bbox,
            "confidence": conf
        }

    elif activity_type == "FALL":
        # Horizontal floor posture outside bed zone (x center > 0.55, y center > 0.85)
        kpts = [
            [250, 390],  # 0: Nose
            [255, 385], [255, 395], [260, 380], [260, 400],
            [300, 400], [300, 420], # 5, 6: Shoulders
            [360, 405], [360, 425], # 7, 8: Elbows
            [410, 405], [410, 425], # 9, 10: Wrists
            [470, 410], [470, 430], # 11, 12: Hips
            [540, 415], [540, 435], # 13, 14: Knees
            [610, 420], [610, 440], # 15, 16: Ankles
        ]
        bbox = [240, 370, 630, 450] # center_x = 435/640 = 0.68 > 0.55 (outside bed zone)
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [conf] * 17,
            "bbox": bbox,
            "confidence": conf
        }

    elif activity_type == "SITTING":
        # Sitting on a chair/bed: knees bent horizontally, shorter vertical span (0.35), wider aspect ratio (0.65)
        kpts = [
            [320, 200],  # Nose
            [315, 195], [325, 195], [310, 200], [330, 200],
            [280, 240], [360, 240], # Shoulders
            [270, 290], [370, 290], # Elbows
            [270, 330], [370, 330], # Wrists
            [290, 340], [350, 340], # Hips
            [270, 350], [370, 350], # Knees (bent out)
            [280, 370], [360, 370], # Ankles
        ]
        bbox = [250, 190, 390, 380] # width 140, height 190 -> ar = 0.73, vertical_span = 170/480 = 0.35
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [conf] * 17,
            "bbox": bbox,
            "confidence": conf
        }

    elif activity_type == "WALKING":
        # Upright moving across the room
        x_shift = (step % 10) * 15
        kpts = [
            [200 + x_shift, 60],
            [195 + x_shift, 55], [205 + x_shift, 55], [190 + x_shift, 60], [210 + x_shift, 60],
            [170 + x_shift, 120], [230 + x_shift, 120],
            [160 + x_shift, 190], [240 + x_shift, 190],
            [155 + x_shift, 250], [245 + x_shift, 250],
            [180 + x_shift, 270], [220 + x_shift, 270],
            [175 + x_shift, 360], [225 + x_shift, 360],
            [170 + x_shift, 450], [230 + x_shift, 450],
        ]
        bbox = [150 + x_shift, 50, 250 + x_shift, 460]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [conf] * 17,
            "bbox": bbox,
            "confidence": conf
        }

    elif activity_type == "HAND_MOVE":
        # Upright with right wrist moving right->left
        wrist_x = 360 - step * 25
        kpts = [
            [320, 80],
            [315, 75], [325, 75], [310, 80], [330, 80],
            [290, 140], [350, 140],
            [280, 200], [330, 180],
            [275, 260], [wrist_x, 180],
            [300, 280], [340, 280],
            [300, 370], [340, 370],
            [300, 450], [340, 450],
        ]
        bbox = [240, 60, 380, 460]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [conf] * 17,
            "bbox": bbox,
            "confidence": conf
        }

    else:
        # NORMAL resting
        kpts = [
            [320, 180],
            [315, 175], [325, 175], [310, 180], [330, 180],
            [280, 230], [360, 230],
            [270, 280], [370, 280],
            [270, 320], [370, 320],
            [290, 330], [350, 330],
            [280, 380], [360, 380],
            [280, 430], [360, 430],
        ]
        bbox = [250, 170, 390, 440]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [conf] * 17,
            "bbox": bbox,
            "confidence": conf
        }


def run_tests():
    print("================================================================")
    print("RECOVERAI NTFY LOGIC VERIFICATION SUITE")
    print("================================================================")
    
    results = {}
    analyzer = ActivityAnalyzer(fall_confirmation_frames=5, fall_alert_cooldown=60.0)
    frame_shape = (480, 640)
    
    # Mock network calls to count exact NTFY send calls
    ntfy_send_count = 0
    
    def mock_send(*args, **kwargs):
        nonlocal ntfy_send_count
        ntfy_send_count += 1
        return {
            "channel": "ntfy",
            "success": True,
            "status_code": 200,
            "has_screenshot": True
        }

    with patch.object(notification_service.ntfy, 'send', side_effect=mock_send):
        
        # Test 1: Standing -> NO NTFY
        print("\n--- TEST 1: Standing ---")
        ntfy_send_count = 0
        analyzer.reset()
        for i in range(10):
            res = analyzer.analyze(make_detection("STANDING"), frame_shape, sim_time=i*0.1)
        results["1. Standing"] = (ntfy_send_count == 0 and res["activity"] == "STANDING")
        print(f"Result: {'PASS' if results['1. Standing'] else 'FAIL'} (NTFY calls: {ntfy_send_count}, Activity: {res['activity']})")

        # Test 2: Sitting -> NO NTFY
        print("\n--- TEST 2: Sitting ---")
        ntfy_send_count = 0
        analyzer.reset()
        for i in range(10):
            res = analyzer.analyze(make_detection("SITTING"), frame_shape, sim_time=i*0.1)
        results["2. Sitting"] = (ntfy_send_count == 0 and res["activity"] in ("SITTING", "NORMAL"))
        print(f"Result: {'PASS' if results['2. Sitting'] else 'FAIL'} (NTFY calls: {ntfy_send_count}, Activity: {res['activity']})")

        # Test 3: Walking -> NO NTFY
        print("\n--- TEST 3: Walking ---")
        ntfy_send_count = 0
        analyzer.reset()
        for i in range(10):
            res = analyzer.analyze(make_detection("WALKING", step=i), frame_shape, sim_time=i*0.1)
        results["3. Walking"] = (ntfy_send_count == 0 and res["activity"] in ("WALKING", "STANDING", "NORMAL"))
        print(f"Result: {'PASS' if results['3. Walking'] else 'FAIL'} (NTFY calls: {ntfy_send_count}, Activity: {res['activity']})")

        # Test 4: Hand Movement -> NO NTFY
        print("\n--- TEST 4: Hand Movement ---")
        ntfy_send_count = 0
        analyzer.reset()
        for i in range(5):
            analyzer.analyze(make_detection("STANDING"), frame_shape, sim_time=i*0.1)
        for i in range(5, 10):
            res = analyzer.analyze(make_detection("HAND_MOVE", step=i-5), frame_shape, sim_time=i*0.1)
        results["4. Hand Movement"] = (ntfy_send_count == 0)
        print(f"Result: {'PASS' if results['4. Hand Movement'] else 'FAIL'} (NTFY calls: {ntfy_send_count})")

        # Test 5: Bed Exit -> NO NTFY
        print("\n--- TEST 5: Bed Exit ---")
        ntfy_send_count = 0
        analyzer.reset()
        analyzer.was_in_bed = True
        res = analyzer.analyze(make_detection("STANDING"), frame_shape, sim_time=1.0)
        results["5. Bed Exit"] = (ntfy_send_count == 0)
        print(f"Result: {'PASS' if results['5. Bed Exit'] else 'FAIL'} (NTFY calls: {ntfy_send_count})")

        # Test 6: Normal Activity -> NO NTFY
        print("\n--- TEST 6: Normal Activity ---")
        ntfy_send_count = 0
        analyzer.reset()
        for i in range(15):
            res = analyzer.analyze(make_detection("NORMAL"), frame_shape, sim_time=i*0.1)
        results["6. Normal Activity"] = (ntfy_send_count == 0 and res["activity"] in ("NORMAL", "SITTING", "WALKING", "STANDING"))
        print(f"Result: {'PASS' if results['6. Normal Activity'] else 'FAIL'} (NTFY calls: {ntfy_send_count}, Activity: {res['activity']})")

        # Test 7: Single Noisy Fall-Like Frame -> NO NTFY
        print("\n--- TEST 7: Single Noisy Fall-Like Frame ---")
        ntfy_send_count = 0
        analyzer.reset()
        analyzer.analyze(make_detection("NORMAL"), frame_shape, sim_time=0.1)
        res_noisy = analyzer.analyze(make_detection("FALL"), frame_shape, sim_time=0.2)
        res_next = analyzer.analyze(make_detection("NORMAL"), frame_shape, sim_time=0.3)
        
        results["7. Single Noisy Frame"] = (ntfy_send_count == 0 and not res_noisy["is_confirmed_event"] and analyzer.fall_counter == 0)
        print(f"Result: {'PASS' if results['7. Single Noisy Frame'] else 'FAIL'} (NTFY calls: {ntfy_send_count}, Confirmed: {res_noisy['is_confirmed_event']}, Counter reset: {analyzer.fall_counter == 0})")

        # Test 8: Confirmed Fall (>= 5 consecutive frames) -> ONE NTFY
        print("\n--- TEST 8: Confirmed Fall (5 consecutive frames) ---")
        ntfy_send_count = 0
        analyzer.reset()
        confirmed_count = 0
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        for i in range(1, 6):
            t = i * 0.1
            res_fall = analyzer.analyze(make_detection("FALL"), frame_shape, sim_time=t)
            if res_fall["is_confirmed_event"]:
                confirmed_count += 1
                handle_confirmed_event(
                    frame=dummy_frame,
                    patient_id="P-101",
                    event_type=res_fall["screenshot_event"],
                    risk_level=res_fall["risk_level"],
                    confidence=0.95,
                    source="yolo"
                )

        results["8. Confirmed Fall"] = (confirmed_count == 1 and ntfy_send_count == 1)
        print(f"Result: {'PASS' if results['8. Confirmed Fall'] else 'FAIL'} (Confirmed events: {confirmed_count}, NTFY calls: {ntfy_send_count})")

        # Test 9: Same Fall Detected for 30 Seconds -> ONE NTFY ONLY
        print("\n--- TEST 9: Same Fall Continued for 30 Seconds (Cooldown active) ---")
        more_confirmed = 0
        for step in range(300):
            sim_t = 0.6 + step * 0.1
            res_cont = analyzer.analyze(make_detection("FALL"), frame_shape, sim_time=sim_t)
            if res_cont["is_confirmed_event"]:
                more_confirmed += 1
                handle_confirmed_event(
                    frame=dummy_frame,
                    patient_id="P-101",
                    event_type=res_cont["screenshot_event"],
                    risk_level=res_cont["risk_level"],
                    confidence=0.95,
                    source="yolo"
                )

        results["9. Same Fall for 30s"] = (more_confirmed == 0 and ntfy_send_count == 1)
        print(f"Result: {'PASS' if results['9. Same Fall for 30s'] else 'FAIL'} (Additional NTFY calls: {more_confirmed}, Total NTFY calls: {ntfy_send_count})")

        # Test 10: New Separate Fall After Recovery & Cooldown -> ONE New NTFY
        print("\n--- TEST 10: New Separate Fall After Cooldown & Recovery ---")
        for step in range(15):
            sim_t = 65.0 + step * 0.1
            analyzer.analyze(make_detection("STANDING"), frame_shape, sim_time=sim_t)
        
        new_fall_confirmed = 0
        for step in range(1, 6):
            sim_t = 70.0 + step * 0.1
            res_new = analyzer.analyze(make_detection("FALL"), frame_shape, sim_time=sim_t)
            if res_new["is_confirmed_event"]:
                new_fall_confirmed += 1
                handle_confirmed_event(
                    frame=dummy_frame,
                    patient_id="P-101",
                    event_type=res_new["screenshot_event"],
                    risk_level=res_new["risk_level"],
                    confidence=0.95,
                    source="yolo"
                )

        results["10. New Fall After Cooldown"] = (new_fall_confirmed == 1 and ntfy_send_count == 2)
        print(f"Result: {'PASS' if results['10. New Fall After Cooldown'] else 'FAIL'} (New confirmed fall: {new_fall_confirmed}, Total NTFY calls: {ntfy_send_count})")

    print("\n================================================================")
    print("FINAL TEST SUMMARY:")
    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED [OK]" if passed else "FAILED [X]"
        print(f" - {test_name:35s}: {status}")
        if not passed:
            all_passed = False
    print("================================================================")
    print(f"OVERALL STATUS: {'ALL 10 TESTS PASSED!' if all_passed else 'SOME TESTS FAILED'}")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
