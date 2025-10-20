"""
TTS Generator Module
Handles text-to-speech generation using Coqui TTS
"""

import os
import wave
from pathlib import Path
from typing import Optional
from modules.scene_parser import Scene
from utils.exceptions import TTSError, DependencyError, ResourceNotFoundError


class TTSGenerator:
    """
    Text-to-Speech generator using Coqui TTS
    """

    # Supported TTS models
    MODELS = {
        "multilingual": "tts_models/multilingual/multi-dataset/xtts_v2",
        "en": "tts_models/en/ljspeech/vits"
    }

    def __init__(self, config: dict):
        """
        Initialize TTS generator

        Args:
            config: Configuration dictionary with TTS settings
        """
        self.config = config
        self.language = config.get('tts', {}).get('language', 'ru')
        self.speed = config.get('tts', {}).get('speed', 1.0)

        # Get model name for the language
        models = config.get('tts', {}).get('models', self.MODELS)

        # Use multilingual model for Russian, language-specific for others
        if self.language == 'ru':
            self.model_name = models.get('multilingual', self.MODELS['multilingual'])
        else:
            self.model_name = models.get(self.language, self.MODELS.get(self.language, self.MODELS['multilingual']))

        # Lazy initialization - TTS model will be loaded on first use
        self.tts = None

    def _initialize_tts(self):
        """
        Initialize TTS model (lazy loading)

        Raises:
            DependencyError: If TTS library is not installed
            TTSError: If TTS model initialization fails
        """
        if self.tts is None:
            try:
                from TTS.api import TTS
            except ImportError:
                raise DependencyError(
                    "TTS library not installed",
                    dependency="TTS",
                    details="Install with: pip install TTS>=0.22.0"
                )

            try:
                self.tts = TTS(model_name=self.model_name)
            except Exception as e:
                raise TTSError(
                    f"Failed to initialize TTS model: {self.model_name}",
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
            # Ensure TTS is initialized
            self._initialize_tts()

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

            # Generate output filename
            output_filename = f"scene_{scene.id:03d}_audio.wav"
            output_path = os.path.join(output_dir, output_filename)

            # Generate speech
            try:
                # Check if model is multilingual (XTTS)
                if "xtts" in self.model_name.lower():
                    # XTTS requires speaker parameter
                    # Use default speaker "Claribel Dervla" for English-like quality
                    self.tts.tts_to_file(
                        text=scene.text,
                        file_path=output_path,
                        language=self.language,
                        speaker="Claribel Dervla"  # Default XTTS speaker
                    )
                else:
                    self.tts.tts_to_file(
                        text=scene.text,
                        file_path=output_path
                    )
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
            audio_path: Path to the WAV audio file

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
            with wave.open(audio_path, 'r') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()

                if rate == 0:
                    raise TTSError(
                        "Invalid audio file - framerate is zero",
                        details=f"File: {audio_path}"
                    )

                duration = frames / float(rate)
                return duration

        except ResourceNotFoundError:
            # Re-raise
            raise
        except TTSError:
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
