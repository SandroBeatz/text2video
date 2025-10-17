"""
Tests for Scene Parser Module
"""

import pytest
from pathlib import Path
from modules.scene_parser import Scene, SceneParser


class TestScene:
    """Tests for Scene dataclass"""

    def test_scene_creation(self):
        """Test creating a Scene object"""
        scene = Scene(id=1, text="Test text")
        assert scene.id == 1
        assert scene.text == "Test text"
        assert scene.duration == 0.0
        assert scene.audio_path is None
        assert scene.subtitle_path is None
        assert scene.image_path is None
        assert scene.metadata == {}

    def test_scene_with_all_fields(self):
        """Test creating a Scene with all fields"""
        scene = Scene(
            id=1,
            text="Test text",
            duration=5.5,
            audio_path="/path/to/audio.wav",
            subtitle_path="/path/to/subtitle.srt",
            image_path="/path/to/image.jpg",
            metadata={"key": "value"}
        )
        assert scene.id == 1
        assert scene.text == "Test text"
        assert scene.duration == 5.5
        assert scene.audio_path == "/path/to/audio.wav"
        assert scene.subtitle_path == "/path/to/subtitle.srt"
        assert scene.image_path == "/path/to/image.jpg"
        assert scene.metadata == {"key": "value"}


class TestSceneParser:
    """Tests for SceneParser class"""

    def test_parser_initialization(self):
        """Test creating a SceneParser"""
        parser = SceneParser()
        assert parser is not None

    def test_parse_simple_text(self, tmp_path):
        """Test parsing simple text with 3 paragraphs"""
        # Create temporary test file
        test_file = tmp_path / "test.txt"
        test_file.write_text(
            "First paragraph.\n\n"
            "Second paragraph.\n\n"
            "Third paragraph.",
            encoding='utf-8'
        )

        parser = SceneParser()
        scenes = parser.parse(str(test_file))

        assert len(scenes) == 3
        assert scenes[0].id == 1
        assert scenes[0].text == "First paragraph."
        assert scenes[1].id == 2
        assert scenes[1].text == "Second paragraph."
        assert scenes[2].id == 3
        assert scenes[2].text == "Third paragraph."

    def test_parse_with_empty_lines(self, tmp_path):
        """Test parsing text with empty lines"""
        test_file = tmp_path / "test.txt"
        test_file.write_text(
            "First paragraph.\n\n\n\n"
            "Second paragraph.\n\n",
            encoding='utf-8'
        )

        parser = SceneParser()
        scenes = parser.parse(str(test_file))

        # Empty paragraphs should be ignored
        assert len(scenes) == 2
        assert scenes[0].text == "First paragraph."
        assert scenes[1].text == "Second paragraph."

    def test_clean_text_removes_extra_spaces(self):
        """Test that clean_text removes extra whitespace"""
        parser = SceneParser()
        dirty = "  Text   with    many    spaces  "
        clean = parser.clean_text(dirty)
        assert clean == "Text with many spaces"

    def test_clean_text_removes_newlines(self):
        """Test that clean_text replaces newlines with spaces"""
        parser = SceneParser()
        dirty = "Text with\nnewlines\nand\ttabs"
        clean = parser.clean_text(dirty)
        assert clean == "Text with newlines and tabs"

    def test_split_into_scenes(self):
        """Test splitting text into scenes"""
        parser = SceneParser()
        text = "First scene.\n\nSecond scene.\n\nThird scene."
        scenes = parser.split_into_scenes(text)

        assert len(scenes) == 3
        assert scenes[0] == "First scene."
        assert scenes[1] == "Second scene."
        assert scenes[2] == "Third scene."

    def test_parse_txt_file(self, tmp_path):
        """Test parsing .txt file"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content", encoding='utf-8')

        parser = SceneParser()
        scenes = parser.parse(str(test_file))

        assert len(scenes) == 1
        assert scenes[0].text == "Test content"

    def test_parse_md_file(self, tmp_path):
        """Test parsing .md file"""
        test_file = tmp_path / "test.md"
        test_file.write_text("Markdown content", encoding='utf-8')

        parser = SceneParser()
        scenes = parser.parse(str(test_file))

        assert len(scenes) == 1
        assert scenes[0].text == "Markdown content"

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        parser = SceneParser()

        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.txt")

    def test_parse_unsupported_format(self, tmp_path):
        """Test parsing unsupported file format"""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("Content", encoding='utf-8')

        parser = SceneParser()

        with pytest.raises(ValueError, match="Unsupported file format"):
            parser.parse(str(test_file))

    def test_parse_unicode_text(self, tmp_path):
        """Test parsing text with Unicode characters"""
        test_file = tmp_path / "test.txt"
        test_file.write_text(
            "Привет мир!\n\n"
            "Hello world!\n\n"
            "你好世界!",
            encoding='utf-8'
        )

        parser = SceneParser()
        scenes = parser.parse(str(test_file))

        assert len(scenes) == 3
        assert scenes[0].text == "Привет мир!"
        assert scenes[1].text == "Hello world!"
        assert scenes[2].text == "你好世界!"

    def test_scene_ids_are_sequential(self, tmp_path):
        """Test that scene IDs are sequential"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("One\n\nTwo\n\nThree\n\nFour", encoding='utf-8')

        parser = SceneParser()
        scenes = parser.parse(str(test_file))

        assert len(scenes) == 4
        for idx, scene in enumerate(scenes, start=1):
            assert scene.id == idx
