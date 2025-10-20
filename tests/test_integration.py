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
from modules.subtitle_generator import SubtitleGenerator
from modules.visual_selector import VisualSelector
from modules.music_selector import MusicSelector
from modules.video_assembler import VideoAssembler


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

    def test_full_pipeline_with_tts(self, config, test_script_path, tmp_path):
        """
        Test full pipeline: parse text -> generate audio -> verify results
        (uses Edge TTS - requires internet connection)
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

            # Check filename format (MP3 for Edge TTS)
            assert f"scene_{scene.id:03d}_audio.mp3" in scene.audio_path

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

    def test_russian_text_with_tts(self, config, tmp_path):
        """
        Test Russian text parsing and audio generation
        (uses Edge TTS - requires internet connection)
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

        # Generate audio (will use Edge TTS with ru-RU voice)
        output_dir = tmp_path / "russian_audio"
        output_dir.mkdir()

        tts_generator = TTSGenerator(config)
        tts_generator.batch_generate(scenes, str(output_dir))

        # Verify
        for scene in scenes:
            assert scene.audio_path is not None
            assert os.path.exists(scene.audio_path)
            assert scene.duration > 0


class TestFullPipelineIntegration:
    """Integration tests for the complete pipeline (all 7 steps)"""

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
            "First test scene.\n"
            "This is a simple test.\n\n"
            "Second test scene.\n"
            "It has multiple lines too.",
            encoding='utf-8'
        )
        return str(script_path)

    @pytest.fixture
    def test_images_dir(self, tmp_path):
        """Create test images"""
        from PIL import Image

        images_dir = tmp_path / "test_images"
        images_dir.mkdir()

        # Create 3 test images
        for i in range(1, 4):
            img = Image.new('RGB', (1920, 1080), color=(100*i, 100*i, 100*i))
            img.save(images_dir / f"test_image_{i}.jpg")

        return str(images_dir)

    @pytest.fixture
    def test_music_dir(self, tmp_path):
        """Create test music files"""
        from pydub import AudioSegment
        from pydub.generators import Sine

        music_dir = tmp_path / "test_music"
        music_dir.mkdir()

        # Create a test music file (5 seconds)
        tone = Sine(440).to_audio_segment(duration=5000)
        tone.export(music_dir / "test_music.mp3", format="mp3")

        return str(music_dir)

    def test_pipeline_step_by_step_without_tts(self, config, test_script_path,
                                                 test_images_dir, tmp_path):
        """
        Test pipeline steps without TTS (using mock audio)
        Tests: Parse -> Subtitles -> Visuals -> (skip Music) -> (skip Assembly)
        """
        # Step 1: Parse
        parser = SceneParser()
        scenes = parser.parse(test_script_path)
        assert len(scenes) == 2

        # Mock audio data (simulate TTS output)
        for i, scene in enumerate(scenes):
            # Create mock audio file
            from pydub import AudioSegment
            from pydub.generators import Sine

            audio_dir = tmp_path / "audio"
            audio_dir.mkdir(exist_ok=True)

            # Create 3 second audio
            audio = Sine(440).to_audio_segment(duration=3000)
            audio_path = audio_dir / f"scene_{scene.id:03d}_audio.wav"
            audio.export(audio_path, format="wav")

            scene.audio_path = str(audio_path)
            scene.duration = 3.0

        # Step 3: Generate subtitles
        subtitle_generator = SubtitleGenerator(config)
        subtitle_dir = tmp_path / "subtitles"
        subtitle_dir.mkdir()

        subtitle_generator.batch_generate(scenes, str(subtitle_dir))

        for scene in scenes:
            assert scene.subtitle_path is not None
            assert os.path.exists(scene.subtitle_path)
            assert scene.subtitle_path.endswith('.srt')

        # Step 4: Select and scale images
        visual_selector = VisualSelector(config)
        images_output_dir = tmp_path / "images"
        images_output_dir.mkdir()

        visual_selector.batch_process(scenes, test_images_dir, str(images_output_dir))

        for scene in scenes:
            assert scene.image_path is not None
            assert os.path.exists(scene.image_path)

    @pytest.mark.skip(reason="Skip full pipeline test with TTS - requires internet")
    def test_full_pipeline_with_tts(self, config, test_script_path,
                                    test_images_dir, test_music_dir, tmp_path):
        """
        Test complete pipeline with TTS
        All 7 steps: Parse -> TTS -> Subtitles -> Visuals -> Music -> Assembly

        This test requires:
        - edge-tts library installed
        - Internet connection (for Edge TTS)
        - FFmpeg installed

        Note: Skipped by default to avoid internet dependency in tests
        """
        # Adjust config to use test resources
        config['visuals']['images_dir'] = test_images_dir
        config['paths']['music_dir'] = test_music_dir
        config['audio']['music']['enabled'] = True

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Step 1: Parse text
        parser = SceneParser()
        scenes = parser.parse(test_script_path)
        assert len(scenes) == 2

        # Step 2: Generate audio (TTS)
        tts_generator = TTSGenerator(config)
        audio_output_dir = tmp_path / "audio"
        audio_output_dir.mkdir()

        tts_generator.batch_generate(scenes, str(audio_output_dir))

        total_duration = sum(scene.duration for scene in scenes)
        assert total_duration > 0

        # Step 3: Generate subtitles
        subtitle_generator = SubtitleGenerator(config)
        subtitle_output_dir = tmp_path / "subtitles"
        subtitle_output_dir.mkdir()

        subtitle_generator.batch_generate(scenes, str(subtitle_output_dir))

        # Step 4: Select and scale images
        visual_selector = VisualSelector(config)
        images_output_dir = tmp_path / "images"
        images_output_dir.mkdir()

        visual_selector.batch_process(scenes, test_images_dir, str(images_output_dir))

        # Step 5: Process music
        music_selector = MusicSelector(config)
        music_output_dir = tmp_path / "music"
        music_output_dir.mkdir()

        selected_music = music_selector.select_music(test_music_dir)
        music_path = music_selector.adjust_duration(
            selected_music,
            total_duration,
            str(music_output_dir)
        )

        # Step 6: Assemble video
        video_assembler = VideoAssembler(config)
        output_path = output_dir / "test_video.mp4"

        final_video = video_assembler.assemble(
            scenes=scenes,
            output_path=str(output_path),
            background_music_path=music_path
        )

        # Verify final video
        assert os.path.exists(final_video)
        assert os.path.getsize(final_video) > 0
        assert final_video.endswith('.mp4')

        # Verify video info
        video_info = video_assembler.get_video_info(final_video)
        assert video_info['duration'] > 0
        assert video_info['width'] == config['video']['resolution']['width']
        assert video_info['height'] == config['video']['resolution']['height']

    def test_pipeline_without_music(self, config, test_script_path,
                                    test_images_dir, tmp_path):
        """
        Test pipeline without background music
        Tests: Parse -> Mock Audio -> Subtitles -> Visuals -> Assembly (no music)
        """
        # Disable music in config
        config['audio']['music']['enabled'] = False
        config['visuals']['images_dir'] = test_images_dir

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Step 1: Parse
        parser = SceneParser()
        scenes = parser.parse(test_script_path)

        # Create mock audio
        from pydub import AudioSegment
        from pydub.generators import Sine

        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        for scene in scenes:
            audio = Sine(440).to_audio_segment(duration=3000)
            audio_path = audio_dir / f"scene_{scene.id:03d}_audio.wav"
            audio.export(audio_path, format="wav")
            scene.audio_path = str(audio_path)
            scene.duration = 3.0

        # Step 3: Subtitles
        subtitle_generator = SubtitleGenerator(config)
        subtitle_dir = tmp_path / "subtitles"
        subtitle_dir.mkdir()
        subtitle_generator.batch_generate(scenes, str(subtitle_dir))

        # Step 4: Visuals
        visual_selector = VisualSelector(config)
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        visual_selector.batch_process(scenes, test_images_dir, str(images_dir))

        # Step 6: Assemble (without music)
        video_assembler = VideoAssembler(config)
        output_path = output_dir / "test_video_no_music.mp4"

        final_video = video_assembler.assemble(
            scenes=scenes,
            output_path=str(output_path),
            background_music_path=None  # No music
        )

        # Verify
        assert os.path.exists(final_video)
        assert os.path.getsize(final_video) > 0
