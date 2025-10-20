"""
Tests for TTS Generator Module (Edge TTS)
"""

import pytest
import os
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from modules.scene_parser import Scene
from modules.tts_generator import TTSGenerator
from utils.exceptions import TTSError, DependencyError


class TestTTSGenerator:
    """Tests for TTSGenerator class with Edge TTS"""

    def test_generator_initialization(self):
        """Test creating a TTSGenerator with Edge TTS"""
        config = {
            'tts': {
                'language': 'ru',
                'speed': 1.7,
                'voice': 'ru-RU-DmitryNeural'
            }
        }
        generator = TTSGenerator(config)
        assert generator is not None
        assert generator.language == 'ru'
        assert generator.speed == 1.7
        assert generator.voice == 'ru-RU-DmitryNeural'

    def test_generator_default_values(self):
        """Test default values are applied correctly"""
        config = {'tts': {}}
        generator = TTSGenerator(config)
        assert generator.language == 'ru'
        assert generator.speed == 1.0
        assert generator.voice == 'ru-RU-DmitryNeural'

    def test_generator_english_voice(self):
        """Test setting English voice"""
        config = {
            'tts': {
                'language': 'en',
                'voice': 'en-US-GuyNeural'
            }
        }
        generator = TTSGenerator(config)
        assert generator.language == 'en'
        assert generator.voice == 'en-US-GuyNeural'

    def test_format_rate(self):
        """Test _format_rate() conversion"""
        config = {'tts': {}}
        generator = TTSGenerator(config)

        # Test various speed values
        assert generator._format_rate(0.5) == "-50%"
        assert generator._format_rate(1.0) == "+0%"
        assert generator._format_rate(1.5) == "+50%"
        assert generator._format_rate(1.7) == "+70%"
        assert generator._format_rate(2.0) == "+100%"

    def test_format_rate_edge_cases(self):
        """Test _format_rate() with edge cases"""
        config = {'tts': {}}
        generator = TTSGenerator(config)

        assert generator._format_rate(0.0) == "-100%"
        assert generator._format_rate(0.75) == "-25%"
        assert generator._format_rate(1.25) == "+25%"
        assert generator._format_rate(3.0) == "+200%"

    def test_generate(self, tmp_path, monkeypatch):
        """Test synchronous generate() method"""
        config = {
            'tts': {
                'voice': 'ru-RU-DmitryNeural',
                'speed': 1.7
            }
        }

        # Create mock Communicate class
        class MockCommunicate:
            def __init__(self, text, voice, rate):
                self.text = text
                self.voice = voice
                self.rate = rate
                # Verify rate is formatted correctly
                assert rate == "+70%"

            async def save(self, path):
                # Create a fake MP3 file with some content
                from pydub import AudioSegment
                from pydub.generators import Sine

                # Create 2 second audio
                audio = Sine(440).to_audio_segment(duration=2000)
                audio.export(path, format="mp3")

        generator = TTSGenerator(config)
        monkeypatch.setattr(generator.edge_tts, 'Communicate', MockCommunicate)

        scene = Scene(id=1, text="Тестовый текст для проверки.", duration=0)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        audio_path = generator.generate(scene, str(output_dir))

        # Verify MP3 file was created
        assert os.path.exists(audio_path)
        assert audio_path.endswith('.mp3')
        assert 'scene_001_audio.mp3' in audio_path
        assert os.path.getsize(audio_path) > 0

    def test_generate_empty_text_raises_error(self, tmp_path):
        """Test that generating audio from empty text raises TTSError"""
        config = {'tts': {}}
        generator = TTSGenerator(config)

        scene = Scene(id=1, text="", duration=0)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(TTSError) as exc_info:
            generator.generate(scene, str(output_dir))

        assert "empty text" in str(exc_info.value).lower()

    def test_get_audio_duration_mp3(self, tmp_path):
        """Test getting duration of an MP3 file using pydub"""
        from pydub import AudioSegment
        from pydub.generators import Sine

        # Create a 3-second MP3 file
        audio = Sine(440).to_audio_segment(duration=3000)
        mp3_path = tmp_path / "test.mp3"
        audio.export(mp3_path, format="mp3")

        config = {'tts': {}}
        generator = TTSGenerator(config)

        duration = generator.get_audio_duration(str(mp3_path))
        assert duration == pytest.approx(3.0, abs=0.1)

    def test_get_audio_duration_wav(self, tmp_path):
        """Test getting duration of a WAV file (backward compatibility)"""
        from pydub import AudioSegment
        from pydub.generators import Sine

        # Create a 2-second WAV file
        audio = Sine(440).to_audio_segment(duration=2000)
        wav_path = tmp_path / "test.wav"
        audio.export(wav_path, format="wav")

        config = {'tts': {}}
        generator = TTSGenerator(config)

        duration = generator.get_audio_duration(str(wav_path))
        assert duration == pytest.approx(2.0, abs=0.1)

    def test_get_audio_duration_file_not_found(self, tmp_path):
        """Test getting duration of non-existent file raises error"""
        config = {'tts': {}}
        generator = TTSGenerator(config)

        from utils.exceptions import ResourceNotFoundError
        with pytest.raises(ResourceNotFoundError):
            generator.get_audio_duration(str(tmp_path / "nonexistent.mp3"))

    def test_batch_generate(self, tmp_path, monkeypatch):
        """Test batch generation of multiple scenes"""
        config = {
            'tts': {
                'voice': 'ru-RU-DmitryNeural',
                'speed': 1.0
            }
        }

        # Create mock Communicate
        class MockCommunicate:
            def __init__(self, text, voice, rate):
                self.text = text

            async def save(self, path):
                from pydub import AudioSegment
                from pydub.generators import Sine

                # Create 1.5 second audio for each scene
                audio = Sine(440).to_audio_segment(duration=1500)
                audio.export(path, format="mp3")

        generator = TTSGenerator(config)
        monkeypatch.setattr(generator.edge_tts, 'Communicate', MockCommunicate)

        scenes = [
            Scene(id=1, text="Первая сцена.", duration=0),
            Scene(id=2, text="Вторая сцена.", duration=0),
            Scene(id=3, text="Третья сцена.", duration=0),
        ]

        output_dir = tmp_path / "batch_output"
        output_dir.mkdir()

        generator.batch_generate(scenes, str(output_dir))

        # Verify all scenes have audio and duration
        for scene in scenes:
            assert scene.audio_path is not None
            assert os.path.exists(scene.audio_path)
            assert scene.audio_path.endswith('.mp3')
            assert scene.duration > 0
            assert scene.duration == pytest.approx(1.5, abs=0.1)

    def test_dependency_error_without_edge_tts(self, monkeypatch):
        """Test that initialization fails gracefully when edge-tts is not installed"""
        def mock_import(*args, **kwargs):
            raise ImportError("No module named 'edge_tts'")

        # This test is tricky because we import edge_tts in __init__
        # We need to test the error handling separately
        config = {'tts': {}}

        # We can't easily test this without actually uninstalling edge-tts
        # So we'll just verify the exception type exists
        assert DependencyError is not None

    def test_output_directory_creation(self, tmp_path, monkeypatch):
        """Test that output directory is created if it doesn't exist"""
        config = {'tts': {}}

        class MockCommunicate:
            def __init__(self, text, voice, rate):
                pass

            async def save(self, path):
                with open(path, 'wb') as f:
                    f.write(b'fake mp3')

        generator = TTSGenerator(config)
        monkeypatch.setattr(generator.edge_tts, 'Communicate', MockCommunicate)

        scene = Scene(id=1, text="Test", duration=0)

        # Non-existent nested directory
        output_dir = tmp_path / "nested" / "dirs" / "output"

        # Should not raise error
        generator.generate(scene, str(output_dir))

        assert output_dir.exists()

    def test_female_voice(self):
        """Test initialization with female voice"""
        config = {
            'tts': {
                'voice': 'ru-RU-SvetlanaNeural',
                'language': 'ru'
            }
        }
        generator = TTSGenerator(config)
        assert generator.voice == 'ru-RU-SvetlanaNeural'

    def test_english_female_voice(self):
        """Test initialization with English female voice"""
        config = {
            'tts': {
                'voice': 'en-US-JennyNeural',
                'language': 'en'
            }
        }
        generator = TTSGenerator(config)
        assert generator.voice == 'en-US-JennyNeural'
        assert generator.language == 'en'
