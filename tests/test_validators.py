"""
Tests for validation utilities.

This module tests all validation functions in utils/validators.py.
"""

import pytest
import os
import tempfile
from pathlib import Path
from utils.validators import (
    validate_file_exists,
    validate_file_format,
    validate_directory_exists,
    validate_config,
    validate_resolution,
    validate_aspect_ratio,
    validate_language,
    validate_fps,
    validate_volume,
    validate_duration,
    validate_path_is_safe,
    validate_text_content,
)


class TestValidateFileExists:
    """Tests for validate_file_exists function."""

    def test_existing_file(self, tmp_path):
        """Test validation of an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        assert validate_file_exists(str(test_file)) is True

    def test_nonexistent_file(self, tmp_path):
        """Test validation of a non-existent file."""
        test_file = tmp_path / "nonexistent.txt"

        assert validate_file_exists(str(test_file)) is False

    def test_empty_path(self):
        """Test validation with empty path."""
        assert validate_file_exists("") is False

    def test_directory_not_file(self, tmp_path):
        """Test that directory is not validated as a file."""
        assert validate_file_exists(str(tmp_path)) is False


class TestValidateFileFormat:
    """Tests for validate_file_format function."""

    def test_valid_format_txt(self):
        """Test validation of .txt file."""
        assert validate_file_format("test.txt", [".txt", ".md"]) is True

    def test_valid_format_md(self):
        """Test validation of .md file."""
        assert validate_file_format("test.md", [".txt", ".md"]) is True

    def test_invalid_format(self):
        """Test validation of invalid file format."""
        assert validate_file_format("test.pdf", [".txt", ".md"]) is False

    def test_format_without_dot(self):
        """Test that formats without leading dot are normalized."""
        assert validate_file_format("test.txt", ["txt", "md"]) is True

    def test_case_insensitive(self):
        """Test that format validation is case-insensitive."""
        assert validate_file_format("test.TXT", [".txt"]) is True

    def test_empty_path(self):
        """Test validation with empty path."""
        assert validate_file_format("", [".txt"]) is False

    def test_empty_formats_list(self):
        """Test validation with empty formats list."""
        assert validate_file_format("test.txt", []) is False


class TestValidateDirectoryExists:
    """Tests for validate_directory_exists function."""

    def test_existing_directory(self, tmp_path):
        """Test validation of existing directory."""
        assert validate_directory_exists(str(tmp_path)) is True

    def test_nonexistent_directory(self, tmp_path):
        """Test validation of non-existent directory."""
        test_dir = tmp_path / "nonexistent"
        assert validate_directory_exists(str(test_dir)) is False

    def test_create_if_missing(self, tmp_path):
        """Test directory creation when create_if_missing=True."""
        test_dir = tmp_path / "new_dir"
        assert validate_directory_exists(str(test_dir), create_if_missing=True) is True
        assert test_dir.exists()

    def test_empty_path(self):
        """Test validation with empty path."""
        assert validate_directory_exists("") is False


class TestValidateConfig:
    """Tests for validate_config function."""

    def test_valid_config(self):
        """Test validation of a valid configuration."""
        config = {
            'project': {'name': 'Test Project'},
            'video': {
                'fps': 30,
                'resolution': {'width': 1920, 'height': 1080},
                'codec': 'libx264'
            },
            'tts': {'language': 'en'},
            'subtitles': {},
            'audio': {},
            'paths': {'music_dir': './music', 'temp_dir': './temp'}
        }
        assert validate_config(config) is True

    def test_empty_config(self):
        """Test validation of empty config."""
        assert validate_config({}) is False

    def test_missing_project_section(self):
        """Test validation with missing project section."""
        config = {
            'video': {'fps': 30, 'resolution': {'width': 1920, 'height': 1080}, 'codec': 'libx264'},
            'tts': {'language': 'en'},
            'subtitles': {},
            'audio': {},
            'paths': {'music_dir': './music', 'temp_dir': './temp'}
        }
        assert validate_config(config) is False

    def test_missing_project_name(self):
        """Test validation with missing project name."""
        config = {
            'project': {},  # Missing 'name'
            'video': {'fps': 30, 'resolution': {'width': 1920, 'height': 1080}, 'codec': 'libx264'},
            'tts': {'language': 'en'},
            'subtitles': {},
            'audio': {},
            'paths': {'music_dir': './music', 'temp_dir': './temp'}
        }
        assert validate_config(config) is False

    def test_missing_video_fps(self):
        """Test validation with missing video FPS."""
        config = {
            'project': {'name': 'Test'},
            'video': {'resolution': {'width': 1920, 'height': 1080}, 'codec': 'libx264'},
            'tts': {'language': 'en'},
            'subtitles': {},
            'audio': {},
            'paths': {'music_dir': './music', 'temp_dir': './temp'}
        }
        assert validate_config(config) is False

    def test_missing_resolution_width(self):
        """Test validation with missing resolution width."""
        config = {
            'project': {'name': 'Test'},
            'video': {'fps': 30, 'resolution': {'height': 1080}, 'codec': 'libx264'},
            'tts': {'language': 'en'},
            'subtitles': {},
            'audio': {},
            'paths': {'music_dir': './music', 'temp_dir': './temp'}
        }
        assert validate_config(config) is False

    def test_missing_tts_language(self):
        """Test validation with missing TTS language."""
        config = {
            'project': {'name': 'Test'},
            'video': {'fps': 30, 'resolution': {'width': 1920, 'height': 1080}, 'codec': 'libx264'},
            'tts': {},
            'subtitles': {},
            'audio': {},
            'paths': {'music_dir': './music', 'temp_dir': './temp'}
        }
        assert validate_config(config) is False

    def test_missing_paths_music_dir(self):
        """Test validation with missing music_dir in paths."""
        config = {
            'project': {'name': 'Test'},
            'video': {'fps': 30, 'resolution': {'width': 1920, 'height': 1080}, 'codec': 'libx264'},
            'tts': {'language': 'en'},
            'subtitles': {},
            'audio': {},
            'paths': {'temp_dir': './temp'}  # Missing 'music_dir'
        }
        assert validate_config(config) is False


class TestValidateResolution:
    """Tests for validate_resolution function."""

    def test_valid_hd_resolution(self):
        """Test validation of 1920x1080 resolution."""
        assert validate_resolution(1920, 1080) is True

    def test_valid_4k_resolution(self):
        """Test validation of 4K resolution."""
        assert validate_resolution(3840, 2160) is True

    def test_zero_width(self):
        """Test validation with zero width."""
        assert validate_resolution(0, 1080) is False

    def test_negative_height(self):
        """Test validation with negative height."""
        assert validate_resolution(1920, -1080) is False

    def test_very_high_resolution(self):
        """Test validation with very high resolution (8K)."""
        # Should return True but with a warning
        assert validate_resolution(7680, 4320) is True

    def test_very_low_resolution(self):
        """Test validation with very low resolution."""
        # Should return True but with a warning
        assert validate_resolution(320, 240) is True


class TestValidateAspectRatio:
    """Tests for validate_aspect_ratio function."""

    def test_valid_16_9(self):
        """Test validation of 16:9 aspect ratio."""
        assert validate_aspect_ratio("16:9") is True

    def test_valid_9_16(self):
        """Test validation of 9:16 aspect ratio."""
        assert validate_aspect_ratio("9:16") is True

    def test_valid_1_1(self):
        """Test validation of 1:1 aspect ratio."""
        assert validate_aspect_ratio("1:1") is True

    def test_valid_4_3(self):
        """Test validation of 4:3 aspect ratio."""
        assert validate_aspect_ratio("4:3") is True

    def test_invalid_aspect_ratio(self):
        """Test validation of invalid aspect ratio."""
        assert validate_aspect_ratio("16:10") is False


class TestValidateLanguage:
    """Tests for validate_language function."""

    def test_valid_russian(self):
        """Test validation of Russian language."""
        assert validate_language("ru") is True

    def test_valid_english(self):
        """Test validation of English language."""
        assert validate_language("en") is True

    def test_invalid_language(self):
        """Test validation of unsupported language."""
        assert validate_language("fr") is False


class TestValidateFps:
    """Tests for validate_fps function."""

    def test_valid_30_fps(self):
        """Test validation of 30 FPS."""
        assert validate_fps(30) is True

    def test_valid_60_fps(self):
        """Test validation of 60 FPS."""
        assert validate_fps(60) is True

    def test_zero_fps(self):
        """Test validation of zero FPS."""
        assert validate_fps(0) is False

    def test_negative_fps(self):
        """Test validation of negative FPS."""
        assert validate_fps(-30) is False

    def test_very_low_fps(self):
        """Test validation of very low FPS."""
        # Should return True but with a warning
        assert validate_fps(5) is True

    def test_very_high_fps(self):
        """Test validation of very high FPS."""
        # Should return True but with a warning
        assert validate_fps(240) is True


class TestValidateVolume:
    """Tests for validate_volume function."""

    def test_valid_volume_zero(self):
        """Test validation of volume 0.0."""
        assert validate_volume(0.0) is True

    def test_valid_volume_half(self):
        """Test validation of volume 0.5."""
        assert validate_volume(0.5) is True

    def test_valid_volume_one(self):
        """Test validation of volume 1.0."""
        assert validate_volume(1.0) is True

    def test_negative_volume(self):
        """Test validation of negative volume."""
        assert validate_volume(-0.1) is False

    def test_volume_too_high(self):
        """Test validation of volume > 1.0."""
        assert validate_volume(1.5) is False

    def test_custom_param_name(self):
        """Test validation with custom parameter name."""
        # Should still validate correctly
        assert validate_volume(0.5, "music_volume") is True


class TestValidateDuration:
    """Tests for validate_duration function."""

    def test_valid_duration(self):
        """Test validation of valid duration."""
        assert validate_duration(10.0) is True

    def test_zero_duration(self):
        """Test validation of zero duration."""
        assert validate_duration(0.0) is False

    def test_negative_duration(self):
        """Test validation of negative duration."""
        assert validate_duration(-5.0) is False

    def test_very_long_duration(self):
        """Test validation of very long duration."""
        # Should return True but with a warning
        assert validate_duration(7200) is True  # 2 hours


class TestValidatePathIsSafe:
    """Tests for validate_path_is_safe function."""

    def test_safe_relative_path(self):
        """Test validation of safe relative path."""
        assert validate_path_is_safe("output/video.mp4") is True

    def test_path_traversal_attempt(self):
        """Test detection of path traversal attempt."""
        assert validate_path_is_safe("../../../etc/passwd") is False

    def test_absolute_path(self):
        """Test detection of absolute path."""
        assert validate_path_is_safe("/etc/passwd") is False

    def test_empty_path(self):
        """Test validation of empty path."""
        assert validate_path_is_safe("") is False


class TestValidateTextContent:
    """Tests for validate_text_content function."""

    def test_valid_text(self):
        """Test validation of valid text."""
        assert validate_text_content("This is a test text.") is True

    def test_empty_text(self):
        """Test validation of empty text."""
        assert validate_text_content("") is False

    def test_text_too_short(self):
        """Test validation of text that's too short."""
        assert validate_text_content("Hi", min_length=10) is False

    def test_text_too_long(self):
        """Test validation of text that's too long."""
        long_text = "a" * 1000
        assert validate_text_content(long_text, max_length=100) is False

    def test_text_at_min_boundary(self):
        """Test validation of text at minimum length boundary."""
        assert validate_text_content("Hello", min_length=5) is True

    def test_text_at_max_boundary(self):
        """Test validation of text at maximum length boundary."""
        assert validate_text_content("Hello", max_length=5) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
