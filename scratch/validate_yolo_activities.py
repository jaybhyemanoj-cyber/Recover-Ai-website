import os
import sys
import time
from pathlib import Path
import numpy as np

# Add subfolder
root_dir = Path(__file__).resolve().parent.parent / "HackSprint--main"
sys.path.insert(0, str(root_dir))
os.chdir(str(root_dir))

import config
from ai.activity_rules import ActivityAnalyzer
from ai.detector import pose_detector, YOLOPoseDetector

def make_test_detection(test_type: str, step: int = 0):
    """
    Produce realistic keypoint detections for each activity state
    using standard COCO 17-keypoint indexes.
    """
    w, h = 640, 480
    
    if test_type == "STANDING":
        # Upright tall human pose: angle ~ 0 deg, vertical span ~ 0.85
        kpts = [
            [320, 50],   # 0: Nose
            [315, 45], [325, 45], [310, 50], [330, 50],
            [280, 110], [360, 110], # 5, 6: Shoulders
            [270, 180], [370, 180], # 7, 8: Elbows
            [265, 240], [375, 240], # 9, 10: Wrists
            [290, 260], [350, 260], # 11, 12: Hips
            [290, 360], [350, 360], # 13, 14: Knees
            [290, 460], [350, 460], # 15, 16: Ankles
        ]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [0.95] * 17,
            "bbox": [250, 40, 390, 470],
            "confidence": 0.96
        }

    elif test_type == "SITTING_FULL":
        # Full body sitting on a chair
        kpts = [
            [320, 150],  # 0: Nose
            [315, 145], [325, 145], [310, 150], [330, 150],
            [280, 200], [360, 200], # 5, 6: Shoulders
            [270, 250], [370, 250], # 7, 8: Elbows
            [270, 290], [370, 290], # 9, 10: Wrists
            [290, 310], [350, 310], # 11, 12: Hips
            [270, 370], [370, 370], # 13, 14: Knees
            [270, 440], [370, 440], # 15, 16: Ankles
        ]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [0.92] * 17,
            "bbox": [250, 140, 390, 450],
            "confidence": 0.94
        }

    elif test_type == "SITTING_UPPER_BODY_ONLY":
        # Sitting at desk / webcam closeup where hips and legs are NOT visible (conf=0.0)
        kpts = [
            [320, 120],  # 0: Nose
            [315, 115], [325, 115], [310, 120], [330, 120],
            [260, 180], [380, 180], # 5, 6: Shoulders (conf 0.90)
            [230, 260], [410, 260], # 7, 8: Elbows
            [210, 320], [430, 320], # 9, 10: Wrists
            [0, 0], [0, 0],         # 11, 12: Hips (MISSING / OCCLUDED)
            [0, 0], [0, 0],         # 13, 14: Knees (MISSING)
            [0, 0], [0, 0],         # 15, 16: Ankles (MISSING)
        ]
        kpts_conf = [0.95, 0.95, 0.95, 0.90, 0.90, 0.92, 0.92, 0.85, 0.85, 0.80, 0.80, 0.05, 0.05, 0.0, 0.0, 0.0, 0.0]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": kpts_conf,
            "bbox": [200, 100, 440, 360],
            "confidence": 0.91
        }

    elif test_type == "WALKING":
        # Upright moving horizontally across frames
        x_shift = (step % 10) * 20
        kpts = [
            [180 + x_shift, 50],
            [175 + x_shift, 45], [185 + x_shift, 45], [170 + x_shift, 50], [190 + x_shift, 50],
            [150 + x_shift, 110], [210 + x_shift, 110],
            [140 + x_shift, 180], [220 + x_shift, 180],
            [135 + x_shift, 240], [225 + x_shift, 240],
            [160 + x_shift, 260], [200 + x_shift, 260],
            [155 + x_shift, 360], [205 + x_shift, 360],
            [150 + x_shift, 460], [210 + x_shift, 460],
        ]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [0.95] * 17,
            "bbox": [130 + x_shift, 40, 230 + x_shift, 470],
            "confidence": 0.95
        }

    elif test_type == "HAND_MOVEMENT":
        # Standing upright, moving right wrist from x=420 to x=180 across frames
        wrist_x = 420 - step * 30
        kpts = [
            [320, 50],
            [315, 45], [325, 45], [310, 50], [330, 50],
            [280, 110], [360, 110],
            [270, 180], [350, 170],
            [265, 240], [wrist_x, 170],
            [290, 260], [350, 260],
            [290, 360], [350, 360],
            [290, 460], [350, 460],
        ]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [0.95] * 17,
            "bbox": [250, 40, 430, 470],
            "confidence": 0.95
        }

    elif test_type == "TURNING_BENDING":
        # Slight torso incline (30 deg), upper body above hips
        kpts = [
            [280, 160],
            [275, 155], [285, 155], [270, 160], [290, 160],
            [260, 200], [320, 200],
            [250, 260], [330, 260],
            [250, 300], [330, 300],
            [290, 310], [330, 310],
            [290, 390], [330, 390],
            [290, 460], [330, 460],
        ]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [0.90] * 17,
            "bbox": [240, 150, 350, 470],
            "confidence": 0.92
        }

    elif test_type == "IN_BED_LYING":
        # Horizontal posture but within normalized Bed Zone [0.05, 0.15, 0.55, 0.85]
        # x between 32 and 352, y between 72 and 408
        kpts = [
            [80, 220],
            [85, 215], [85, 225], [90, 210], [90, 230],
            [120, 230], [120, 250],
            [160, 235], [160, 255],
            [200, 235], [200, 255],
            [230, 240], [230, 260],
            [270, 245], [270, 265],
            [310, 250], [310, 270],
        ]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [0.93] * 17,
            "bbox": [70, 200, 320, 280],
            "confidence": 0.95
        }

    elif test_type == "NO_PERSON":
        return {
            "detected": False,
            "keypoints": [],
            "keypoints_conf": [],
            "bbox": None,
            "confidence": 0.0
        }

    elif test_type == "LOW_CONFIDENCE":
        return {
            "detected": True,
            "keypoints": [[320, 200]] * 17,
            "keypoints_conf": [0.2] * 17,
            "bbox": [200, 100, 400, 400],
            "confidence": 0.25  # Below PERSON_CONFIDENCE_THRESHOLD (0.45)
        }

    elif test_type == "GENUINE_FALL":
        # True fall: outside bed zone, sudden downward drop to ground, torso horizontal (85 deg)
        # Hips at y=420 (h*0.87 > h*0.55), shoulders at y=400, ankles at y=430
        kpts = [
            [150, 390],  # 0: Nose
            [155, 385], [155, 395], [160, 380], [160, 400],
            [200, 400], [200, 420], # 5, 6: Shoulders
            [260, 405], [260, 425], # 7, 8: Elbows
            [310, 405], [310, 425], # 9, 10: Wrists
            [370, 410], [370, 430], # 11, 12: Hips
            [440, 415], [440, 435], # 13, 14: Knees
            [510, 420], [510, 440], # 15, 16: Ankles
        ]
        return {
            "detected": True,
            "keypoints": kpts,
            "keypoints_conf": [0.95] * 17,
            "bbox": [140, 370, 530, 450],
            "confidence": 0.95
        }

    return make_test_detection("STANDING")


