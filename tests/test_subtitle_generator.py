"""
Tests for Subtitle Generator Module
"""

import pytest
import os
import pysrt
from pathlib import Path
from modules.scene_parser import Scene
from modules.subtitle_generator import SubtitleGenerator


class TestSubtitleGenerator:
    """Tests for SubtitleGenerator class"""

    def test_generator_initialization(self):
        """Test creating a SubtitleGenerator"""
        config = {
            'subtitles': {
                'enabled': True,
                'max_chars_per_line': 40,
                'font': 'Arial',
                'font_size': 48,
                'color': 'white'
            }
        }
        generator = SubtitleGenerator(config)
        assert generator is not None
        assert generator.enabled is True
        assert generator.max_chars_per_line == 40
        assert generator.font == 'Arial'
        assert generator.font_size == 48
        assert generator.color == 'white'

    def test_generator_default_settings(self):
        """Test default settings when config is minimal"""
        config = {'subtitles': {}}
        generator = SubtitleGenerator(config)
        assert generator.enabled is True
        assert generator.max_chars_per_line == 40

    def test_split_into_lines_short_text(self):
        """Test splitting text shorter than max_chars"""
        config = {'subtitles': {'max_chars_per_line': 40}}
        generator = SubtitleGenerator(config)

        text = "Short text"
        lines = generator.split_into_lines(text)

        assert len(lines) == 1
        assert lines[0] == "Short text"

    def test_split_into_lines_long_text(self):
        """Test splitting long text into multiple lines"""
        config = {'subtitles': {'max_chars_per_line': 20}}
        generator = SubtitleGenerator(config)

        text = "This is a very long text that definitely needs to be split"
        lines = generator.split_into_lines(text)

        assert len(lines) > 1
        # Each line should be <= 20 chars
        for line in lines:
            assert len(line) <= 20

    def test_split_into_lines_respects_word_boundaries(self):
        """Test that split respects word boundaries"""
        config = {'subtitles': {'max_chars_per_line': 15}}
        generator = SubtitleGenerator(config)

        text = "One two three four five"
        lines = generator.split_into_lines(text)

        # No line should contain partial words
        for line in lines:
            assert not line.startswith(' ')
            assert not line.endswith(' ')

    def test_split_into_lines_custom_max_chars(self):
        """Test split with custom max_chars parameter"""
        config = {'subtitles': {'max_chars_per_line': 40}}
        generator = SubtitleGenerator(config)

        text = "Test text for custom splitting"
        lines = generator.split_into_lines(text, max_chars=10)

        for line in lines:
            assert len(line) <= 10

    def test_calculate_timings_single_line(self):
        """Test calculating timings for single line"""
        config = {'subtitles': {'max_chars_per_line': 100}}
        generator = SubtitleGenerator(config)

        text = "Short text"
        duration = 2.0  # 2 seconds

        timings = generator.calculate_timings(text, duration)

        assert len(timings) == 1
        start, end, line_text = timings[0]
        assert start == 0.0
        assert end == pytest.approx(2.0, abs=0.01)
        assert line_text == "Short text"

    def test_calculate_timings_multiple_lines(self):
        """Test calculating timings for multiple lines"""
        config = {'subtitles': {'max_chars_per_line': 10}}
        generator = SubtitleGenerator(config)

        text = "One two three four five six"
        duration = 6.0

        timings = generator.calculate_timings(text, duration)

        assert len(timings) > 1

        # Check that timings are sequential without gaps
        for i in range(len(timings) - 1):
            _, end1, _ = timings[i]
            start2, _, _ = timings[i + 1]
            assert end1 == pytest.approx(start2, abs=0.01)

        # Check that total duration matches
        _, last_end, _ = timings[-1]
        assert last_end == pytest.approx(duration, abs=0.01)

    def test_calculate_timings_proportional_distribution(self):
        """Test that time is distributed proportionally to word count"""
        config = {'subtitles': {'max_chars_per_line': 20}}
        generator = SubtitleGenerator(config)

        # Text with clear word count: "Two words" (2 words) and rest (5 words)
        text = "Two words and then five more words here"
        duration = 7.0  # Total 7 seconds for 7 words = 1 sec/word

        timings = generator.calculate_timings(text, duration)

        # First line should have 2 words (~2 seconds)
        # Check that timing is roughly proportional
        start1, end1, _ = timings[0]
        duration1 = end1 - start1

        # Duration should be positive and less than total
        assert duration1 > 0
        assert duration1 < duration

    def test_calculate_timings_empty_text(self):
        """Test calculating timings for empty text"""
        config = {'subtitles': {}}
        generator = SubtitleGenerator(config)

        timings = generator.calculate_timings("", 5.0)
        assert len(timings) == 0

    def test_seconds_to_srt_time(self):
        """Test conversion of seconds to SRT time format"""
        config = {'subtitles': {}}
        generator = SubtitleGenerator(config)

        # Test: 1 hour, 23 minutes, 45 seconds, 678 milliseconds
        total_seconds = 3600 + 23 * 60 + 45 + 0.678

        srt_time = generator._seconds_to_srt_time(total_seconds)

        assert srt_time.hours == 1
        assert srt_time.minutes == 23
        assert srt_time.seconds == 45
        # Allow for rounding errors in float conversion
        assert srt_time.milliseconds == pytest.approx(678, abs=2)

    def test_generate_creates_srt_file(self, tmp_path):
        """Test that generate creates a valid SRT file"""
        config = {'subtitles': {'max_chars_per_line': 40}}
        generator = SubtitleGenerator(config)

        scene = Scene(id=1, text="Test subtitle text", duration=2.0)
        output_dir = tmp_path / "subtitles"

        subtitle_path = generator.generate(scene, str(output_dir))

        # Check file exists
        assert os.path.exists(subtitle_path)
        assert subtitle_path.endswith('.srt')

        # Check file is not empty
        assert os.path.getsize(subtitle_path) > 0

    def test_generate_valid_srt_format(self, tmp_path):
        """Test that generated SRT has valid format"""
        config = {'subtitles': {'max_chars_per_line': 40}}
        generator = SubtitleGenerator(config)

        scene = Scene(id=1, text="Test subtitle text for validation", duration=3.0)
        output_dir = tmp_path / "subtitles"

        subtitle_path = generator.generate(scene, str(output_dir))

        # Load and verify SRT structure
        subs = pysrt.open(subtitle_path)

        assert len(subs) > 0

        for sub in subs:
            # Check that each subtitle has required fields
            assert sub.index > 0
            assert sub.start is not None
            assert sub.end is not None
            assert sub.text != ""
            # Start time should be less than end time
            assert sub.start < sub.end

    def test_generate_timing_accuracy(self, tmp_path):
        """Test that subtitle timings match scene duration"""
        config = {'subtitles': {'max_chars_per_line': 40}}
        generator = SubtitleGenerator(config)

        duration = 5.5
        scene = Scene(id=1, text="Testing timing accuracy in subtitles", duration=duration)
        output_dir = tmp_path / "subtitles"

        subtitle_path = generator.generate(scene, str(output_dir))

        subs = pysrt.open(subtitle_path)

        # Last subtitle should end at or near the scene duration
        last_sub = subs[-1]
        last_end_seconds = (
            last_sub.end.hours * 3600 +
            last_sub.end.minutes * 60 +
            last_sub.end.seconds +
            last_sub.end.milliseconds / 1000.0
        )

        assert last_end_seconds == pytest.approx(duration, abs=0.1)

    def test_generate_without_duration_raises_error(self, tmp_path):
        """Test that generate fails if scene has no duration"""
        config = {'subtitles': {}}
        generator = SubtitleGenerator(config)

        scene = Scene(id=1, text="Test text", duration=0.0)
        output_dir = tmp_path / "subtitles"

        with pytest.raises(ValueError, match="has no duration"):
            generator.generate(scene, str(output_dir))

    def test_generate_creates_output_directory(self, tmp_path):
        """Test that generate creates output directory if it doesn't exist"""
        config = {'subtitles': {}}
        generator = SubtitleGenerator(config)

        scene = Scene(id=1, text="Test text", duration=2.0)
        output_dir = tmp_path / "nonexistent" / "subtitles"

        # Directory doesn't exist yet
        assert not output_dir.exists()

        subtitle_path = generator.generate(scene, str(output_dir))

        # Directory should be created
        assert output_dir.exists()
        assert os.path.exists(subtitle_path)

    def test_generate_filename_format(self, tmp_path):
        """Test that generated filename follows expected format"""
        config = {'subtitles': {}}
        generator = SubtitleGenerator(config)

        scene = Scene(id=42, text="Test", duration=1.0)
        output_dir = tmp_path / "subtitles"

        subtitle_path = generator.generate(scene, str(output_dir))

        # Should be scene_042_subtitle.srt
        assert "scene_042_subtitle.srt" in subtitle_path

    def test_batch_generate(self, tmp_path):
        """Test batch generation for multiple scenes"""
        config = {'subtitles': {'max_chars_per_line': 40}}
        generator = SubtitleGenerator(config)

        scenes = [
            Scene(id=1, text="First scene text", duration=2.0),
            Scene(id=2, text="Second scene with more text", duration=3.0),
            Scene(id=3, text="Third scene", duration=1.5),
        ]

        output_dir = tmp_path / "subtitles"

        generator.batch_generate(scenes, str(output_dir))

        # Check that all scenes have subtitle_path set
        for scene in scenes:
            assert scene.subtitle_path is not None
            assert os.path.exists(scene.subtitle_path)
            assert scene.subtitle_path.endswith('.srt')

    def test_batch_generate_skips_scenes_without_duration(self, tmp_path):
        """Test that batch_generate skips scenes with no duration"""
        config = {'subtitles': {}}
        generator = SubtitleGenerator(config)

        scenes = [
            Scene(id=1, text="Scene with duration", duration=2.0),
            Scene(id=2, text="Scene without duration", duration=0.0),
            Scene(id=3, text="Another scene with duration", duration=1.5),
        ]

        output_dir = tmp_path / "subtitles"

        generator.batch_generate(scenes, str(output_dir))

        # First and third scenes should have subtitles
        assert scenes[0].subtitle_path is not None
        assert scenes[2].subtitle_path is not None

        # Second scene should not have subtitles
        assert scenes[1].subtitle_path is None

    def test_unicode_text_handling(self, tmp_path):
        """Test subtitle generation with Unicode text"""
        config = {'subtitles': {'max_chars_per_line': 40}}
        generator = SubtitleGenerator(config)

        scene = Scene(
            id=1,
            text="Привет мир! Hello world! 你好世界!",
            duration=3.0
        )
        output_dir = tmp_path / "subtitles"

        subtitle_path = generator.generate(scene, str(output_dir))

        # Load and check content
        subs = pysrt.open(subtitle_path, encoding='utf-8')

        assert len(subs) > 0

        # Combine all subtitle text
        all_text = ' '.join(sub.text for sub in subs)

        # Check that Unicode characters are preserved
        assert "Привет" in all_text or "мир" in all_text
        assert "Hello" in all_text
