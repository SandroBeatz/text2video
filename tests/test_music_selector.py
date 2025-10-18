"""
Tests for Music Selector Module
"""

import pytest
import os
from pathlib import Path
from pydub import AudioSegment
from pydub.generators import Sine
from modules.music_selector import MusicSelector


@pytest.fixture
def create_test_audio(tmp_path):
    """Create test audio files with different durations"""
    audio_dir = tmp_path / "test_audio"
    audio_dir.mkdir()

    # Create a 5-second test tone (440 Hz - A4 note)
    tone_5s = Sine(440).to_audio_segment(duration=5000)
    music_5s_path = audio_dir / "music_5s.mp3"
    tone_5s.export(str(music_5s_path), format='mp3')

    # Create a 2-second test tone
    tone_2s = Sine(440).to_audio_segment(duration=2000)
    music_2s_path = audio_dir / "music_2s.mp3"
    tone_2s.export(str(music_2s_path), format='mp3')

    # Create a 10-second test tone
    tone_10s = Sine(440).to_audio_segment(duration=10000)
    music_10s_path = audio_dir / "music_10s.mp3"
    tone_10s.export(str(music_10s_path), format='mp3')

    # Create WAV file
    tone_wav = Sine(440).to_audio_segment(duration=3000)
    wav_path = audio_dir / "music.wav"
    tone_wav.export(str(wav_path), format='wav')

    # Create voice file (3 seconds)
    voice_tone = Sine(220).to_audio_segment(duration=3000)
    voice_path = audio_dir / "voice.mp3"
    voice_tone.export(str(voice_path), format='mp3')

    return {
        'dir': str(audio_dir),
        'music_5s': str(music_5s_path),
        'music_2s': str(music_2s_path),
        'music_10s': str(music_10s_path),
        'wav': str(wav_path),
        'voice': str(voice_path)
    }