def run_comprehensive_validation():
    print("=" * 75)
    print("      RECOVERAI — COMPREHENSIVE YOLO POSE & ACTIVITY AUDIT      ")
    print("=" * 75)
    
    analyzer = ActivityAnalyzer(fall_confirmation_frames=5, fall_alert_cooldown=60.0)
    frame_shape = (480, 640)
    
    tests_passed = 0
    total_tests = 11

    # --- Test 1: Standing ---
    analyzer.reset()
    for i in range(10):
        res1 = analyzer.analyze(make_test_detection("STANDING"), frame_shape, sim_time=i*0.1)
    t1_pass = (res1["activity"] == "STANDING" and not res1["is_confirmed_event"])
    print(f"Test 1 [Standing]                  : {'PASS' if t1_pass else 'FAIL'} | Activity: {res1['activity']}, Confirmed: {res1['is_confirmed_event']}")
    tests_passed += int(t1_pass)

    # --- Test 2: Full Body Sitting ---
    analyzer.reset()
    for i in range(10):
        res2 = analyzer.analyze(make_test_detection("SITTING_FULL"), frame_shape, sim_time=i*0.1)
    t2_pass = (res2["activity"] in ("SITTING", "NORMAL") and not res2["is_confirmed_event"])
    print(f"Test 2 [Sitting Full Body]         : {'PASS' if t2_pass else 'FAIL'} | Activity: {res2['activity']}, Confirmed: {res2['is_confirmed_event']}")
    tests_passed += int(t2_pass)

    # --- Test 3: Upper Body Sitting (Occluded Lower Body / Desk Closeup) ---
    analyzer.reset()
    for i in range(10):
        res3 = analyzer.analyze(make_test_detection("SITTING_UPPER_BODY_ONLY"), frame_shape, sim_time=i*0.1)
    t3_pass = (res3["activity"] in ("SITTING", "NORMAL") and not res3["is_confirmed_event"] and analyzer.fall_counter == 0)
    print(f"Test 3 [Sitting Upper Body Closeup]: {'PASS' if t3_pass else 'FAIL'} | Activity: {res3['activity']}, Torso Angle: {res3['torso_angle']}°, Fall Count: {analyzer.fall_counter}")
    tests_passed += int(t3_pass)

    # --- Test 4: Walking ---
    analyzer.reset()
    for i in range(10):
        res4 = analyzer.analyze(make_test_detection("WALKING", step=i), frame_shape, sim_time=i*0.1)
    t4_pass = (res4["activity"] in ("WALKING", "STANDING", "NORMAL") and not res4["is_confirmed_event"])
    print(f"Test 4 [Walking Across Room]       : {'PASS' if t4_pass else 'FAIL'} | Activity: {res4['activity']}, Confirmed: {res4['is_confirmed_event']}")
    tests_passed += int(t4_pass)

    # --- Test 5: Hand Movement ---
    analyzer.reset()
    for i in range(5):
        analyzer.analyze(make_test_detection("STANDING"), frame_shape, sim_time=i*0.1)
    for i in range(5, 10):
        res5 = analyzer.analyze(make_test_detection("HAND_MOVEMENT", step=i-5), frame_shape, sim_time=i*0.1)
    t5_pass = (res5["activity"] in ("HAND_MOVEMENT", "STANDING", "NORMAL") and not res5["is_confirmed_event"])
    print(f"Test 5 [Hand Gesture Wave]         : {'PASS' if t5_pass else 'FAIL'} | Activity: {res5['activity']}, Confirmed: {res5['is_confirmed_event']}")
    tests_passed += int(t5_pass)

    # --- Test 6: Turning & Bending ---
    analyzer.reset()
    for i in range(10):
        res6 = analyzer.analyze(make_test_detection("TURNING_BENDING"), frame_shape, sim_time=i*0.1)
    t6_pass = (res6["activity"] in ("NORMAL", "SITTING", "STANDING") and not res6["is_confirmed_event"])
    print(f"Test 6 [Turning / Bending]         : {'PASS' if t6_pass else 'FAIL'} | Activity: {res6['activity']}, Confirmed: {res6['is_confirmed_event']}")
    tests_passed += int(t6_pass)

    # --- Test 7: Resting / Lying In Bed (Inside Bed Zone) ---
    analyzer.reset()
    for i in range(10):
        res7 = analyzer.analyze(make_test_detection("IN_BED_LYING"), frame_shape, sim_time=i*0.1)
    t7_pass = (res7["activity"] in ("NORMAL", "SITTING") and not res7["is_confirmed_event"] and analyzer.fall_counter == 0)
    print(f"Test 7 [Lying in Bed (Bed Zone)]   : {'PASS' if t7_pass else 'FAIL'} | Activity: {res7['activity']}, In Bed: {res7['in_bed_zone']}, Fall Count: {analyzer.fall_counter}")
    tests_passed += int(t7_pass)

    # --- Test 8: No Person in Frame ---
    analyzer.reset()
    for i in range(10):
        res8 = analyzer.analyze(make_test_detection("NO_PERSON"), frame_shape, sim_time=i*0.1)
    t8_pass = (res8["activity"] == "NORMAL" and not res8["is_confirmed_event"])
    print(f"Test 8 [No Person in Frame]        : {'PASS' if t8_pass else 'FAIL'} | Activity: {res8['activity']}, Confirmed: {res8['is_confirmed_event']}")
    tests_passed += int(t8_pass)

    # --- Test 9: Low Confidence Pose (<0.45) ---
    analyzer.reset()
    for i in range(10):
        res9 = analyzer.analyze(make_test_detection("LOW_CONFIDENCE"), frame_shape, sim_time=i*0.1)
    t9_pass = (res9["activity"] == "NORMAL" and not res9["is_confirmed_event"] and analyzer.fall_counter == 0)
    print(f"Test 9 [Low Confidence Detection]  : {'PASS' if t9_pass else 'FAIL'} | Activity: {res9['activity']}, Conf: {res9['confidence']}, Fall Count: {analyzer.fall_counter}")
    tests_passed += int(t9_pass)

    # --- Test 10: Single Noisy Fall Frame ---
    analyzer.reset()
    analyzer.analyze(make_test_detection("STANDING"), frame_shape, sim_time=0.1)
    res_noisy = analyzer.analyze(make_test_detection("GENUINE_FALL"), frame_shape, sim_time=0.2) # 1 noisy frame
    res_return = analyzer.analyze(make_test_detection("STANDING"), frame_shape, sim_time=0.3) # next frame normal
    t10_pass = (not res_noisy["is_confirmed_event"] and analyzer.fall_counter == 0)
    print(f"Test 10 [Single Noisy Fall Frame]  : {'PASS' if t10_pass else 'FAIL'} | Confirmed on 1 frame: {res_noisy['is_confirmed_event']}, Reset: {analyzer.fall_counter == 0}")
    tests_passed += int(t10_pass)

    # --- Test 11: Confirmed Genuine Fall (5 consecutive frames) ---
    analyzer.reset()
    # 1. Standing frame first
    analyzer.analyze(make_test_detection("STANDING"), frame_shape, sim_time=0.1)
    
    # 2. Five consecutive fall frames outside bed zone
    fall_confirmed_step = None
    for step in range(1, 6):
        res_fall = analyzer.analyze(make_test_detection("GENUINE_FALL"), frame_shape, sim_time=0.1 + step*0.1)
        if res_fall["is_confirmed_event"]:
            fall_confirmed_step = step

    t11_pass = (fall_confirmed_step == 5 and res_fall["activity"] == "CONFIRMED_FALL")
    print(f"Test 11 [Genuine Fall (5 frames)]  : {'PASS' if t11_pass else 'FAIL'} | Confirmed on frame: {fall_confirmed_step}/5, Activity: {res_fall['activity']}")
    tests_passed += int(t11_pass)

    print("-" * 75)
    print(f"OVERALL AUDIT SCORE: {tests_passed}/{total_tests} TESTS PASSED ({tests_passed/total_tests*100:.1f}%)")
    print("=" * 75)
    return (tests_passed == total_tests)

if __name__ == "__main__":
    success = run_comprehensive_validation()
    sys.exit(0 if success else 1)
