"""
Tests for Video Assembler Module
"""

import pytest
import os
from pathlib import Path
from PIL import Image
from pydub import AudioSegment
from pydub.generators import Sine
import pysrt
from modules.scene_parser import Scene
from modules.video_assembler import VideoAssembler


@pytest.fixture
def create_test_resources(tmp_path):
    """Create test images, audio, and subtitles"""
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()

    # Create test image
    img = Image.new('RGB', (1920, 1080), color='blue')
    image_path = resources_dir / "test_image.jpg"
    img.save(image_path)

    # Create another test image
    img2 = Image.new('RGB', (1920, 1080), color='red')
    image_path2 = resources_dir / "test_image2.jpg"
    img2.save(image_path2)

    # Create test audio (3 seconds, 440 Hz tone)
    tone = Sine(440).to_audio_segment(duration=3000)
    audio_path = resources_dir / "test_audio.mp3"
    tone.export(str(audio_path), format='mp3')

    # Create another test audio (2 seconds)
    tone2 = Sine(440).to_audio_segment(duration=2000)
    audio_path2 = resources_dir / "test_audio2.mp3"
    tone2.export(str(audio_path2), format='mp3')

    # Create background music (5 seconds)
    music_tone = Sine(220).to_audio_segment(duration=5000)
    music_path = resources_dir / "background_music.mp3"
    music_tone.export(str(music_path), format='mp3')

    # Create test subtitle file
    subs = pysrt.SubRipFile()
    subs.append(pysrt.SubRipItem(
        index=1,
        start=pysrt.SubRipTime(seconds=0),
        end=pysrt.SubRipTime(seconds=1, milliseconds=500),
        text="First subtitle line"
    ))
    subs.append(pysrt.SubRipItem(
        index=2,
        start=pysrt.SubRipTime(seconds=1, milliseconds=500),
        end=pysrt.SubRipTime(seconds=3),
        text="Second subtitle line"
    ))

    subtitle_path = resources_dir / "test_subtitles.srt"
    subs.save(str(subtitle_path), encoding='utf-8')

    # Create another subtitle file
    subs2 = pysrt.SubRipFile()
    subs2.append(pysrt.SubRipItem(
        index=1,
        start=pysrt.SubRipTime(seconds=0),
        end=pysrt.SubRipTime(seconds=2),
        text="Scene two subtitle"
    ))

    subtitle_path2 = resources_dir / "test_subtitles2.srt"
    subs2.save(str(subtitle_path2), encoding='utf-8')

    return {
        'dir': str(resources_dir),
        'image': str(image_path),
        'image2': str(image_path2),
        'audio': str(audio_path),
        'audio2': str(audio_path2),
        'music': str(music_path),
        'subtitle': str(subtitle_path),
        'subtitle2': str(subtitle_path2)
    }


