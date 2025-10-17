"""
Integration Tests
Tests for the integration between different modules
"""

import pytest
import os
import yaml
from pathlib import Path
from modules.scene_parser import SceneParser
from modules.tts_generator import TTSGenerator


class TestSceneParserTTSIntegration:
    """Integration tests for SceneParser and TTSGenerator"""

    @pytest.fixture
    def config(self):
        """Load configuration from config.yaml"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def test_script_path(self, tmp_path):
        """Create a temporary test script file"""
        script_path = tmp_path / "test_script.txt"
        script_path.write_text(
            "First scene with some text.\n"
            "This is a simple test.\n\n"
            "Second scene goes here.\n"
            "It has multiple lines too.\n\n"
            "Third and final scene.\n"
            "The end.",
            encoding='utf-8'
        )
        return str(script_path)

    def test_parse_and_check_scenes(self, test_script_path):
        """Test parsing a script and checking scene structure"""
        parser = SceneParser()
        scenes = parser.parse(test_script_path)

        # Check we got 3 scenes
        assert len(scenes) == 3

        # Check scene IDs are sequential
        assert scenes[0].id == 1
        assert scenes[1].id == 2
        assert scenes[2].id == 3

        # Check scene texts
        assert "First scene" in scenes[0].text
        assert "Second scene" in scenes[1].text
        assert "Third and final" in scenes[2].text

        # Check initial state - no audio generated yet
        for scene in scenes:
            assert scene.audio_path is None
            assert scene.duration == 0.0

    @pytest.mark.skipif(
        not os.path.exists('./venv/lib/python3.11/site-packages/TTS'),
        reason="TTS library not installed"
    )
    def test_full_pipeline_with_tts(self, config, test_script_path, tmp_path):
        """
        Test full pipeline: parse text -> generate audio -> verify results
        (requires TTS installed)
        """
        # Parse the script
        parser = SceneParser()
        scenes = parser.parse(test_script_path)

        assert len(scenes) == 3

        # Generate audio for all scenes
        output_dir = tmp_path / "audio_output"
        output_dir.mkdir()

        tts_generator = TTSGenerator(config)
        tts_generator.batch_generate(scenes, str(output_dir))

        # Verify all scenes have audio
        for scene in scenes:
            # Check audio_path is set
            assert scene.audio_path is not None
            assert os.path.exists(scene.audio_path)

            # Check file is not empty
            assert os.path.getsize(scene.audio_path) > 0

            # Check duration is set and positive
            assert scene.duration > 0

            # Check filename format
            assert f"scene_{scene.id:03d}_audio.wav" in scene.audio_path

    def test_scene_metadata_preservation(self, test_script_path):
        """Test that scene metadata is preserved during processing"""
        parser = SceneParser()
        scenes = parser.parse(test_script_path)

        # Add some metadata
        scenes[0].metadata['custom_key'] = 'custom_value'
        scenes[1].metadata['priority'] = 'high'

        # Verify metadata is preserved
        assert scenes[0].metadata['custom_key'] == 'custom_value'
        assert scenes[1].metadata['priority'] == 'high'
        assert scenes[2].metadata == {}  # No metadata added

    def test_empty_script_handling(self, tmp_path):
        """Test handling of empty script file"""
        empty_script = tmp_path / "empty.txt"
        empty_script.write_text("", encoding='utf-8')

        parser = SceneParser()
        scenes = parser.parse(str(empty_script))

        # Should return empty list for empty file
        assert len(scenes) == 0

    def test_single_scene_script(self, tmp_path):
        """Test script with only one scene"""
        single_scene = tmp_path / "single.txt"
        single_scene.write_text(
            "This is a single scene.\n"
            "With multiple lines.\n"
            "But no paragraph breaks.",
            encoding='utf-8'
        )

        parser = SceneParser()
        scenes = parser.parse(str(single_scene))

        assert len(scenes) == 1
        assert scenes[0].id == 1
        assert "This is a single scene" in scenes[0].text

    def test_unicode_text_parsing(self, tmp_path):
        """Test parsing text with Unicode characters"""
        unicode_script = tmp_path / "unicode.txt"
        unicode_script.write_text(
            "Сцена первая на русском языке.\n\n"
            "Scene two in English.\n\n"
            "第三场景用中文。",
            encoding='utf-8'
        )

        parser = SceneParser()
        scenes = parser.parse(str(unicode_script))

        assert len(scenes) == 3
        assert "русском" in scenes[0].text
        assert "English" in scenes[1].text
        assert "中文" in scenes[2].text

    @pytest.mark.skipif(
        not os.path.exists('./venv/lib/python3.11/site-packages/TTS'),
        reason="TTS library not installed"
    )
    def test_russian_text_with_tts(self, config, tmp_path):
        """
        Test Russian text parsing and audio generation
        (requires TTS installed and model downloaded)
        """
        # Create Russian script
        russian_script = tmp_path / "russian.txt"
        russian_script.write_text(
            "Привет, это тестовая сцена.\n\n"
            "Вторая сцена на русском языке.",
            encoding='utf-8'
        )

        # Parse
        parser = SceneParser()
        scenes = parser.parse(str(russian_script))

        assert len(scenes) == 2

        # Generate audio (will use multilingual XTTS model)
        output_dir = tmp_path / "russian_audio"
        output_dir.mkdir()

        tts_generator = TTSGenerator(config)
        tts_generator.batch_generate(scenes, str(output_dir))

        # Verify
        for scene in scenes:
            assert scene.audio_path is not None
            assert os.path.exists(scene.audio_path)
            assert scene.duration > 0
