import os
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
import cv2
import numpy as np
from ultralytics import YOLO

import config

logger = logging.getLogger("ai.detector")

# COCO Pose Skeleton Connections (pair of keypoint indices)
SKELETON_PAIRS = [
    (0, 1), (0, 2), (1, 3), (2, 4),        # Head / Facial features
    (5, 6),                                # Left Shoulder to Right Shoulder
    (5, 7), (7, 9),                        # Left Arm
    (6, 8), (8, 10),                       # Right Arm
    (5, 11), (6, 12),                      # Torso (Shoulder to Hip)
    (11, 12),                              # Left Hip to Right Hip
    (11, 13), (13, 15),                    # Left Leg
    (12, 14), (14, 16)                     # Right Leg
]

KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

class YOLOPoseDetector:
    """
    Optimized Real Ultralytics YOLO Pose Model Detector.
    Configured with imgsz=416, hardware device auto-selection (CUDA/CPU),
    and fast skeleton rendering.
    """
    def __init__(
        self,
        model_path: str = config.YOLO_MODEL_PATH,
        conf_threshold: float = config.YOLO_CONFIDENCE_THRESHOLD,
        img_size: int = config.YOLO_IMG_SIZE,
        device: str = config.DEVICE
    ):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.img_size = img_size
        self.device = device
        self.model: Optional[YOLO] = None
        self.last_inference_time_ms: float = 0.0
        self.avg_inference_time_ms: float = 0.0
        self._load_model()

    def _load_model(self):
        """Load pretrained YOLO Pose model with specified device."""
        try:
            logger.info(f"Loading YOLO Pose model from '{self.model_path}' on device '{self.device}' (imgsz={self.img_size})...")
            self.model = YOLO(self.model_path)
            # Warm up model with a dummy inference
            dummy = np.zeros((self.img_size, self.img_size, 3), dtype=np.uint8)
            self.model(dummy, imgsz=self.img_size, device=self.device, verbose=False)
            logger.info(f"Ultralytics YOLO Pose model ready on {self.device.upper()}.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def detect(self, frame: np.ndarray, draw_overlay: bool = True) -> Dict[str, Any]:
        """
        Run REAL YOLO Pose inference on an OpenCV BGR frame.
        """
        if self.model is None or frame is None:
            return {
                "detected": False,
                "person_count": 0,
                "keypoints": [],
                "keypoints_conf": [],
                "bbox": None,
                "confidence": 0.0,
                "inference_time_ms": 0.0,
                "annotated_frame": frame.copy() if frame is not None else None
            }

        annotated_frame = frame.copy() if draw_overlay else frame
        t0 = time.perf_counter()

        try:
            # Run real YOLO inference with optimized image size and device
            results = self.model(
                frame,
                imgsz=self.img_size,
                device=self.device,
                conf=self.conf_threshold,
                verbose=False
            )
            
            t1 = time.perf_counter()
            self.last_inference_time_ms = (t1 - t0) * 1000.0
            if self.avg_inference_time_ms == 0:
                self.avg_inference_time_ms = self.last_inference_time_ms
            else:
                self.avg_inference_time_ms = 0.9 * self.avg_inference_time_ms + 0.1 * self.last_inference_time_ms

            if not results or len(results) == 0:
                return {
                    "detected": False,
                    "person_count": 0,
                    "keypoints": [],
                    "keypoints_conf": [],
                    "bbox": None,
                    "confidence": 0.0,
                    "inference_time_ms": self.last_inference_time_ms,
                    "annotated_frame": annotated_frame
                }

            result = results[0]
            boxes = result.boxes
            keypoints_obj = result.keypoints

            if boxes is None or len(boxes) == 0 or keypoints_obj is None:
                return {
                    "detected": False,
                    "person_count": 0,
                    "keypoints": [],
                    "keypoints_conf": [],
                    "bbox": None,
                    "confidence": 0.0,
                    "inference_time_ms": self.last_inference_time_ms,
                    "annotated_frame": annotated_frame
                }

            # Extract highest confidence person
            confidences = boxes.conf.cpu().numpy()
            best_idx = int(np.argmax(confidences))
            real_confidence = float(confidences[best_idx])
            
            box_xyxy = boxes.xyxy[best_idx].cpu().numpy().tolist()
            x1, y1, x2, y2 = [int(v) for v in box_xyxy]

            # Extract real keypoints (x, y) coordinates and confidence
            kpts_xy = keypoints_obj.xy[best_idx].cpu().numpy()  # shape (17, 2)
            kpts_conf = (
                keypoints_obj.conf[best_idx].cpu().numpy()
                if keypoints_obj.conf is not None
                else np.ones(17)
            )

            keypoints_list = [[float(pt[0]), float(pt[1])] for pt in kpts_xy]
            keypoints_conf_list = [float(c) for c in kpts_conf]

            if draw_overlay:
                annotated_frame = self.draw_pose_overlay(
                    annotated_frame,
                    keypoints_list,
                    keypoints_conf_list,
                    (x1, y1, x2, y2),
                    real_confidence
                )

            return {
                "detected": True,
                "person_count": len(boxes),
                "keypoints": keypoints_list,
                "keypoints_conf": keypoints_conf_list,
                "bbox": [x1, y1, x2, y2],
                "confidence": real_confidence,
                "inference_time_ms": round(self.last_inference_time_ms, 1),
                "avg_inference_time_ms": round(self.avg_inference_time_ms, 1),
                "annotated_frame": annotated_frame
            }

        except Exception as err:
            logger.error(f"Error during YOLO Pose inference: {err}")
            return {
                "detected": False,
                "person_count": 0,
                "keypoints": [],
                "keypoints_conf": [],
                "bbox": None,
                "confidence": 0.0,
                "inference_time_ms": 0.0,
                "annotated_frame": annotated_frame,
                "error": str(err)
            }

    @staticmethod
    def draw_pose_overlay(
        frame: np.ndarray,
        kpts: List[List[float]],
        kpts_conf: List[float],
        bbox: Optional[Tuple[int, int, int, int]],
        confidence: float
    ) -> np.ndarray:
        """Fast, thread-safe drawing of real body keypoints, skeleton bones, and bounding box."""
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            # Bounding Box (Cyan / Teal)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (240, 180, 20), 2)
            
            # Confidence tag
            label = f"Person {int(confidence * 100)}%"
            cv2.rectangle(frame, (x1, max(0, y1 - 22)), (x1 + 110, max(0, y1)), (240, 180, 20), -1)
            cv2.putText(
                frame,
                label,
                (x1 + 5, max(14, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (15, 23, 42),
                2
            )

        # Draw Skeleton Bones
        for idx1, idx2 in SKELETON_PAIRS:
            if idx1 < len(kpts) and idx2 < len(kpts):
                conf1 = kpts_conf[idx1] if idx1 < len(kpts_conf) else 1.0
                conf2 = kpts_conf[idx2] if idx2 < len(kpts_conf) else 1.0
                if conf1 > 0.25 and conf2 > 0.25:
                    pt1 = (int(kpts[idx1][0]), int(kpts[idx1][1]))
                    pt2 = (int(kpts[idx2][0]), int(kpts[idx2][1]))
                    if pt1[0] > 0 and pt1[1] > 0 and pt2[0] > 0 and pt2[1] > 0:
                        cv2.line(frame, pt1, pt2, (52, 211, 153), 2)  # Emerald green

        # Draw Keypoint Nodes
        for i, pt in enumerate(kpts):
            conf = kpts_conf[i] if i < len(kpts_conf) else 1.0
            if conf > 0.25:
                px, py = int(pt[0]), int(pt[1])
                if px > 0 and py > 0:
                    cv2.circle(frame, (px, py), 4, (225, 29, 72), -1)   # Rose red
                    cv2.circle(frame, (px, py), 5, (255, 255, 255), 1)

        return frame

# Global Detector Singleton
pose_detector = YOLOPoseDetector()
