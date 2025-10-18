"""
Video Assembler Module
Handles final video assembly from scenes, images, audio, and subtitles
"""

import os
from typing import List, Optional
from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    TextClip,
    CompositeAudioClip,
    VideoFileClip
)
import pysrt


class VideoAssembler:
    """
    Assembler for creating final video from processed scenes
    """

    def __init__(self, config: dict):
        """
        Initialize video assembler

        Args:
            config: Configuration dictionary with video settings
        """
        self.config = config
        video_config = config.get('video', {})
        subtitle_config = config.get('subtitles', {})
        project_config = config.get('project', {})

        # Video settings
        self.fps = video_config.get('fps', 30)
        resolution = video_config.get('resolution', {})
        self.width = resolution.get('width', 1920)
        self.height = resolution.get('height', 1080)
        self.codec = video_config.get('codec', 'libx264')
        self.bitrate = video_config.get('bitrate', '5000k')

        # Subtitle settings
        self.subtitle_enabled = subtitle_config.get('enabled', True)
        self.subtitle_font = subtitle_config.get('font', 'Arial')
        self.subtitle_font_size = subtitle_config.get('font_size', 48)
        self.subtitle_color = subtitle_config.get('color', 'white')
        self.subtitle_position = subtitle_config.get('position', 'bottom')

        # Project settings
        self.output_dir = project_config.get('output_dir', './output')

    def assemble(
        self,
        scenes: List,
        output_path: str,
        background_music_path: Optional[str] = None
    ) -> str:
        """
        Assemble final video from all scenes

        Args:
            scenes: List of Scene objects with all paths set
            output_path: Path where to save the final video
            background_music_path: Optional path to background music

        Returns:
            Path to the assembled video file

        Raises:
            ValueError: If scenes list is empty or scenes are not properly configured
            RuntimeError: If video assembly fails
        """
        if not scenes:
            raise ValueError("Cannot assemble video: scenes list is empty")

        # Validate scenes
        for scene in scenes:
            if not scene.image_path or not os.path.exists(scene.image_path):
                raise ValueError(f"Scene {scene.id} has no valid image_path")
            if not scene.audio_path or not os.path.exists(scene.audio_path):
                raise ValueError(f"Scene {scene.id} has no valid audio_path")
            if scene.duration <= 0:
                raise ValueError(f"Scene {scene.id} has invalid duration: {scene.duration}")

        try:
            # Create clips for each scene
            scene_clips = []
            for scene in scenes:
                clip = self.create_scene_clip(scene)
                scene_clips.append(clip)

            # Concatenate all scene clips
            final_video = concatenate_videoclips(scene_clips, method='compose')

            # Add background music if provided
            if background_music_path and os.path.exists(background_music_path):
                background_music = AudioFileClip(background_music_path)

                # Adjust music duration to match video
                video_duration = final_video.duration
                if background_music.duration > video_duration:
                    background_music = background_music.subclipped(0, video_duration)
                elif background_music.duration < video_duration:
                    # Loop music by concatenating
                    from moviepy import concatenate_audioclips
                    loops_needed = int(video_duration / background_music.duration) + 1
                    looped_clips = [background_music] * loops_needed
                    background_music = concatenate_audioclips(looped_clips)
                    background_music = background_music.subclipped(0, video_duration)

                # Mix background music with existing audio
                # Background music at lower volume
                music_volume = self.config.get('audio', {}).get('music', {}).get('volume', 0.2)
                background_music = background_music.with_volume_scaled(music_volume)

                # Composite audio (original audio + background music)
                final_audio = CompositeAudioClip([final_video.audio, background_music])
                final_video = final_video.with_audio(final_audio)

            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Write final video
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec=self.codec,
                bitrate=self.bitrate,
                audio_codec='aac',
                preset='medium',
                threads=4
            )

            # Clean up
            final_video.close()
            for clip in scene_clips:
                clip.close()

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to assemble video: {e}")

    def create_scene_clip(self, scene) -> CompositeVideoClip:
        """
        Create a video clip for a single scene

        Args:
            scene: Scene object with image_path, audio_path, subtitle_path, duration

        Returns:
            CompositeVideoClip with image, audio, and subtitles

        Raises:
            FileNotFoundError: If required files don't exist
            RuntimeError: If clip creation fails
        """
        if not os.path.exists(scene.image_path):
            raise FileNotFoundError(f"Image not found: {scene.image_path}")
        if not os.path.exists(scene.audio_path):
            raise FileNotFoundError(f"Audio not found: {scene.audio_path}")

        try:
            # Create image clip
            image_clip = ImageClip(scene.image_path)
            image_clip = image_clip.with_duration(scene.duration)
            image_clip = image_clip.resized((self.width, self.height))

            # Load audio
            audio_clip = AudioFileClip(scene.audio_path)

            # Set audio to image clip
            image_clip = image_clip.with_audio(audio_clip)

            # Add subtitles if enabled and available
            if self.subtitle_enabled and scene.subtitle_path and os.path.exists(scene.subtitle_path):
                subtitle_clips = self._create_subtitle_clips(scene.subtitle_path, scene.duration)

                if subtitle_clips:
                    # Composite image with subtitles
                    composite_clip = CompositeVideoClip([image_clip] + subtitle_clips)
                    composite_clip = composite_clip.with_duration(scene.duration)
                    composite_clip = composite_clip.with_audio(audio_clip)
                    return composite_clip

            return image_clip

        except Exception as e:
            raise RuntimeError(f"Failed to create scene clip: {e}")

    def _create_subtitle_clips(self, subtitle_path: str, duration: float) -> List[TextClip]:
        """
        Create text clips from SRT subtitle file

        Args:
            subtitle_path: Path to SRT subtitle file
            duration: Duration of the scene in seconds

        Returns:
            List of TextClip objects with proper timing and positioning

        Raises:
            RuntimeError: If subtitle processing fails
        """
        try:
            # Load SRT file
            subs = pysrt.open(subtitle_path, encoding='utf-8')

            subtitle_clips = []

            for sub in subs:
                # Convert SubRipTime to seconds
                start_time = (
                    sub.start.hours * 3600 +
                    sub.start.minutes * 60 +
                    sub.start.seconds +
                    sub.start.milliseconds / 1000.0
                )
                end_time = (
                    sub.end.hours * 3600 +
                    sub.end.minutes * 60 +
                    sub.end.seconds +
                    sub.end.milliseconds / 1000.0
                )

                # Create text clip
                txt_clip = TextClip(
                    text=sub.text,
                    font_size=self.subtitle_font_size,
                    color=self.subtitle_color,
                    font=self.subtitle_font,
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(self.width - 100, None)  # Leave margin
                )

                # Position subtitle
                if self.subtitle_position == 'bottom':
                    txt_clip = txt_clip.with_position(('center', self.height - txt_clip.h - 50))
                elif self.subtitle_position == 'top':
                    txt_clip = txt_clip.with_position(('center', 50))
                elif self.subtitle_position == 'center':
                    txt_clip = txt_clip.with_position('center')
                else:
                    txt_clip = txt_clip.with_position(('center', self.height - txt_clip.h - 50))

                # Set timing
                txt_clip = txt_clip.with_start(start_time)
                txt_clip = txt_clip.with_duration(end_time - start_time)

                subtitle_clips.append(txt_clip)

            return subtitle_clips

        except Exception as e:
            raise RuntimeError(f"Failed to create subtitle clips: {e}")

    def get_video_info(self, video_path: str) -> dict:
        """
        Get information about a video file

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information

        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            clip = VideoFileClip(video_path)

            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': (clip.w, clip.h),
                'width': clip.w,
                'height': clip.h,
                'file_size': os.path.getsize(video_path)
            }

            clip.close()

            return info

        except Exception as e:
            raise RuntimeError(f"Failed to get video info: {e}")

    def create_simple_video(
        self,
        image_path: str,
        audio_path: str,
        output_path: str,
        duration: Optional[float] = None
    ) -> str:
        """
        Create a simple video from single image and audio

        Args:
            image_path: Path to image file
            audio_path: Path to audio file
            output_path: Path where to save the video
            duration: Optional duration override (uses audio duration if None)

        Returns:
            Path to created video file

        Raises:
            FileNotFoundError: If image or audio file doesn't exist
            RuntimeError: If video creation fails
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        try:
            # Load audio to get duration
            audio_clip = AudioFileClip(audio_path)

            if duration is None:
                duration = audio_clip.duration
            else:
                # If custom duration specified, trim audio to match
                if audio_clip.duration > duration:
                    audio_clip = audio_clip.subclipped(0, duration)

            # Create image clip
            image_clip = ImageClip(image_path)
            image_clip = image_clip.with_duration(duration)
            image_clip = image_clip.resized((self.width, self.height))
            image_clip = image_clip.with_audio(audio_clip)

            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Write video
            image_clip.write_videofile(
                output_path,
                fps=self.fps,
                codec=self.codec,
                bitrate=self.bitrate,
                audio_codec='aac',
                preset='medium',
                threads=4
            )

            # Clean up
            image_clip.close()
            audio_clip.close()

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to create simple video: {e}")
