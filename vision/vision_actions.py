"""
Smart Vision Voice Actions Handler for X Assistant (Phase 5).
Translates natural language vision voice commands into camera, object detection,
OCR, and desktop screen recognition actions.
"""

from typing import Dict, Any
from core.logger import logger
from core.database import db
from vision.camera_engine import camera_engine
from vision.detector import vision_detector
from vision.ocr_engine import ocr_engine


class VisionActionsHandler:
    """Executes Smart Vision AI voice intents."""

    def handle_vision_command(self, action_name: str, params: Dict[str, Any]) -> str:
        """
        Execute Vision AI command.
        
        Args:
            action_name: Action name.
            params: Parameters dict.
            
        Returns:
            Status / response speech text.
        """
        logger.info(f"Executing Vision Action: '{action_name}' with params: {params}")

        # 1. What do you see? / Scene description
        if action_name == "describe_scene":
            scene_text = vision_detector.describe_current_scene()
            logger.info(f"Scene Description: {scene_text}")
            return scene_text

        # 2. Read text on screen (Desktop Screen OCR)
        elif action_name == "read_screen_text":
            text_result = ocr_engine.extract_text_from_screen()
            logger.info(f"Screen OCR Result: {text_result}")
            return text_result

        # 3. Count people
        elif action_name == "count_people":
            count = vision_detector.count_people()
            msg = f"I detected {count} {'person' if count == 1 else 'people'} in front of the camera."
            logger.info(msg)
            return msg

        # 4. Recognize object
        elif action_name == "recognize_object":
            res = vision_detector.detect_objects_and_faces()
            objs = ", ".join(res.get("detected_objects", ["object"]))
            msg = f"Recognized objects: {objs}."
            logger.info(msg)
            return msg

        # 5. Check door / intruder motion
        elif action_name == "check_door_vision":
            res = vision_detector.detect_objects_and_faces()
            count = res.get("person_count", 0)
            if count > 0:
                msg = f"Alert! I see {count} person near the door view."
            else:
                msg = "Door camera clear. No persons detected."
            logger.info(msg)
            return msg

        # 6. Take a picture
        elif action_name == "take_picture":
            success, msg = camera_engine.capture_photo()
            return msg

        # 7. Start / Stop video recording
        elif action_name == "start_camera_recording":
            duration = params.get("duration", 5)
            return camera_engine.start_video_recording(duration_sec=duration)

        elif action_name == "stop_camera_recording":
            return camera_engine.stop_video_recording()

        return "Vision command processed."


# Global Vision Actions Handler instance
vision_actions_handler = VisionActionsHandler()
