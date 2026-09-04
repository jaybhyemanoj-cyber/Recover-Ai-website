import time
import threading
import logging
from typing import Optional
import cv2
import numpy as np

import config

logger = logging.getLogger("ai.camera")

class CameraManager:
    """
    High-performance, low-latency OpenCV webcam manager.
    Gracefully handles headless/cloud environments (Render, Linux servers without USB webcams)
    without raising unhandled exceptions or blocking the server.
    """
    def __init__(self, camera_index: int = config.CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.lock = threading.Lock()
        self.running = False
        self.latest_frame: Optional[np.ndarray] = None
        self.thread: Optional[threading.Thread] = None
        self.last_frame_time: float = 0.0
        self.fps: float = 0.0
        self.last_attempt_time: float = 0.0
        self.device_available: bool = True

    def start(self) -> bool:
        """Initialize camera at 640x480 and start capture worker."""
        with self.lock:
            if self.running and self.cap and self.cap.isOpened():
                return True

            now = time.time()
            # If camera was previously not found, allow quick retry (1.5s cooldown instead of 15s)
            if not self.device_available and (now - self.last_attempt_time) < 1.5:
                return False

            self.last_attempt_time = now
            self.device_available = True
            logger.info(f"Checking webcam index {self.camera_index} (Resolution: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT})...")

            try:
                # Try DirectShow for fast startup on Windows, fallback to default
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                if not self.cap or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.camera_index)

                if not self.cap or not self.cap.isOpened():
                    logger.info(f"Webcam not attached or unavailable at index {self.camera_index} (Running in headless/cloud mode).")
                    self.device_available = False
                    self.running = False
                    if self.cap:
                        try:
                            self.cap.release()
                        except Exception:
                            pass
                        self.cap = None
                    return False

                # Set camera capture resolution & buffer size
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                try:
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Drop old queued frames for zero latency
                except Exception:
                    pass

                self.device_available = True
                self.running = True
                self.thread = threading.Thread(target=self._capture_loop, daemon=True)
                self.thread.start()
                logger.info("Webcam capture thread started successfully.")
                return True

            except Exception as err:
                logger.warning(f"Webcam device initialization exception (safe fallback): {err}")
                self.device_available = False
                self.running = False
                self.cap = None
                return False

    def _capture_loop(self):
        """Continuous grab loop keeping only the newest frame in memory."""
        prev_time = time.time()
        while self.running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    time.sleep(0.05)
                    continue

                now = time.time()
                dt = now - prev_time
                if dt > 0:
                    self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)
                prev_time = now

                with self.lock:
                    self.latest_frame = frame
                    self.last_frame_time = now

                time.sleep(0.005)
            except Exception as e:
                logger.warning(f"Exception in capture loop: {e}")
                time.sleep(0.1)

    def get_frame(self) -> Optional[np.ndarray]:
        """Get copy of latest frame."""
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None

    def is_connected(self) -> bool:
        """Check if camera is active."""
        with self.lock:
            return bool(self.running and self.cap and self.cap.isOpened() and (time.time() - self.last_frame_time < 3.0))

    def stop(self):
        """Safely release webcam."""
        with self.lock:
            self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

        with self.lock:
            if self.cap:
                try:
                    self.cap.release()
                except Exception as e:
                    logger.error(f"Error releasing camera: {e}")
                self.cap = None
            self.latest_frame = None
            logger.info("Webcam released safely.")

# Global Camera Singleton
camera_manager = CameraManager(config.CAMERA_INDEX)
