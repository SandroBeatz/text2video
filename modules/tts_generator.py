"""
TTS Generator Module
Handles text-to-speech generation using Coqui TTS
"""

import os
import wave
from pathlib import Path
from typing import Optional
from modules.scene_parser import Scene


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
        """Initialize TTS model (lazy loading)"""
        if self.tts is None:
            try:
                from TTS.api import TTS
                self.tts = TTS(model_name=self.model_name)
            except ImportError:
                raise ImportError(
                    "TTS library not installed. "
                    "Install with: pip install TTS"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize TTS model: {e}")

    def generate(self, scene: Scene, output_dir: str) -> str:
        """
        Generate audio for a scene

        Args:
            scene: Scene object containing text to convert
            output_dir: Directory to save the audio file

        Returns:
            Path to the generated audio file

        Raises:
            RuntimeError: If TTS generation fails
        """
        # Ensure TTS is initialized
        self._initialize_tts()

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        output_filename = f"scene_{scene.id:03d}_audio.wav"
        output_path = os.path.join(output_dir, output_filename)

        try:
            # Generate speech
            # Check if model is multilingual (XTTS)
            if "xtts" in self.model_name.lower():
                self.tts.tts_to_file(
                    text=scene.text,
                    file_path=output_path,
                    language=self.language
                )
            else:
                self.tts.tts_to_file(
                    text=scene.text,
                    file_path=output_path
                )

            return output_path

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate audio for scene {scene.id}: {e}"
            )

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of an audio file in seconds

        Args:
            audio_path: Path to the WAV audio file

        Returns:
            Duration in seconds

        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If unable to read audio file
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            with wave.open(audio_path, 'r') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return duration

        except Exception as e:
            raise RuntimeError(f"Failed to read audio file {audio_path}: {e}")

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