class TestMusicSelector:
    """Tests for MusicSelector class"""

    def test_selector_initialization(self):
        """Test creating a MusicSelector"""
        config = {
            'audio': {
                'music': {
                    'enabled': True,
                    'volume': 0.3,
                    'fade_in': 1.5,
                    'fade_out': 2.5
                }
            },
            'paths': {
                'music_dir': './assets/music'
            }
        }
        selector = MusicSelector(config)
        assert selector is not None
        assert selector.enabled is True
        assert selector.music_volume == 0.3
        assert selector.fade_in_duration == 1.5
        assert selector.fade_out_duration == 2.5
        assert selector.music_dir == './assets/music'

    def test_selector_default_settings(self):
        """Test default settings when config is minimal"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)
        assert selector.enabled is True
        assert selector.music_volume == 0.2
        assert selector.fade_in_duration == 2.0
        assert selector.fade_out_duration == 3.0
        assert selector.music_dir == './assets/music'

    def test_get_music_files(self, create_test_audio):
        """Test getting list of music files"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        music_files = selector._get_music_files(create_test_audio['dir'])

        # Should find 5 audio files (4 mp3 + 1 wav)
        assert len(music_files) == 5
        # Should be sorted
        assert all('.mp3' in f or '.wav' in f for f in music_files)

    def test_get_music_files_empty_directory(self, tmp_path):
        """Test getting music files from empty directory"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        music_files = selector._get_music_files(str(empty_dir))
        assert len(music_files) == 0

    def test_select_music_random(self, create_test_audio):
        """Test selecting a random music file"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        music_path = selector.select_music(create_test_audio['dir'])

        assert os.path.exists(music_path)
        assert music_path in [
            create_test_audio['music_5s'],
            create_test_audio['music_2s'],
            create_test_audio['music_10s'],
            create_test_audio['wav']
        ]

    def test_select_music_no_directory(self):
        """Test selecting music when directory doesn't exist"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="Music directory not found"):
            selector.select_music("/nonexistent/directory")

    def test_select_music_empty_directory(self, tmp_path):
        """Test selecting music from empty directory"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="No music files found"):
            selector.select_music(str(empty_dir))

    def test_adjust_duration_trim(self, create_test_audio, tmp_path):
        """Test trimming music to shorter duration"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "adjusted"
        adjusted_path = selector.adjust_duration(
            create_test_audio['music_5s'],
            target_duration=3.0,
            output_dir=str(output_dir)
        )

        assert os.path.exists(adjusted_path)

        # Check adjusted duration
        audio = AudioSegment.from_file(adjusted_path)
        duration_sec = len(audio) / 1000.0
        assert duration_sec == pytest.approx(3.0, abs=0.1)

    def test_adjust_duration_loop(self, create_test_audio, tmp_path):
        """Test looping music to longer duration"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "adjusted"
        adjusted_path = selector.adjust_duration(
            create_test_audio['music_2s'],
            target_duration=7.0,
            output_dir=str(output_dir)
        )

        assert os.path.exists(adjusted_path)

        # Check adjusted duration
        audio = AudioSegment.from_file(adjusted_path)
        duration_sec = len(audio) / 1000.0
        assert duration_sec == pytest.approx(7.0, abs=0.1)

    def test_adjust_duration_exact_match(self, create_test_audio, tmp_path):
        """Test when music duration exactly matches target"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "adjusted"
        adjusted_path = selector.adjust_duration(
            create_test_audio['music_5s'],
            target_duration=5.0,
            output_dir=str(output_dir)
        )

        assert os.path.exists(adjusted_path)

        audio = AudioSegment.from_file(adjusted_path)
        duration_sec = len(audio) / 1000.0
        assert duration_sec == pytest.approx(5.0, abs=0.1)

    def test_adjust_duration_nonexistent_file(self):
        """Test adjusting duration of nonexistent file"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="Music file not found"):
            selector.adjust_duration("/nonexistent/music.mp3", 5.0)

    def test_adjust_duration_creates_output_directory(self, create_test_audio, tmp_path):
        """Test that adjust_duration creates output directory if it doesn't exist"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "nonexistent" / "adjusted"

        # Directory doesn't exist yet
        assert not output_dir.exists()

        adjusted_path = selector.adjust_duration(
            create_test_audio['music_5s'],
            target_duration=3.0,
            output_dir=str(output_dir)
        )

        # Directory should be created
        assert output_dir.exists()
        assert os.path.exists(adjusted_path)

    def test_adjust_duration_filename_format(self, create_test_audio, tmp_path):
        """Test that adjusted file has correct filename format"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "adjusted"
        adjusted_path = selector.adjust_duration(
            create_test_audio['music_5s'],
            target_duration=3.0,
            output_dir=str(output_dir)
        )

        # Should contain duration in filename
        assert "music_5s_adjusted_3s.mp3" in adjusted_path

    def test_apply_fade(self, create_test_audio, tmp_path):
        """Test applying fade in/out effects"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "faded"
        faded_path = selector.apply_fade(
            create_test_audio['music_5s'],
            fade_in=1.0,
            fade_out=1.5,
            output_dir=str(output_dir)
        )

        assert os.path.exists(faded_path)
        # File should have same duration
        audio = AudioSegment.from_file(faded_path)
        duration_sec = len(audio) / 1000.0
        assert duration_sec == pytest.approx(5.0, abs=0.1)

    def test_apply_fade_default_settings(self, create_test_audio, tmp_path):
        """Test applying fade with default config settings"""
        config = {
            'audio': {
                'music': {
                    'fade_in': 1.5,
                    'fade_out': 2.0
                }
            },
            'paths': {}
        }
        selector = MusicSelector(config)

        output_dir = tmp_path / "faded"
        faded_path = selector.apply_fade(
            create_test_audio['music_5s'],
            output_dir=str(output_dir)
        )

        assert os.path.exists(faded_path)

    def test_apply_fade_nonexistent_file(self):
        """Test applying fade to nonexistent file"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="Music file not found"):
            selector.apply_fade("/nonexistent/music.mp3")

    def test_adjust_volume(self, create_test_audio, tmp_path):
        """Test adjusting music volume"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "volume"
        adjusted_path = selector.adjust_volume(
            create_test_audio['music_5s'],
            volume_level=0.5,
            output_dir=str(output_dir)
        )

        assert os.path.exists(adjusted_path)
        # File should have same duration
        audio = AudioSegment.from_file(adjusted_path)
        duration_sec = len(audio) / 1000.0
        assert duration_sec == pytest.approx(5.0, abs=0.1)

    def test_adjust_volume_default_config(self, create_test_audio, tmp_path):
        """Test volume adjustment with default config volume"""
        config = {
            'audio': {
                'music': {
                    'volume': 0.3
                }
            },
            'paths': {}
        }
        selector = MusicSelector(config)

        output_dir = tmp_path / "volume"
        adjusted_path = selector.adjust_volume(
            create_test_audio['music_5s'],
            output_dir=str(output_dir)
        )

        assert os.path.exists(adjusted_path)
        assert "vol_30.mp3" in adjusted_path

    def test_adjust_volume_invalid_level(self, create_test_audio):
        """Test volume adjustment with invalid level"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(ValueError, match="Volume level must be between"):
            selector.adjust_volume(create_test_audio['music_5s'], volume_level=1.5)

        with pytest.raises(ValueError, match="Volume level must be between"):
            selector.adjust_volume(create_test_audio['music_5s'], volume_level=-0.1)

    def test_adjust_volume_zero(self, create_test_audio, tmp_path):
        """Test volume adjustment with zero volume (silence)"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "volume"
        adjusted_path = selector.adjust_volume(
            create_test_audio['music_5s'],
            volume_level=0.0,
            output_dir=str(output_dir)
        )

        assert os.path.exists(adjusted_path)

    def test_adjust_volume_nonexistent_file(self):
        """Test adjusting volume of nonexistent file"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="Music file not found"):
            selector.adjust_volume("/nonexistent/music.mp3", 0.5)

    def test_mix_with_voice(self, create_test_audio, tmp_path):
        """Test mixing music with voice"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "mixed"
        mixed_path = selector.mix_with_voice(
            create_test_audio['voice'],
            create_test_audio['music_5s'],
            output_dir=str(output_dir),
            music_volume=0.2
        )

        assert os.path.exists(mixed_path)

        # Mixed audio should have same duration as voice
        mixed = AudioSegment.from_file(mixed_path)
        mixed_duration = len(mixed) / 1000.0

        voice = AudioSegment.from_file(create_test_audio['voice'])
        voice_duration = len(voice) / 1000.0

        assert mixed_duration == pytest.approx(voice_duration, abs=0.2)

    def test_mix_with_voice_longer_music(self, create_test_audio, tmp_path):
        """Test mixing when music is longer than voice (should trim)"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "mixed"
        mixed_path = selector.mix_with_voice(
            create_test_audio['voice'],
            create_test_audio['music_10s'],
            output_dir=str(output_dir)
        )

        assert os.path.exists(mixed_path)

        # Duration should match voice
        mixed = AudioSegment.from_file(mixed_path)
        mixed_duration = len(mixed) / 1000.0
        assert mixed_duration == pytest.approx(3.0, abs=0.2)

    def test_mix_with_voice_shorter_music(self, create_test_audio, tmp_path):
        """Test mixing when music is shorter than voice (should loop)"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        output_dir = tmp_path / "mixed"
        mixed_path = selector.mix_with_voice(
            create_test_audio['voice'],
            create_test_audio['music_2s'],
            output_dir=str(output_dir)
        )

        assert os.path.exists(mixed_path)

        # Duration should match voice
        mixed = AudioSegment.from_file(mixed_path)
        mixed_duration = len(mixed) / 1000.0
        assert mixed_duration == pytest.approx(3.0, abs=0.2)

    def test_mix_with_voice_default_volume(self, create_test_audio, tmp_path):
        """Test mixing with default config volume"""
        config = {
            'audio': {
                'music': {
                    'volume': 0.15,
                    'fade_in': 1.0,
                    'fade_out': 1.0
                }
            },
            'paths': {}
        }
        selector = MusicSelector(config)

        output_dir = tmp_path / "mixed"
        mixed_path = selector.mix_with_voice(
            create_test_audio['voice'],
            create_test_audio['music_5s'],
            output_dir=str(output_dir)
        )

        assert os.path.exists(mixed_path)

    def test_mix_with_voice_nonexistent_voice(self, create_test_audio):
        """Test mixing with nonexistent voice file"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="Voice file not found"):
            selector.mix_with_voice(
                "/nonexistent/voice.mp3",
                create_test_audio['music_5s']
            )

    def test_mix_with_voice_nonexistent_music(self, create_test_audio):
        """Test mixing with nonexistent music file"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="Music file not found"):
            selector.mix_with_voice(
                create_test_audio['voice'],
                "/nonexistent/music.mp3"
            )

    def test_get_audio_info(self, create_test_audio):
        """Test getting audio file information"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        info = selector.get_audio_info(create_test_audio['music_5s'])

        assert info['duration'] == pytest.approx(5.0, abs=0.1)
        assert info['channels'] in [1, 2]  # Mono or stereo
        assert info['sample_width'] > 0
        assert info['frame_rate'] > 0
        assert info['size'] > 0

    def test_get_audio_info_wav_format(self, create_test_audio):
        """Test getting info for WAV format"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        info = selector.get_audio_info(create_test_audio['wav'])

        assert info['duration'] == pytest.approx(3.0, abs=0.1)
        assert 'channels' in info
        assert 'frame_rate' in info

    def test_get_audio_info_nonexistent(self):
        """Test getting info for nonexistent audio file"""
        config = {'audio': {}, 'paths': {}}
        selector = MusicSelector(config)

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            selector.get_audio_info("/nonexistent/audio.mp3")

    def test_mix_includes_fade_effects(self, create_test_audio, tmp_path):
        """Test that mixing applies fade in/out to music"""
        config = {
            'audio': {
                'music': {
                    'fade_in': 0.5,
                    'fade_out': 0.5
                }
            },
            'paths': {}
        }
        selector = MusicSelector(config)

        output_dir = tmp_path / "mixed"
        mixed_path = selector.mix_with_voice(
            create_test_audio['voice'],
            create_test_audio['music_5s'],
            output_dir=str(output_dir)
        )

        # Should complete successfully with fade effects applied
        assert os.path.exists(mixed_path)
