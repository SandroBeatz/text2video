"""
Tests for TTS Generator Module
"""

import pytest
import os
import wave
from pathlib import Path
from modules.scene_parser import Scene
from modules.tts_generator import TTSGenerator


class TestTTSGenerator:
    """Tests for TTSGenerator class"""

    def test_generator_initialization(self):
        """Test creating a TTSGenerator"""
        config = {
            'tts': {
                'language': 'ru',
                'speed': 1.0,
                'models': {
                    'multilingual': 'tts_models/multilingual/multi-dataset/xtts_v2',
                    'en': 'tts_models/en/ljspeech/vits'
                }
            }
        }
        generator = TTSGenerator(config)
        assert generator is not None
        assert generator.language == 'ru'
        assert generator.speed == 1.0
        assert generator.model_name == 'tts_models/multilingual/multi-dataset/xtts_v2'

    def test_generator_default_language(self):
        """Test default language is Russian"""
        config = {'tts': {}}
        generator = TTSGenerator(config)
        assert generator.language == 'ru'

    def test_generator_english_language(self):
        """Test setting English language"""
        config = {
            'tts': {
                'language': 'en',
                'models': {
                    'multilingual': 'tts_models/multilingual/multi-dataset/xtts_v2',
                    'en': 'tts_models/en/ljspeech/vits'
                }
            }
        }
        generator = TTSGenerator(config)
        assert generator.language == 'en'
        assert generator.model_name == 'tts_models/en/ljspeech/vits'

    def test_lazy_loading(self):
        """Test that TTS model is not loaded on initialization"""
        config = {'tts': {'language': 'ru'}}
        generator = TTSGenerator(config)
        assert generator.tts is None

    def test_get_audio_duration_file_not_found(self):
        """Test getting duration of non-existent file"""
        config = {'tts': {'language': 'ru'}}
        generator = TTSGenerator(config)

        with pytest.raises(FileNotFoundError):
            generator.get_audio_duration('/nonexistent/file.wav')

    def test_get_audio_duration(self, tmp_path):
        """Test getting duration of a real WAV file"""
        # Create a simple WAV file for testing
        wav_path = tmp_path / "test.wav"

        # Create a 1-second mono WAV file at 16kHz
        with wave.open(str(wav_path), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(b'\x00\x00' * 16000)  # 1 second of silence

        config = {'tts': {'language': 'ru'}}
        generator = TTSGenerator(config)

        duration = generator.get_audio_duration(str(wav_path))
        assert duration == pytest.approx(1.0, abs=0.01)

    @pytest.mark.skipif(
        not os.path.exists('./venv/lib/python3.11/site-packages/TTS'),
        reason="TTS library not installed"
    )
    def test_generate_audio_simple_text(self, tmp_path):
        """Test generating audio from simple text (requires TTS installed)"""
        config = {
            'tts': {
                'language': 'ru',
                'models': {
                    'multilingual': 'tts_models/multilingual/multi-dataset/xtts_v2'
                }
            }
        }
        generator = TTSGenerator(config)
        scene = Scene(id=1, text="Тестовый текст для проверки.")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        audio_path = generator.generate(scene, str(output_dir))

        assert os.path.exists(audio_path)
        assert audio_path.endswith('.wav')
        assert os.path.getsize(audio_path) > 0

    @pytest.mark.skipif(
        not os.path.exists('./venv/lib/python3.11/site-packages/TTS'),
        reason="TTS library not installed"
    )
    def test_batch_generate(self, tmp_path):
        """Test batch generation (requires TTS installed)"""
        config = {
            'tts': {
                'language': 'ru',
                'models': {
                    'multilingual': 'tts_models/multilingual/multi-dataset/xtts_v2'
                }
            }
        }
        generator = TTSGenerator(config)

        scenes = [
            Scene(id=1, text="Первая сцена."),
            Scene(id=2, text="Вторая сцена."),
        ]

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generator.batch_generate(scenes, str(output_dir))

        # Check that all scenes have audio_path and duration set
        for scene in scenes:
            assert scene.audio_path is not None
            assert os.path.exists(scene.audio_path)
            assert scene.duration > 0

    def test_generate_without_tts_raises_import_error(self, tmp_path, monkeypatch):
        """Test that generate fails gracefully when TTS is not installed"""
        # Mock the TTS import to fail
        def mock_import_fail(*args, **kwargs):
            raise ImportError("No module named 'TTS'")

        config = {'tts': {'language': 'ru'}}
        generator = TTSGenerator(config)
        scene = Scene(id=1, text="Test")

        # Force TTS initialization to fail
        generator._initialize_tts = mock_import_fail

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(ImportError):
            generator.generate(scene, str(output_dir))
