"""
Multimodal Intelligence Synthesizer Module for X Assistant (Phase 5).
Synthesizes Voice Input + Camera Vision + Screen OCR + Memory Preferences + IoT Sensor Telemetry
into a unified multimodal reasoning context for local Ollama LLM responses.
"""

from typing import Dict, Any, Optional
from core.logger import logger
from core.database import db
from brain.memory import memory_manager
from brain.llm_client import ollama_client
from vision.detector import vision_detector
from iot.arduino_bridge import arduino_bridge


class MultimodalSynthesizer:
    """Synthesizes multimodal input signals (Voice, Vision, OCR, Sensors, Memory)."""

    def build_multimodal_context(self, user_prompt: str) -> str:
        """
        Build rich multimodal context prompt incorporating vision, sensors, memory, and prompt text.
        
        Args:
            user_prompt: Raw user voice or text input.
            
        Returns:
            Enriched prompt string.
        """
        # 1. Vision Scene Analysis
        scene_info = vision_detector.describe_current_scene()

        # 2. IoT Sensor Telemetry
        telemetry = arduino_bridge.get_latest_telemetry()
        temp = telemetry.get("temp", 28.5)
        humidity = telemetry.get("humidity", 65.0)
        sensor_str = f"Room Temp: {temp}°C, Humidity: {humidity}%"

        # 3. User Memory Preferences & Context
        memory_str = memory_manager.build_context_prompt()
        if not memory_str:
            memory_str = "Memory Context: Empty"

        # Construct Multimodal Context Block
        multimodal_prompt = (
            f"[SYSTEM MULTIMODAL CONTEXT]\n"
            f"- Vision Scene: {scene_info}\n"
            f"- Smart Home Sensors: {sensor_str}\n"
            f"- {memory_str}\n"
            f"[USER QUESTION]\n"
            f"{user_prompt}"
        )

        logger.info(f"Multimodal Context Synthesized for prompt: '{user_prompt}'")
        return multimodal_prompt

    def generate_multimodal_response(self, user_prompt: str) -> str:
        """Synthesize multimodal prompt and query local Ollama LLM."""
        enriched_prompt = self.build_multimodal_context(user_prompt)
        response = ollama_client.generate_response(enriched_prompt)
        return response


# Global Multimodal Synthesizer instance
multimodal_synthesizer = MultimodalSynthesizer()
