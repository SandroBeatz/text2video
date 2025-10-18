"""
Subtitle Generator Module
Handles subtitle generation and synchronization with audio
"""

import os
import pysrt
from typing import List, Tuple
from modules.scene_parser import Scene


class SubtitleGenerator:
    """
    Generator for creating synchronized SRT subtitle files
    """

    def __init__(self, config: dict):
        """
        Initialize subtitle generator

        Args:
            config: Configuration dictionary with subtitle settings
        """
        self.config = config
        subtitle_config = config.get('subtitles', {})

        self.enabled = subtitle_config.get('enabled', True)
        self.max_chars_per_line = subtitle_config.get('max_chars_per_line', 40)
        self.font = subtitle_config.get('font', 'Arial')
        self.font_size = subtitle_config.get('font_size', 48)
        self.color = subtitle_config.get('color', 'white')

    def generate(self, scene: Scene, output_dir: str) -> str:
        """
        Generate subtitle file for a scene

        Args:
            scene: Scene object with text and duration
            output_dir: Directory to save subtitle file

        Returns:
            Path to generated SRT file

        Raises:
            ValueError: If scene has no duration set
            RuntimeError: If subtitle generation fails
        """
        if scene.duration <= 0:
            raise ValueError(
                f"Scene {scene.id} has no duration set. "
                "Generate audio first to calculate duration."
            )

        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        output_filename = f"scene_{scene.id:03d}_subtitle.srt"
        output_path = os.path.join(output_dir, output_filename)

        try:
            # Calculate subtitle timings
            timings = self.calculate_timings(scene.text, scene.duration)

            # Create SRT file
            self._create_srt_file(timings, output_path)

            return output_path

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate subtitles for scene {scene.id}: {e}"
            )

    def split_into_lines(self, text: str, max_chars: int = None) -> List[str]:
        """
        Split text into lines respecting word boundaries

        Args:
            text: Text to split
            max_chars: Maximum characters per line (uses config default if None)

        Returns:
            List of text lines

        Examples:
            >>> gen = SubtitleGenerator({'subtitles': {'max_chars_per_line': 20}})
            >>> gen.split_into_lines("This is a long text that needs splitting")
            ['This is a long text', 'that needs splitting']
        """
        if max_chars is None:
            max_chars = self.max_chars_per_line

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            # +1 for the space before the word
            space_needed = word_length + (1 if current_line else 0)

            if current_length + space_needed <= max_chars:
                # Word fits in current line
                current_line.append(word)
                current_length += space_needed
            else:
                # Start new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        # Add last line
        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def calculate_timings(self, text: str, duration: float) -> List[Tuple[float, float, str]]:
        """
        Calculate subtitle timings based on text and audio duration

        Args:
            text: Text to create subtitles for
            duration: Total duration in seconds

        Returns:
            List of tuples (start_time, end_time, subtitle_text)

        Algorithm:
            1. Split text into lines respecting max_chars_per_line
            2. Calculate time per word
            3. Distribute time proportionally to word count in each line
        """
        # Split text into lines
        lines = self.split_into_lines(text)

        if not lines:
            return []

        # Count total words
        total_words = sum(len(line.split()) for line in lines)

        if total_words == 0:
            return []

        # Calculate time per word
        time_per_word = duration / total_words

        # Calculate timings for each line
        timings = []
        current_time = 0.0

        for line in lines:
            words_in_line = len(line.split())
            line_duration = words_in_line * time_per_word

            start_time = current_time
            end_time = current_time + line_duration

            timings.append((start_time, end_time, line))

            current_time = end_time

        return timings

    def _create_srt_file(self, timings: List[Tuple[float, float, str]], output_path: str):
        """
        Create SRT file from timings

        Args:
            timings: List of (start, end, text) tuples
            output_path: Path where to save the SRT file
        """
        subs = pysrt.SubRipFile()

        for idx, (start, end, text) in enumerate(timings, start=1):
            # Convert seconds to SubRipTime format (hours, minutes, seconds, milliseconds)
            start_time = self._seconds_to_srt_time(start)
            end_time = self._seconds_to_srt_time(end)

            # Create subtitle item
            sub = pysrt.SubRipItem(
                index=idx,
                start=start_time,
                end=end_time,
                text=text
            )

            subs.append(sub)

        # Save to file
        subs.save(output_path, encoding='utf-8')

    def _seconds_to_srt_time(self, seconds: float) -> pysrt.SubRipTime:
        """
        Convert seconds to SubRipTime object

        Args:
            seconds: Time in seconds

        Returns:
            SubRipTime object
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)

        return pysrt.SubRipTime(
            hours=hours,
            minutes=minutes,
            seconds=secs,
            milliseconds=milliseconds
        )

    def batch_generate(self, scenes: List[Scene], output_dir: str) -> None:
        """
        Generate subtitles for multiple scenes

        Args:
            scenes: List of Scene objects
            output_dir: Directory to save subtitle files

        Note:
            This method updates each scene's subtitle_path
        """
        for scene in scenes:
            if scene.duration > 0:  # Only generate if duration is set
                subtitle_path = self.generate(scene, output_dir)
                scene.subtitle_path = subtitle_path
