"""
TTS Generator Module
Handles text-to-speech generation using Microsoft Edge TTS
"""

import os
import asyncio
from pathlib import Path
from typing import Optional
from pydub import AudioSegment
from modules.scene_parser import Scene
from utils.exceptions import TTSError, DependencyError, ResourceNotFoundError


class TTSGenerator:
    """
    Text-to-Speech generator using Microsoft Edge TTS
    """

    def __init__(self, config: dict):
        """
        Initialize TTS generator

        Args:
            config: Configuration dictionary with TTS settings
        """
        self.config = config
        tts_config = config.get('tts', {})

        self.language = tts_config.get('language', 'ru')
        self.speed = tts_config.get('speed', 1.0)
        self.voice = tts_config.get('voice', 'ru-RU-DmitryNeural')

        # Validate Edge TTS is available
        try:
            import edge_tts
            self.edge_tts = edge_tts
        except ImportError:
            raise DependencyError(
                "edge-tts library not installed",
                dependency="edge-tts",
                details="Install with: pip install edge-tts>=6.1.9"
            )

    def _format_rate(self, speed: float) -> str:
        """
        Convert speed multiplier to Edge TTS rate format

        Args:
            speed: Speed multiplier (e.g., 1.7 = 170% speed)

        Returns:
            Rate string (e.g., "+70%" for speed=1.7)

        Examples:
            0.5 -> "-50%"
            1.0 -> "+0%"
            1.5 -> "+50%"
            2.0 -> "+100%"
        """
        percentage = int((speed - 1.0) * 100)
        sign = "+" if percentage >= 0 else ""
        return f"{sign}{percentage}%"

    async def _generate_async(self, text: str, output_path: str) -> None:
        """
        Async wrapper for Edge TTS generation

        Args:
            text: Text to convert to speech
            output_path: Path where to save the generated audio

        Raises:
            TTSError: If TTS generation fails
        """
        try:
            rate = self._format_rate(self.speed)
            communicate = self.edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=rate
            )
            await communicate.save(output_path)
        except Exception as e:
            raise TTSError(
                f"Edge TTS generation failed",
                language=self.language,
                details=str(e)
            )

    def generate(self, scene: Scene, output_dir: str) -> str:
        """
        Generate audio for a scene

        Args:
            scene: Scene object containing text to convert
            output_dir: Directory to save the audio file

        Returns:
            Path to the generated audio file

        Raises:
            TTSError: If TTS generation fails
        """
        try:
            # Create output directory if it doesn't exist
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                raise TTSError(
                    f"Failed to create output directory: {output_dir}",
                    language=self.language,
                    details=str(e)
                )

            # Validate scene text
            if not scene.text or not scene.text.strip():
                raise TTSError(
                    f"Scene {scene.id} has empty text",
                    language=self.language,
                    details="Cannot generate audio for empty text"
                )

            # Generate output filename (MP3 instead of WAV)
            output_filename = f"scene_{scene.id:03d}_audio.mp3"
            output_path = os.path.join(output_dir, output_filename)

            # Generate speech using async Edge TTS
            try:
                asyncio.run(self._generate_async(scene.text, output_path))
            except Exception as e:
                raise TTSError(
                    f"Audio generation failed for scene {scene.id}",
                    language=self.language,
                    details=str(e)
                )

            # Verify output file was created
            if not os.path.exists(output_path):
                raise TTSError(
                    f"Audio file was not created for scene {scene.id}",
                    language=self.language,
                    details=f"Expected output: {output_path}"
                )

            return output_path

        except (TTSError, DependencyError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any unexpected errors and wrap them
            raise TTSError(
                f"Unexpected error during audio generation for scene {scene.id}",
                language=self.language,
                details=str(e)
            )

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of an audio file in seconds

        Args:
            audio_path: Path to the audio file (MP3 or WAV)

        Returns:
            Duration in seconds

        Raises:
            ResourceNotFoundError: If audio file doesn't exist
            TTSError: If unable to read audio file
        """
        if not os.path.exists(audio_path):
            raise ResourceNotFoundError(
                "Audio file not found",
                resource_path=audio_path,
                details="File may not have been generated correctly"
            )

        try:
            # Use pydub to handle both MP3 and WAV files
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0  # Convert milliseconds to seconds
            return duration

        except ResourceNotFoundError:
            # Re-raise
            raise
        except Exception as e:
            raise TTSError(
                "Failed to read audio file",
                details=f"File: {audio_path}, Error: {str(e)}"
            )

    def batch_generate(self, scenes: list[Scene], output_dir: str) -> None:
        """
        Generate audio for multiple scenes

        Args:
            scenes: List of Scene objects
            output_dir: Directory to save audio files

        Note:
            This method updates each scene's audio_path and duration
        """
        for scene in scenes:
            # Generate audio
            audio_path = self.generate(scene, output_dir)
            scene.audio_path = audio_path

            # Calculate and set duration
            duration = self.get_audio_duration(audio_path)
            scene.duration = duration
