"""
Tests for custom exceptions.

This module tests all custom exception classes in utils/exceptions.py.
"""

import pytest
from utils.exceptions import (
    Text2VideoException,
    SceneParseError,
    TTSError,
    SubtitleError,
    VisualError,
    MusicError,
    VideoAssemblyError,
    ConfigError,
    ValidationError,
    DependencyError,
    ResourceNotFoundError,
    ProcessingError,
)


class TestText2VideoException:
    """Tests for base Text2VideoException class."""

    def test_basic_exception(self):
        """Test creating basic exception with message."""
        exc = Text2VideoException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.details is None

    def test_exception_with_details(self):
        """Test creating exception with details."""
        exc = Text2VideoException("Test error", details="Additional info")
        assert "Test error" in str(exc)
        assert "Additional info" in str(exc)
        assert exc.details == "Additional info"

    def test_exception_can_be_raised(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(Text2VideoException) as exc_info:
            raise Text2VideoException("Test error")
        assert "Test error" in str(exc_info.value)

    def test_exception_inherits_from_exception(self):
        """Test that exception inherits from built-in Exception."""
        exc = Text2VideoException("Test")
        assert isinstance(exc, Exception)


class TestSceneParseError:
    """Tests for SceneParseError class."""

    def test_basic_scene_parse_error(self):
        """Test creating basic scene parse error."""
        exc = SceneParseError("Parsing failed")
        assert "Parsing failed" in str(exc)

    def test_scene_parse_error_with_file_path(self):
        """Test scene parse error with file path."""
        exc = SceneParseError("Parsing failed", file_path="test.txt")
        assert "Parsing failed" in str(exc)
        assert "test.txt" in str(exc)
        assert exc.file_path == "test.txt"

    def test_scene_parse_error_with_details(self):
        """Test scene parse error with details."""
        exc = SceneParseError("Parsing failed", file_path="test.txt", details="Invalid format")
        assert "Parsing failed" in str(exc)
        assert "test.txt" in str(exc)
        assert "Invalid format" in str(exc)

    def test_inherits_from_base(self):
        """Test that SceneParseError inherits from Text2VideoException."""
        exc = SceneParseError("Test")
        assert isinstance(exc, Text2VideoException)


class TestTTSError:
    """Tests for TTSError class."""

    def test_basic_tts_error(self):
        """Test creating basic TTS error."""
        exc = TTSError("TTS generation failed")
        assert "TTS generation failed" in str(exc)

    def test_tts_error_with_language(self):
        """Test TTS error with language."""
        exc = TTSError("Model not available", language="ru")
        assert "Model not available" in str(exc)
        assert "ru" in str(exc)
        assert exc.language == "ru"

    def test_tts_error_with_details(self):
        """Test TTS error with details."""
        exc = TTSError("Generation failed", language="en", details="Out of memory")
        assert "Generation failed" in str(exc)
        assert "en" in str(exc)
        assert "Out of memory" in str(exc)

    def test_inherits_from_base(self):
        """Test that TTSError inherits from Text2VideoException."""
        exc = TTSError("Test")
        assert isinstance(exc, Text2VideoException)


class TestSubtitleError:
    """Tests for SubtitleError class."""

    def test_basic_subtitle_error(self):
        """Test creating basic subtitle error."""
        exc = SubtitleError("Subtitle generation failed")
        assert "Subtitle generation failed" in str(exc)

    def test_subtitle_error_with_scene_id(self):
        """Test subtitle error with scene ID."""
        exc = SubtitleError("Timing calculation failed", scene_id="scene_001")
        assert "Timing calculation failed" in str(exc)
        assert "scene_001" in str(exc)
        assert exc.scene_id == "scene_001"

    def test_subtitle_error_with_details(self):
        """Test subtitle error with details."""
        exc = SubtitleError("Failed", scene_id="scene_002", details="Invalid duration")
        assert "Failed" in str(exc)
        assert "scene_002" in str(exc)
        assert "Invalid duration" in str(exc)

    def test_inherits_from_base(self):
        """Test that SubtitleError inherits from Text2VideoException."""
        exc = SubtitleError("Test")
        assert isinstance(exc, Text2VideoException)


class TestVisualError:
    """Tests for VisualError class."""

    def test_basic_visual_error(self):
        """Test creating basic visual error."""
        exc = VisualError("Image processing failed")
        assert "Image processing failed" in str(exc)

    def test_visual_error_with_image_path(self):
        """Test visual error with image path."""
        exc = VisualError("Cannot read image", image_path="test.jpg")
        assert "Cannot read image" in str(exc)
        assert "test.jpg" in str(exc)
        assert exc.image_path == "test.jpg"

    def test_visual_error_with_details(self):
        """Test visual error with details."""
        exc = VisualError("Failed", image_path="img.png", details="Unsupported format")
        assert "Failed" in str(exc)
        assert "img.png" in str(exc)
        assert "Unsupported format" in str(exc)

    def test_inherits_from_base(self):
        """Test that VisualError inherits from Text2VideoException."""
        exc = VisualError("Test")
        assert isinstance(exc, Text2VideoException)


class TestMusicError:
    """Tests for MusicError class."""

    def test_basic_music_error(self):
        """Test creating basic music error."""
        exc = MusicError("Music processing failed")
        assert "Music processing failed" in str(exc)

    def test_music_error_with_music_path(self):
        """Test music error with music path."""
        exc = MusicError("Cannot load music", music_path="track.mp3")
        assert "Cannot load music" in str(exc)
        assert "track.mp3" in str(exc)
        assert exc.music_path == "track.mp3"

    def test_music_error_with_details(self):
        """Test music error with details."""
        exc = MusicError("Failed", music_path="song.wav", details="Corrupted file")
        assert "Failed" in str(exc)
        assert "song.wav" in str(exc)
        assert "Corrupted file" in str(exc)

    def test_inherits_from_base(self):
        """Test that MusicError inherits from Text2VideoException."""
        exc = MusicError("Test")
        assert isinstance(exc, Text2VideoException)


class TestVideoAssemblyError:
    """Tests for VideoAssemblyError class."""

    def test_basic_video_assembly_error(self):
        """Test creating basic video assembly error."""
        exc = VideoAssemblyError("Video assembly failed")
        assert "Video assembly failed" in str(exc)

    def test_video_assembly_error_with_output_path(self):
        """Test video assembly error with output path."""
        exc = VideoAssemblyError("Encoding failed", output_path="output.mp4")
        assert "Encoding failed" in str(exc)
        assert "output.mp4" in str(exc)
        assert exc.output_path == "output.mp4"

    def test_video_assembly_error_with_details(self):
        """Test video assembly error with details."""
        exc = VideoAssemblyError("Failed", output_path="video.mp4", details="FFmpeg error")
        assert "Failed" in str(exc)
        assert "video.mp4" in str(exc)
        assert "FFmpeg error" in str(exc)

    def test_inherits_from_base(self):
        """Test that VideoAssemblyError inherits from Text2VideoException."""
        exc = VideoAssemblyError("Test")
        assert isinstance(exc, Text2VideoException)


class TestConfigError:
    """Tests for ConfigError class."""

    def test_basic_config_error(self):
        """Test creating basic config error."""
        exc = ConfigError("Invalid configuration")
        assert "Invalid configuration" in str(exc)

    def test_config_error_with_config_path(self):
        """Test config error with config path."""
        exc = ConfigError("Cannot read config", config_path="config.yaml")
        assert "Cannot read config" in str(exc)
        assert "config.yaml" in str(exc)
        assert exc.config_path == "config.yaml"

    def test_config_error_with_details(self):
        """Test config error with details."""
        exc = ConfigError("Failed", config_path="cfg.yaml", details="Missing field")
        assert "Failed" in str(exc)
        assert "cfg.yaml" in str(exc)
        assert "Missing field" in str(exc)

    def test_inherits_from_base(self):
        """Test that ConfigError inherits from Text2VideoException."""
        exc = ConfigError("Test")
        assert isinstance(exc, Text2VideoException)


class TestValidationError:
    """Tests for ValidationError class."""

    def test_basic_validation_error(self):
        """Test creating basic validation error."""
        exc = ValidationError("Validation failed")
        assert "Validation failed" in str(exc)

    def test_validation_error_with_field_name(self):
        """Test validation error with field name."""
        exc = ValidationError("Invalid value", field_name="fps")
        assert "Invalid value" in str(exc)
        assert "fps" in str(exc)
        assert exc.field_name == "fps"

    def test_validation_error_with_details(self):
        """Test validation error with details."""
        exc = ValidationError("Failed", field_name="resolution", details="Must be positive")
        assert "Failed" in str(exc)
        assert "resolution" in str(exc)
        assert "Must be positive" in str(exc)

    def test_inherits_from_base(self):
        """Test that ValidationError inherits from Text2VideoException."""
        exc = ValidationError("Test")
        assert isinstance(exc, Text2VideoException)


class TestDependencyError:
    """Tests for DependencyError class."""

    def test_basic_dependency_error(self):
        """Test creating basic dependency error."""
        exc = DependencyError("Missing dependency")
        assert "Missing dependency" in str(exc)

    def test_dependency_error_with_dependency(self):
        """Test dependency error with dependency name."""
        exc = DependencyError("Not found", dependency="ffmpeg")
        assert "Not found" in str(exc)
        assert "ffmpeg" in str(exc)
        assert exc.dependency == "ffmpeg"

    def test_dependency_error_with_details(self):
        """Test dependency error with details."""
        exc = DependencyError("Missing", dependency="TTS", details="pip install TTS")
        assert "Missing" in str(exc)
        assert "TTS" in str(exc)
        assert "pip install TTS" in str(exc)

    def test_inherits_from_base(self):
        """Test that DependencyError inherits from Text2VideoException."""
        exc = DependencyError("Test")
        assert isinstance(exc, Text2VideoException)


class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError class."""

    def test_basic_resource_not_found_error(self):
        """Test creating basic resource not found error."""
        exc = ResourceNotFoundError("Resource not found")
        assert "Resource not found" in str(exc)

    def test_resource_not_found_error_with_path(self):
        """Test resource not found error with resource path."""
        exc = ResourceNotFoundError("Not found", resource_path="image.jpg")
        assert "Not found" in str(exc)
        assert "image.jpg" in str(exc)
        assert exc.resource_path == "image.jpg"

    def test_resource_not_found_error_with_details(self):
        """Test resource not found error with details."""
        exc = ResourceNotFoundError("Missing", resource_path="font.ttf", details="Check path")
        assert "Missing" in str(exc)
        assert "font.ttf" in str(exc)
        assert "Check path" in str(exc)

    def test_inherits_from_base(self):
        """Test that ResourceNotFoundError inherits from Text2VideoException."""
        exc = ResourceNotFoundError("Test")
        assert isinstance(exc, Text2VideoException)


class TestProcessingError:
    """Tests for ProcessingError class."""

    def test_basic_processing_error(self):
        """Test creating basic processing error."""
        exc = ProcessingError("Processing failed")
        assert "Processing failed" in str(exc)

    def test_processing_error_with_step(self):
        """Test processing error with step name."""
        exc = ProcessingError("Failed", step="audio_generation")
        assert "Failed" in str(exc)
        assert "audio_generation" in str(exc)
        assert exc.step == "audio_generation"

    def test_processing_error_with_details(self):
        """Test processing error with details."""
        exc = ProcessingError("Error", step="rendering", details="Timeout")
        assert "Error" in str(exc)
        assert "rendering" in str(exc)
        assert "Timeout" in str(exc)

    def test_inherits_from_base(self):
        """Test that ProcessingError inherits from Text2VideoException."""
        exc = ProcessingError("Test")
        assert isinstance(exc, Text2VideoException)


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_inherit_from_base(self):
        """Test that all custom exceptions inherit from Text2VideoException."""
        exceptions = [
            SceneParseError("test"),
            TTSError("test"),
            SubtitleError("test"),
            VisualError("test"),
            MusicError("test"),
            VideoAssemblyError("test"),
            ConfigError("test"),
            ValidationError("test"),
            DependencyError("test"),
            ResourceNotFoundError("test"),
            ProcessingError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, Text2VideoException)
            assert isinstance(exc, Exception)

    def test_can_catch_all_with_base(self):
        """Test that all exceptions can be caught with base exception."""
        try:
            raise TTSError("Test error")
        except Text2VideoException as e:
            assert "Test error" in str(e)

    def test_can_catch_specific_exception(self):
        """Test that specific exceptions can be caught."""
        try:
            raise SceneParseError("Parse error")
        except SceneParseError as e:
            assert "Parse error" in str(e)
        except Text2VideoException:
            pytest.fail("Should have caught SceneParseError specifically")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