class TestVideoAssembler:
    """Tests for VideoAssembler class"""

    def test_assembler_initialization(self):
        """Test creating a VideoAssembler"""
        config = {
            'video': {
                'fps': 30,
                'resolution': {'width': 1920, 'height': 1080},
                'codec': 'libx264',
                'bitrate': '5000k'
            },
            'subtitles': {
                'enabled': True,
                'font': 'Arial',
                'font_size': 48,
                'color': 'white',
                'position': 'bottom'
            },
            'project': {
                'output_dir': './output'
            }
        }
        assembler = VideoAssembler(config)
        assert assembler is not None
        assert assembler.fps == 30
        assert assembler.width == 1920
        assert assembler.height == 1080
        assert assembler.codec == 'libx264'
        assert assembler.subtitle_enabled is True

    def test_assembler_default_settings(self):
        """Test default settings when config is minimal"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)
        assert assembler.fps == 30
        assert assembler.width == 1920
        assert assembler.height == 1080
        assert assembler.subtitle_enabled is True

    def test_create_simple_video(self, create_test_resources, tmp_path):
        """Test creating a simple video from image and audio"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        output_path = tmp_path / "output" / "test_video.mp4"

        video_path = assembler.create_simple_video(
            create_test_resources['image'],
            create_test_resources['audio'],
            str(output_path)
        )

        # Check that video was created
        assert os.path.exists(video_path)
        assert os.path.getsize(video_path) > 0
        assert video_path.endswith('.mp4')

    def test_create_simple_video_with_custom_duration(self, create_test_resources, tmp_path):
        """Test creating video with custom duration"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        output_path = tmp_path / "output" / "test_video_custom.mp4"

        video_path = assembler.create_simple_video(
            create_test_resources['image'],
            create_test_resources['audio'],
            str(output_path),
            duration=2.0
        )

        assert os.path.exists(video_path)

        # Check video duration
        info = assembler.get_video_info(video_path)
        assert info['duration'] == pytest.approx(2.0, abs=0.5)

    def test_create_simple_video_nonexistent_image(self, create_test_resources):
        """Test creating video with nonexistent image"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        with pytest.raises(FileNotFoundError, match="Image not found"):
            assembler.create_simple_video(
                "/nonexistent/image.jpg",
                create_test_resources['audio'],
                "output.mp4"
            )

    def test_create_simple_video_nonexistent_audio(self, create_test_resources):
        """Test creating video with nonexistent audio"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        with pytest.raises(FileNotFoundError, match="Audio not found"):
            assembler.create_simple_video(
                create_test_resources['image'],
                "/nonexistent/audio.mp3",
                "output.mp4"
            )

    def test_create_scene_clip(self, create_test_resources):
        """Test creating a clip for a single scene"""
        config = {'video': {}, 'subtitles': {'enabled': False}, 'project': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Test scene",
            duration=3.0,
            audio_path=create_test_resources['audio'],
            image_path=create_test_resources['image']
        )

        clip = assembler.create_scene_clip(scene)

        assert clip is not None
        assert clip.duration == pytest.approx(3.0, abs=0.1)
        assert clip.w == 1920
        assert clip.h == 1080

        clip.close()

    def test_create_scene_clip_with_subtitles(self, create_test_resources):
        """Test creating a clip with subtitles"""
        config = {'video': {}, 'subtitles': {'enabled': True}, 'project': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Test scene with subtitles",
            duration=3.0,
            audio_path=create_test_resources['audio'],
            image_path=create_test_resources['image'],
            subtitle_path=create_test_resources['subtitle']
        )

        clip = assembler.create_scene_clip(scene)

        assert clip is not None
        assert clip.duration == pytest.approx(3.0, abs=0.1)

        clip.close()

    def test_create_scene_clip_missing_image(self, create_test_resources):
        """Test creating scene clip with missing image"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Test",
            duration=3.0,
            audio_path=create_test_resources['audio'],
            image_path="/nonexistent/image.jpg"
        )

        with pytest.raises(FileNotFoundError, match="Image not found"):
            assembler.create_scene_clip(scene)

    def test_create_scene_clip_missing_audio(self, create_test_resources):
        """Test creating scene clip with missing audio"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Test",
            duration=3.0,
            audio_path="/nonexistent/audio.mp3",
            image_path=create_test_resources['image']
        )

        with pytest.raises(FileNotFoundError, match="Audio not found"):
            assembler.create_scene_clip(scene)

    def test_assemble_single_scene(self, create_test_resources, tmp_path):
        """Test assembling video from single scene"""
        config = {'video': {}, 'subtitles': {'enabled': False}, 'project': {}, 'audio': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Single scene",
            duration=3.0,
            audio_path=create_test_resources['audio'],
            image_path=create_test_resources['image']
        )

        output_path = tmp_path / "output" / "assembled_single.mp4"

        video_path = assembler.assemble([scene], str(output_path))

        # Check that video was created
        assert os.path.exists(video_path)
        assert os.path.getsize(video_path) > 0

        # Check video properties
        info = assembler.get_video_info(video_path)
        assert info['duration'] == pytest.approx(3.0, abs=0.5)
        assert info['width'] == 1920
        assert info['height'] == 1080

    def test_assemble_multiple_scenes(self, create_test_resources, tmp_path):
        """Test assembling video from multiple scenes"""
        config = {'video': {}, 'subtitles': {'enabled': False}, 'project': {}, 'audio': {}}
        assembler = VideoAssembler(config)

        scenes = [
            Scene(
                id=1,
                text="First scene",
                duration=3.0,
                audio_path=create_test_resources['audio'],
                image_path=create_test_resources['image']
            ),
            Scene(
                id=2,
                text="Second scene",
                duration=2.0,
                audio_path=create_test_resources['audio2'],
                image_path=create_test_resources['image2']
            )
        ]

        output_path = tmp_path / "output" / "assembled_multiple.mp4"

        video_path = assembler.assemble(scenes, str(output_path))

        assert os.path.exists(video_path)

        # Check total duration (3s + 2s = 5s)
        info = assembler.get_video_info(video_path)
        assert info['duration'] == pytest.approx(5.0, abs=0.5)

    def test_assemble_with_background_music(self, create_test_resources, tmp_path):
        """Test assembling video with background music"""
        config = {
            'video': {},
            'subtitles': {'enabled': False},
            'project': {},
            'audio': {'music': {'volume': 0.2}}
        }
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Scene with music",
            duration=3.0,
            audio_path=create_test_resources['audio'],
            image_path=create_test_resources['image']
        )

        output_path = tmp_path / "output" / "assembled_with_music.mp4"

        video_path = assembler.assemble(
            [scene],
            str(output_path),
            background_music_path=create_test_resources['music']
        )

        assert os.path.exists(video_path)
        assert os.path.getsize(video_path) > 0

    def test_assemble_empty_scenes_list(self):
        """Test that assembling with empty scenes raises error"""
        config = {'video': {}, 'subtitles': {}, 'project': {}, 'audio': {}}
        assembler = VideoAssembler(config)

        with pytest.raises(ValueError, match="scenes list is empty"):
            assembler.assemble([], "output.mp4")

    def test_assemble_scene_without_image(self, create_test_resources):
        """Test that assembling scene without image raises error"""
        config = {'video': {}, 'subtitles': {}, 'project': {}, 'audio': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Scene without image",
            duration=3.0,
            audio_path=create_test_resources['audio']
        )

        with pytest.raises(ValueError, match="has no valid image_path"):
            assembler.assemble([scene], "output.mp4")

    def test_assemble_scene_without_audio(self, create_test_resources):
        """Test that assembling scene without audio raises error"""
        config = {'video': {}, 'subtitles': {}, 'project': {}, 'audio': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Scene without audio",
            duration=3.0,
            image_path=create_test_resources['image']
        )

        with pytest.raises(ValueError, match="has no valid audio_path"):
            assembler.assemble([scene], "output.mp4")

    def test_assemble_scene_with_zero_duration(self, create_test_resources):
        """Test that assembling scene with zero duration raises error"""
        config = {'video': {}, 'subtitles': {}, 'project': {}, 'audio': {}}
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Scene with zero duration",
            duration=0.0,
            audio_path=create_test_resources['audio'],
            image_path=create_test_resources['image']
        )

        with pytest.raises(ValueError, match="has invalid duration"):
            assembler.assemble([scene], "output.mp4")

    def test_get_video_info(self, create_test_resources, tmp_path):
        """Test getting video information"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        # First create a video
        output_path = tmp_path / "test_info.mp4"
        video_path = assembler.create_simple_video(
            create_test_resources['image'],
            create_test_resources['audio'],
            str(output_path)
        )

        # Get info
        info = assembler.get_video_info(video_path)

        assert 'duration' in info
        assert 'fps' in info
        assert 'width' in info
        assert 'height' in info
        assert 'file_size' in info
        assert info['width'] == 1920
        assert info['height'] == 1080

    def test_get_video_info_nonexistent(self):
        """Test getting info for nonexistent video"""
        config = {'video': {}, 'subtitles': {}, 'project': {}}
        assembler = VideoAssembler(config)

        with pytest.raises(FileNotFoundError, match="Video file not found"):
            assembler.get_video_info("/nonexistent/video.mp4")

    def test_assemble_with_subtitles(self, create_test_resources, tmp_path):
        """Test assembling video with subtitles enabled"""
        config = {
            'video': {},
            'subtitles': {
                'enabled': True,
                'font': 'Arial',
                'font_size': 48,
                'color': 'white',
                'position': 'bottom'
            },
            'project': {},
            'audio': {}
        }
        assembler = VideoAssembler(config)

        scene = Scene(
            id=1,
            text="Scene with subtitles",
            duration=3.0,
            audio_path=create_test_resources['audio'],
            image_path=create_test_resources['image'],
            subtitle_path=create_test_resources['subtitle']
        )

        output_path = tmp_path / "output" / "assembled_with_subs.mp4"

        video_path = assembler.assemble([scene], str(output_path))

        assert os.path.exists(video_path)
        assert os.path.getsize(video_path) > 0

    def test_create_subtitle_clips(self, create_test_resources):
        """Test creating subtitle clips from SRT file"""
        config = {
            'video': {'resolution': {'width': 1920, 'height': 1080}},
            'subtitles': {
                'enabled': True,
                'font': 'Arial',
                'font_size': 48,
                'color': 'white',
                'position': 'bottom'
            },
            'project': {}
        }
        assembler = VideoAssembler(config)

        subtitle_clips = assembler._create_subtitle_clips(
            create_test_resources['subtitle'],
            duration=3.0
        )

        # Should have 2 subtitle clips
        assert len(subtitle_clips) == 2

        # Clean up
        for clip in subtitle_clips:
            clip.close()

    def test_different_video_resolutions(self, create_test_resources, tmp_path):
        """Test creating videos with different resolutions"""
        # Test 9:16 vertical video
        config_vertical = {
            'video': {'resolution': {'width': 1080, 'height': 1920}},
            'subtitles': {'enabled': False},
            'project': {}
        }
        assembler_vertical = VideoAssembler(config_vertical)

        output_vertical = tmp_path / "vertical.mp4"
        video_vertical = assembler_vertical.create_simple_video(
            create_test_resources['image'],
            create_test_resources['audio'],
            str(output_vertical)
        )

        info = assembler_vertical.get_video_info(video_vertical)
        assert info['width'] == 1080
        assert info['height'] == 1920

        # Test 1:1 square video
        config_square = {
            'video': {'resolution': {'width': 1080, 'height': 1080}},
            'subtitles': {'enabled': False},
            'project': {}
        }
        assembler_square = VideoAssembler(config_square)

        output_square = tmp_path / "square.mp4"
        video_square = assembler_square.create_simple_video(
            create_test_resources['image'],
            create_test_resources['audio'],
            str(output_square)
        )

        info = assembler_square.get_video_info(video_square)
        assert info['width'] == 1080
        assert info['height'] == 1080
