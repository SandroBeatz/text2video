"""
Music Selector Module
Handles background music selection, duration adjustment, and mixing
"""

import os
import random
from typing import List, Optional
from pydub import AudioSegment
from pydub.effects import normalize


class MusicSelector:
    """
    Selector for choosing and processing background music
    """

    # Supported audio formats
    SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')

    def __init__(self, config: dict):
        """
        Initialize music selector

        Args:
            config: Configuration dictionary with audio settings
        """
        self.config = config
        audio_config = config.get('audio', {})
        music_config = audio_config.get('music', {})

        self.enabled = music_config.get('enabled', True)
        self.music_volume = music_config.get('volume', 0.2)
        self.fade_in_duration = music_config.get('fade_in', 2.0)
        self.fade_out_duration = music_config.get('fade_out', 3.0)

        # Paths
        paths_config = config.get('paths', {})
        self.music_dir = paths_config.get('music_dir', './assets/music')

    def select_music(self, music_dir: str = None) -> str:
        """
        Select a random music file from the music directory

        Args:
            music_dir: Directory containing music files (uses config default if None)

        Returns:
            Path to selected music file

        Raises:
            FileNotFoundError: If music directory doesn't exist or is empty
        """
        if music_dir is None:
            music_dir = self.music_dir

        # Check if directory exists
        if not os.path.exists(music_dir):
            raise FileNotFoundError(f"Music directory not found: {music_dir}")

        # Get list of music files
        music_files = self._get_music_files(music_dir)

        if not music_files:
            raise FileNotFoundError(
                f"No music files found in {music_dir}. "
                f"Supported formats: {self.SUPPORTED_FORMATS}"
            )

        # Select random music file
        selected_music = random.choice(music_files)

        return selected_music

    def _get_music_files(self, directory: str) -> List[str]:
        """
        Get list of music files from directory

        Args:
            directory: Path to directory

        Returns:
            List of full paths to music files
        """
        music_files = []

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)

            # Check if it's a file and has supported extension
            if os.path.isfile(filepath) and filename.lower().endswith(self.SUPPORTED_FORMATS):
                music_files.append(filepath)

        return sorted(music_files)  # Sort for consistent ordering

    def adjust_duration(
        self,
        music_path: str,
        target_duration: float,
        output_dir: str = None
    ) -> str:
        """
        Adjust music duration to match target (trim or loop)

        Args:
            music_path: Path to source music file
            target_duration: Target duration in seconds
            output_dir: Directory to save adjusted music

        Returns:
            Path to adjusted music file

        Raises:
            FileNotFoundError: If source music doesn't exist
            RuntimeError: If audio processing fails

        Algorithm:
            - If music is longer than target: trim from start
            - If music is shorter than target: loop until duration matches
        """
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"Music file not found: {music_path}")

        try:
            # Load music
            music = AudioSegment.from_file(music_path)

            # Get original duration in milliseconds
            original_duration_ms = len(music)
            target_duration_ms = int(target_duration * 1000)

            if original_duration_ms > target_duration_ms:
                # Trim music to target duration
                adjusted_music = music[:target_duration_ms]
            elif original_duration_ms < target_duration_ms:
                # Loop music to reach target duration
                loops_needed = (target_duration_ms // original_duration_ms) + 1
                looped_music = music * int(loops_needed)
                adjusted_music = looped_music[:target_duration_ms]
            else:
                # Duration matches exactly
                adjusted_music = music

            # Generate output filename
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(music_path), 'adjusted')

            os.makedirs(output_dir, exist_ok=True)

            # Create output filename
            base_name = os.path.basename(music_path)
            name, _ = os.path.splitext(base_name)
            output_filename = f"{name}_adjusted_{int(target_duration)}s.mp3"
            output_path = os.path.join(output_dir, output_filename)

            # Export adjusted music
            adjusted_music.export(output_path, format='mp3')

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to adjust music duration {music_path}: {e}")

    def apply_fade(
        self,
        music_path: str,
        fade_in: float = None,
        fade_out: float = None,
        output_dir: str = None
    ) -> str:
        """
        Apply fade in/out effects to music

        Args:
            music_path: Path to source music file
            fade_in: Fade in duration in seconds (uses config default if None)
            fade_out: Fade out duration in seconds (uses config default if None)
            output_dir: Directory to save processed music

        Returns:
            Path to processed music file

        Raises:
            FileNotFoundError: If source music doesn't exist
            RuntimeError: If audio processing fails
        """
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"Music file not found: {music_path}")

        if fade_in is None:
            fade_in = self.fade_in_duration
        if fade_out is None:
            fade_out = self.fade_out_duration

        try:
            # Load music
            music = AudioSegment.from_file(music_path)

            # Apply fade effects
            fade_in_ms = int(fade_in * 1000)
            fade_out_ms = int(fade_out * 1000)

            faded_music = music.fade_in(fade_in_ms).fade_out(fade_out_ms)

            # Generate output filename
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(music_path), 'faded')

            os.makedirs(output_dir, exist_ok=True)

            # Create output filename
            base_name = os.path.basename(music_path)
            name, _ = os.path.splitext(base_name)
            output_filename = f"{name}_faded.mp3"
            output_path = os.path.join(output_dir, output_filename)

            # Export faded music
            faded_music.export(output_path, format='mp3')

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to apply fade effects to {music_path}: {e}")

    def adjust_volume(
        self,
        music_path: str,
        volume_level: float = None,
        output_dir: str = None
    ) -> str:
        """
        Adjust music volume

        Args:
            music_path: Path to source music file
            volume_level: Volume level (0.0 to 1.0), uses config default if None
            output_dir: Directory to save adjusted music

        Returns:
            Path to volume-adjusted music file

        Raises:
            FileNotFoundError: If source music doesn't exist
            ValueError: If volume_level is out of range
            RuntimeError: If audio processing fails
        """
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"Music file not found: {music_path}")

        if volume_level is None:
            volume_level = self.music_volume

        if not 0.0 <= volume_level <= 1.0:
            raise ValueError(f"Volume level must be between 0.0 and 1.0, got {volume_level}")

        try:
            # Load music
            music = AudioSegment.from_file(music_path)

            # Calculate volume change in dB
            # 0.0 volume -> -infinity dB (silence)
            # 1.0 volume -> 0 dB (no change)
            # Formula: dB = 20 * log10(volume_level)
            # We use a simpler linear approximation for clarity
            if volume_level == 0.0:
                db_change = -100  # Effectively silent
            else:
                # Convert 0.0-1.0 to dB scale
                # Reference: 1.0 = 0dB, 0.5 = -6dB, 0.25 = -12dB
                import math
                db_change = 20 * math.log10(volume_level)

            # Apply volume change
            adjusted_music = music + db_change

            # Generate output filename
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(music_path), 'adjusted_volume')

            os.makedirs(output_dir, exist_ok=True)

            # Create output filename
            base_name = os.path.basename(music_path)
            name, _ = os.path.splitext(base_name)
            output_filename = f"{name}_vol_{int(volume_level * 100)}.mp3"
            output_path = os.path.join(output_dir, output_filename)

            # Export adjusted music
            adjusted_music.export(output_path, format='mp3')

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to adjust volume for {music_path}: {e}")

    def mix_with_voice(
        self,
        voice_path: str,
        music_path: str,
        output_dir: str = None,
        music_volume: float = None
    ) -> str:
        """
        Mix background music with voice audio

        Args:
            voice_path: Path to voice audio file
            music_path: Path to background music file
            output_dir: Directory to save mixed audio
            music_volume: Music volume level (0.0-1.0), uses config default if None

        Returns:
            Path to mixed audio file

        Raises:
            FileNotFoundError: If voice or music file doesn't exist
            RuntimeError: If audio mixing fails

        Note:
            Music is automatically adjusted to match voice duration
            and volume-adjusted before mixing
        """
        if not os.path.exists(voice_path):
            raise FileNotFoundError(f"Voice file not found: {voice_path}")
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"Music file not found: {music_path}")

        if music_volume is None:
            music_volume = self.music_volume

        try:
            # Load audio files
            voice = AudioSegment.from_file(voice_path)
            music = AudioSegment.from_file(music_path)

            # Get voice duration
            voice_duration_ms = len(voice)
            voice_duration_sec = voice_duration_ms / 1000.0

            # Adjust music duration to match voice
            target_duration_ms = voice_duration_ms
            music_duration_ms = len(music)

            if music_duration_ms > target_duration_ms:
                # Trim music
                adjusted_music = music[:target_duration_ms]
            elif music_duration_ms < target_duration_ms:
                # Loop music
                loops_needed = (target_duration_ms // music_duration_ms) + 1
                looped_music = music * int(loops_needed)
                adjusted_music = looped_music[:target_duration_ms]
            else:
                adjusted_music = music

            # Apply fade effects to music
            fade_in_ms = int(self.fade_in_duration * 1000)
            fade_out_ms = int(self.fade_out_duration * 1000)
            faded_music = adjusted_music.fade_in(fade_in_ms).fade_out(fade_out_ms)

            # Adjust music volume
            import math
            if music_volume == 0.0:
                db_change = -100
            else:
                db_change = 20 * math.log10(music_volume)

            volume_adjusted_music = faded_music + db_change

            # Mix voice and music (overlay)
            mixed_audio = voice.overlay(volume_adjusted_music)

            # Generate output filename
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(voice_path), 'mixed')

            os.makedirs(output_dir, exist_ok=True)

            # Create output filename
            voice_base = os.path.basename(voice_path)
            voice_name, _ = os.path.splitext(voice_base)
            output_filename = f"{voice_name}_with_music.mp3"
            output_path = os.path.join(output_dir, output_filename)

            # Export mixed audio
            mixed_audio.export(output_path, format='mp3')

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to mix voice and music: {e}")

    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get information about an audio file

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with audio information

        Raises:
            FileNotFoundError: If audio file doesn't exist
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            audio = AudioSegment.from_file(audio_path)

            return {
                'duration': len(audio) / 1000.0,  # Convert to seconds
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'frame_rate': audio.frame_rate,
                'frame_width': audio.frame_width,
                'size': os.path.getsize(audio_path)
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get audio info: {e}")
