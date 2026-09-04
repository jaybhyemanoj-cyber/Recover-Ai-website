import os
import sys
import time
from pathlib import Path
import numpy as np
import cv2
import torch
import joblib
from ultralytics import YOLO

# Add subfolder
root_dir = Path(__file__).resolve().parent.parent / "HackSprint--main"
sys.path.insert(0, str(root_dir))
os.chdir(str(root_dir))

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

import config

def audit():
    print("=" * 70)
    print("      RECOVERAI — YOLOv8 POSE & CLASSIFIER IN-DEPTH AUDIT      ")
    print("=" * 70)

    # 1. Inspect Model File & Ultralytics Pose Model
    model_path = Path(config.YOLO_MODEL_PATH)
    if not model_path.is_absolute():
        model_path = root_dir / config.YOLO_MODEL_PATH
        if not model_path.exists():
            model_path = root_dir.parent / config.YOLO_MODEL_PATH

    print(f"\n[SECTION 1: YOLO Model File & Architecture]")
    print(f"Model Path:         {model_path}")
    print(f"File Exists:        {model_path.exists()}")
    if model_path.exists():
        print(f"File Size:          {model_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Load model
    t0 = time.time()
    model = YOLO(str(model_path))
    load_time = time.time() - t0
    print(f"Load Time:          {load_time:.3f}s")
    print(f"Model Task:         {getattr(model, 'task', 'unknown')}")
    print(f"Model Names:        {model.names}")
    
    # 2. Check Keypoint Shape
    kpt_shape = getattr(model.model, 'kpt_shape', None) if hasattr(model, 'model') else None
    print(f"Keypoint Shape:     {kpt_shape} (Expected: [17, 3] or [17, 2])")

    # 3. Test Inference on Synthetic Frame
    print(f"\n[SECTION 2: Inference & Keypoints Extraction]")
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw simple synthetic stick figure
    cv2.circle(dummy_frame, (320, 100), 25, (255, 255, 255), -1) # Head
    cv2.line(dummy_frame, (320, 125), (320, 280), (255, 255, 255), 8) # Body
    cv2.line(dummy_frame, (320, 160), (250, 220), (255, 255, 255), 6) # Left arm
    cv2.line(dummy_frame, (320, 160), (390, 220), (255, 255, 255), 6) # Right arm
    cv2.line(dummy_frame, (320, 280), (270, 420), (255, 255, 255), 6) # Left leg
    cv2.line(dummy_frame, (320, 280), (370, 420), (255, 255, 255), 6) # Right leg

    t_inf_start = time.perf_counter()
    results = model(dummy_frame, imgsz=config.YOLO_IMG_SIZE, device=config.DEVICE, verbose=False)
    t_inf_end = time.perf_counter()
    latency_ms = (t_inf_end - t_inf_start) * 1000.0

    print(f"Inference Latency:  {latency_ms:.2f} ms")
    print(f"Results Type:       {type(results)}")
    print(f"Detections Count:   {len(results[0].boxes) if results and results[0].boxes is not None else 0}")
    if results and len(results) > 0 and results[0].keypoints is not None:
        print(f"Has Keypoints Obj:  YES")
        if len(results[0].keypoints.xy) > 0:
            kpts_xy = results[0].keypoints.xy[0].cpu().numpy()
            kpts_conf = results[0].keypoints.conf[0].cpu().numpy() if results[0].keypoints.conf is not None else None
            print(f"Keypoints Extracted: {len(kpts_xy)} keypoints")
            print(f"Keypoint Coordinates Shape: {kpts_xy.shape}")
            if kpts_conf is not None:
                print(f"Keypoint Confidence Shape:  {kpts_conf.shape}")
        else:
            print("No keypoint coordinates found in synthetic frame (expected for simple stick figure).")

    # 4. Audit Keypoint Index Mapping in Code
    print(f"\n[SECTION 3: Keypoint Index Mapping Audit]")
    from ai.detector import KEYPOINT_NAMES, SKELETON_PAIRS
    print("COCO 17 Keypoints Index Map in RecoverAI:")
    for idx, name in enumerate(KEYPOINT_NAMES):
        print(f"  Index {idx:2d} -> {name}")

    expected_coco = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    is_map_correct = (KEYPOINT_NAMES == expected_coco)
    print(f"Index Mapping Matches Standard COCO Pose: {is_map_correct}")

    # 5. Check activity_fall_classifier.joblib
    print(f"\n[SECTION 4: Joblib Classifier Audit]")
    joblib_path = root_dir / "models" / "activity_fall_classifier.joblib"
    print(f"Classifier Path:    {joblib_path}")
    print(f"Classifier Exists:  {joblib_path.exists()}")
    if joblib_path.exists():
        data = joblib.load(str(joblib_path))
        print(f"Loaded Object Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        if isinstance(data, dict):
            print(f"Model Class:        {type(data.get('model'))}")
            print(f"Feature Count:      {len(data.get('feature_cols', []))}")
            print(f"Sample Features:    {data.get('feature_cols', [])[:5]}")
            print(f"Classes:            {data.get('classes')}")
            print(f"Trained Accuracy:   {data.get('accuracy')}")

    # 6. Check Camera Connection
    print(f"\n[SECTION 5: OpenCV Camera Audit]")
    from ai.camera import camera_manager
    print(f"Configured Index:   {config.CAMERA_INDEX}")
    print(f"Resolution:         {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
    is_cam_open = camera_manager.start()
    print(f"Camera Start Success: {is_cam_open}")
    if is_cam_open:
        time.sleep(0.5)
        frame = camera_manager.get_frame()
        print(f"Frame Received:     {frame is not None}")
        if frame is not None:
            print(f"Frame Dimensions:   {frame.shape}")
            # Run YOLO on actual camera frame
            t_cam0 = time.perf_counter()
            cam_res = model(frame, imgsz=config.YOLO_IMG_SIZE, device=config.DEVICE, verbose=False)
            t_cam1 = time.perf_counter()
            cam_lat = (t_cam1 - t_cam0) * 1000.0
            print(f"Live Cam Inference Latency: {cam_lat:.2f} ms (~{1000.0/max(1.0, cam_lat):.1f} max FPS)")
            if cam_res and len(cam_res[0].boxes) > 0:
                print(f"Live Cam Persons:   {len(cam_res[0].boxes)}")
                print(f"Live Cam Conf:      {float(cam_res[0].boxes.conf[0]):.2f}")
                if cam_res[0].keypoints is not None and len(cam_res[0].keypoints.xy) > 0:
                    print(f"Live Cam Keypoints: {len(cam_res[0].keypoints.xy[0])} keypoints extracted")
            else:
                print("Live Cam Persons:   0 (No person in front of camera or background only)")
        camera_manager.stop()

    print("\n" + "=" * 70)
    print("AUDIT EXECUTION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    audit()
