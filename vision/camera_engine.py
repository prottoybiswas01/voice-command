"""
Privacy-First Camera & Video Stream Manager for X Assistant (Phase 5).
Manages webcam capture, video stream, frame snapshots, video recording,
and security privacy controls (Camera OFF by default).
"""

import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Any
from config.settings import settings
from core.logger import logger
from core.database import db

try:
    import cv2
except ImportError:
    cv2 = None
    logger.warning("OpenCV (cv2) library unavailable. Camera engine operating in Virtual Simulation mode.")


class CameraEngine:
    """Manages OpenCV webcam stream, image snapshot captures, and privacy controls."""

    def __init__(self) -> None:
        self.camera_index = settings.vision.camera_index
        self.captures_dir = settings.paths.captures_dir
        self.recordings_dir = settings.paths.recordings_dir
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

        self.is_camera_active = False  # Privacy First: OFF by default
        self.is_recording_video = False
        self.cap: Optional[Any] = None
        self._video_writer: Optional[Any] = None
        self._record_thread: Optional[threading.Thread] = None

    def start_camera(self) -> bool:
        """Explicitly activate webcam stream."""
        if self.is_camera_active and self.cap:
            return True

        if not cv2:
            self.is_camera_active = True
            logger.info("Camera active in Virtual Simulation mode.")
            return True

        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if self.cap and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.vision.frame_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.vision.frame_height)
                self.is_camera_active = True
                logger.info(f"Webcam (Index {self.camera_index}) activated successfully.")
                return True
            else:
                logger.warning(f"Could not open webcam index {self.camera_index}. Virtual simulation active.")
                self.is_camera_active = True
                return True
        except Exception as err:
            logger.error(f"Error starting camera: {err}")
            self.is_camera_active = True
            return True

    def stop_camera(self) -> None:
        """Deactivate webcam stream and release hardware."""
        self.is_camera_active = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        logger.info("Webcam stream deactivated (Privacy OFF mode).")

    def get_current_frame(self) -> Tuple[bool, Optional[Any]]:
        """Retrieve single video frame tuple (success, frame)."""
        if not self.is_camera_active:
            self.start_camera()

        if cv2 and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    return True, frame
            except Exception as err:
                logger.error(f"Error reading camera frame: {err}")

        # Return None if frame capture unavailable
        return False, None

    def capture_photo(self) -> Tuple[bool, str]:
        """
        Capture photo frame and save to data/captures/ directory.
        
        Returns:
            Tuple of (success: bool, status_message_or_filepath: str).
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = self.captures_dir / filename

        success, frame = self.get_current_frame()
        if success and frame is not None and cv2:
            try:
                cv2.imwrite(str(filepath), frame)
                msg = f"Photo captured and saved to: {filepath.name}"
                logger.info(msg)
                db.log_vision_capture(filename, str(filepath), "Webcam Photo Capture")
                return True, msg
            except Exception as err:
                logger.error(f"Failed to write image file: {err}")

        # Virtual image placeholder fallback
        msg = f"Virtual photo capture recorded: '{filename}'."
        logger.info(msg)
        db.log_vision_capture(filename, str(filepath), "Virtual Photo Snapshot")
        return True, msg

    def start_video_recording(self, duration_sec: int = 5) -> str:
        """Start background camera video recording."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}.avi"
        filepath = self.recordings_dir / filename

        self.is_recording_video = True

        def _video_worker():
            if cv2 and self.start_camera() and self.cap and self.cap.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(str(filepath), fourcc, 20.0, (settings.vision.frame_width, settings.vision.frame_height))
                end_time = time.time() + duration_sec

                while self.is_recording_video and time.time() < end_time:
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        out.write(frame)
                    time.sleep(0.05)

                out.release()
                logger.info(f"Video recording completed and saved to: {filename}")
                db.log_command("record_camera_video", "SUCCESS", str(filepath))
            else:
                time.sleep(duration_sec)
                logger.info(f"Virtual video recording saved: {filename}")

            self.is_recording_video = False

        self._record_thread = threading.Thread(target=_video_worker, daemon=True)
        self._record_thread.start()

        msg = f"Camera video recording started for {duration_sec} seconds. Saving to '{filename}'."
        return msg

    def stop_video_recording(self) -> str:
        """Stop active camera video recording."""
        self.is_recording_video = False
        msg = "Camera video recording stopped."
        logger.info(msg)
        return msg


# Global Camera Engine instance
camera_engine = CameraEngine()
