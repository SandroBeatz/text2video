#!/usr/bin/env python3
"""
Text-to-Video Generator
Main entry point for the application with full CLI support
"""

import sys
import yaml
import argparse
from pathlib import Path
from tqdm import tqdm

# Import utilities
from utils.logger import setup_logger, log_system_info, log_config_info

# Import all modules
from modules.scene_parser import SceneParser
from modules.tts_generator import TTSGenerator
from modules.subtitle_generator import SubtitleGenerator
from modules.visual_selector import VisualSelector
from modules.music_selector import MusicSelector
from modules.video_assembler import VideoAssembler


def parse_arguments():
    """
    Parse command-line arguments

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Text-to-Video Generator - превращает текст в видео с озвучкой, субтитрами и музыкой',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  # Базовое использование
  python main.py -i script.txt

  # С указанием выходного файла
  python main.py -i script.txt -o my_video.mp4

  # С пользовательским config
  python main.py -i script.txt -c custom_config.yaml

  # Вертикальное видео без музыки
  python main.py -i script.txt --aspect-ratio 9:16 --no-music

  # На английском языке
  python main.py -i script_en.txt --language en

  # С выбором другого голоса
  python main.py -i script.txt --voice ru-RU-SvetlanaNeural

Дополнительная информация:
  - Редактируйте config.yaml для настройки параметров по умолчанию
  - Поддерживаемые форматы входных файлов: .txt, .md
  - Поддерживаемые языки: ru (русский), en (английский)
        '''
    )

    # Required arguments
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Путь к текстовому файлу (.txt или .md)'
    )

    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Путь к выходному видеофайлу (по умолчанию: output/video.mp4)'
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config.yaml',
        help='Путь к файлу конфигурации (по умолчанию: config.yaml)'
    )

    # Video settings
    parser.add_argument(
        '--aspect-ratio',
        type=str,
        choices=['16:9', '9:16', '1:1'],
        help='Соотношение сторон видео (переопределяет config.yaml)'
    )

    parser.add_argument(
        '--resolution',
        type=str,
        help='Разрешение видео в формате WIDTHxHEIGHT (например: 1920x1080)'
    )

    # Audio settings
    parser.add_argument(
        '--no-music',
        action='store_true',
        help='Создать видео без фоновой музыки'
    )

    parser.add_argument(
        '--no-subtitles',
        action='store_true',
        help='Создать видео без субтитров'
    )

    parser.add_argument(
        '--language',
        type=str,
        choices=['ru', 'en'],
        help='Язык озвучки (переопределяет config.yaml)'
    )

    parser.add_argument(
        '--voice',
        type=str,
        help='Имя голоса Edge TTS (например: ru-RU-DmitryNeural, en-US-JennyNeural). Используйте "edge-tts --list-voices" для просмотра всех доступных голосов'
    )

    parser.add_argument(
        '--image-mode',
        type=str,
        choices=['random', 'ordered'],
        help='Режим выбора изображений: random (случайный) или ordered (по порядку имен файлов)'
    )

    parser.add_argument(
        '--music-volume',
        type=float,
        help='Громкость фоновой музыки (0.0 - 1.0)'
    )

    # Logging settings
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Уровень логирования (по умолчанию: INFO)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Минимальный вывод (только ошибки)'
    )

    # Special modes
    parser.add_argument(
        '--version',
        action='version',
        version='Text2Video Generator v1.0.0'
    )

    args = parser.parse_args()

    # Validate: --input must be provided
    if not args.input:
        parser.error("аргумент -i/--input обязателен")

    return args


def load_config(config_path: str, logger) -> dict:
    """Load configuration from YAML file"""
    config_file = Path(config_path)

    if not config_file.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from: {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def apply_cli_overrides(config: dict, args, logger):
    """
    Apply command-line argument overrides to configuration

    Args:
        config: Configuration dictionary
        args: Parsed command-line arguments
        logger: Logger instance
    """
    # Aspect ratio
    if args.aspect_ratio:
        config['video']['aspect_ratio'] = args.aspect_ratio
        logger.info(f"Override: aspect_ratio = {args.aspect_ratio}")

        # Also update resolution based on aspect ratio
        aspect_ratios = {
            '16:9': {'width': 1920, 'height': 1080},
            '9:16': {'width': 1080, 'height': 1920},
            '1:1': {'width': 1080, 'height': 1080}
        }
        if args.aspect_ratio in aspect_ratios:
            config['video']['resolution'] = aspect_ratios[args.aspect_ratio]
            logger.info(f"Auto-adjusted resolution: {config['video']['resolution']}")

    # Manual resolution override
    if args.resolution:
        try:
            width, height = args.resolution.lower().split('x')
            config['video']['resolution']['width'] = int(width)
            config['video']['resolution']['height'] = int(height)
            logger.info(f"Override: resolution = {width}x{height}")
        except ValueError:
            logger.warning(f"Invalid resolution format: {args.resolution}, keeping default")

    # Music
    if args.no_music:
        config['audio']['music']['enabled'] = False
        logger.info("Override: music disabled")

    # Subtitles
    if args.no_subtitles:
        config['subtitles']['enabled'] = False
        logger.info("Override: subtitles disabled")

    # Language
    if args.language:
        config['tts']['language'] = args.language
        logger.info(f"Override: language = {args.language}")

    # Voice (Edge TTS)
    if args.voice:
        config['tts']['voice'] = args.voice
        logger.info(f"Override: voice = {args.voice}")

    # Image mode
    if args.image_mode:
        config['visuals']['selection_mode'] = args.image_mode
        logger.info(f"Override: image selection mode = {args.image_mode}")

    # Music volume
    if args.music_volume is not None:
        config['audio']['music']['volume'] = args.music_volume
        logger.info(f"Override: music volume = {args.music_volume}")


def validate_input(script_path: str, logger) -> Path:
    """Validate input script file"""
    script_file = Path(script_path)

    if not script_file.exists():
        logger.error(f"Input file not found: {script_path}")
        sys.exit(1)

    if script_file.suffix not in ['.txt', '.md']:
        logger.error(f"Unsupported file format: {script_file.suffix}. Use .txt or .md files")
        sys.exit(1)

    logger.info(f"Input file validated: {script_path}")
    return script_file


def ensure_directories(config: dict, logger):
    """Create necessary directories"""
    dirs = [
        config['project']['output_dir'],
        config['paths']['temp_dir'],
        Path(config['logging']['file']).parent,
        config['visuals']['images_dir'],
        config['paths']['music_dir'],
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    logger.debug("All necessary directories ensured")


def run_pipeline(script_path: str, output_path: str, config: dict, logger):
    """
    Main pipeline that processes text script into video

    Pipeline steps:
    1. Parse text into scenes
    2. Generate audio for each scene (TTS)
    3. Calculate durations
    4. Generate subtitles
    5. Select and scale images
    6. Select and process background music
    7. Assemble final video
    """

    logger.info("=" * 70)
    logger.info("TEXT-TO-VIDEO GENERATOR - FULL PIPELINE")
    logger.info("=" * 70)
    logger.info(f"Input:  {script_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Config: {config['project']['name']} v{config['project']['version']}")
    logger.info("=" * 70)

    print()
    print("=" * 70)
    print("TEXT-TO-VIDEO GENERATOR - PIPELINE EXECUTION")
    print("=" * 70)
    print()

    # Ensure all necessary directories exist
    ensure_directories(config, logger)

    # Get temporary directory
    temp_dir = Path(config['paths']['temp_dir'])

    # -------------------------------------------------------------------------
    # STEP 1: Parse text script into scenes
    # -------------------------------------------------------------------------
    print("📄 STEP 1/7: Parsing text script...")
    logger.info("STEP 1/7: Parsing text script")

    parser = SceneParser()
    scenes = parser.parse(script_path)

    logger.info(f"Parsed {len(scenes)} scenes from script")
    print(f"   ✓ Parsed {len(scenes)} scenes")

    if len(scenes) == 0:
        logger.error("No scenes found in the script")
        print("   ❌ Error: No scenes found in the script")
        return False

    for i, scene in enumerate(scenes, 1):
        preview = scene.text[:50] + "..." if len(scene.text) > 50 else scene.text
        logger.debug(f"Scene {i}: {preview}")

    print()

    # -------------------------------------------------------------------------
    # STEP 2: Generate audio for each scene (Text-to-Speech)
    # -------------------------------------------------------------------------
    print("🎤 STEP 2/7: Generating audio (TTS)...")
    logger.info("STEP 2/7: Generating audio with TTS")
    logger.info(f"Language: {config['tts']['language']}")
    logger.info(f"Voice: {config['tts']['voice']}")

    tts_generator = TTSGenerator(config)
    audio_output_dir = temp_dir / "audio"
    audio_output_dir.mkdir(exist_ok=True)

    # Use batch_generate with progress bar
    print(f"   Language: {config['tts']['language']}")
    print(f"   Voice: {config['tts']['voice']}")
    tts_generator.batch_generate(scenes, str(audio_output_dir))

    total_duration = sum(scene.duration for scene in scenes)
    logger.info(f"Audio generation complete. Total duration: {total_duration:.2f}s")
    print(f"   ✓ Audio generated ({total_duration:.2f} seconds total)")
    print()

    # -------------------------------------------------------------------------
    # STEP 3: Select and scale images for each scene
    # -------------------------------------------------------------------------
    print("🖼️  STEP 3/7: Selecting and scaling images...")
    logger.info("STEP 3/7: Selecting and scaling images")
    logger.info(f"Image selection mode: {config['visuals']['selection_mode']}")

    visual_selector = VisualSelector(config)
    images_dir = config['visuals']['images_dir']
    image_output_dir = temp_dir / "images"
    image_output_dir.mkdir(exist_ok=True)

    # Get target resolution from config
    target_resolution = (
        config['video']['resolution']['width'],
        config['video']['resolution']['height']
    )

    visual_selector.batch_process(scenes, images_dir, str(image_output_dir))

    # Recalculate total duration (may have changed if custom durations specified in filenames)
    total_duration = sum(scene.duration for scene in scenes)

    logger.info(f"Image processing complete. Resolution: {target_resolution[0]}x{target_resolution[1]}")
    print(f"   ✓ Images scaled to {target_resolution[0]}x{target_resolution[1]} ({config['video']['aspect_ratio']})")
    if config['visuals']['selection_mode'] == 'ordered':
        print(f"   ℹ️  Images selected in ordered mode by filename")
    print()

    # -------------------------------------------------------------------------
    # STEP 4: Generate subtitles for each scene
    # -------------------------------------------------------------------------
    print("📝 STEP 4/7: Generating subtitles...")
    logger.info("STEP 4/7: Generating subtitles")

    if config['subtitles']['enabled']:
        subtitle_generator = SubtitleGenerator(config)
        subtitle_output_dir = temp_dir / "subtitles"
        subtitle_output_dir.mkdir(exist_ok=True)

        subtitle_generator.batch_generate(scenes, str(subtitle_output_dir))

        logger.info(f"Subtitle generation complete")
        print(f"   ✓ Subtitles generated (max {config['subtitles']['max_chars_per_line']} chars/line)")
    else:
        logger.info("Subtitles disabled in configuration")
        print("   ⊘ Subtitles disabled")

    print()

    # -------------------------------------------------------------------------
    # STEP 5: Select and process background music
    # -------------------------------------------------------------------------
    print("🎵 STEP 5/7: Processing background music...")
    logger.info("STEP 5/7: Processing background music")

    music_path = None

    if config['audio']['music']['enabled']:
        music_selector = MusicSelector(config)
        music_dir = config['paths']['music_dir']
        music_output_dir = temp_dir / "music"
        music_output_dir.mkdir(exist_ok=True)

        # Select random music track
        selected_music = music_selector.select_music(music_dir)
        logger.info(f"Selected music: {Path(selected_music).name}")
        print(f"   Selected: {Path(selected_music).name}")

        # Adjust duration to match total video duration
        music_path = music_selector.adjust_duration(
            selected_music,
            total_duration,
            str(music_output_dir)
        )

        # Apply fade effects
        music_path = music_selector.apply_fade(
            music_path,
            fade_in=config['audio']['music']['fade_in'],
            fade_out=config['audio']['music']['fade_out'],
            output_dir=str(music_output_dir)
        )

        # NOTE: Volume is applied in VideoAssembler, not here (to avoid double application)
        logger.info(f"Music processed: duration={total_duration:.2f}s, fade_in={config['audio']['music']['fade_in']}s, fade_out={config['audio']['music']['fade_out']}s")
        logger.info(f"Music will be mixed with volume={config['audio']['music']['volume']} in video assembly")
        print(f"   ✓ Music processed (duration: {total_duration:.2f}s)")
    else:
        logger.info("Music disabled in configuration")
        print("   ⊘ Music disabled")

    print()

    # -------------------------------------------------------------------------
    # STEP 6: Assemble final video
    # -------------------------------------------------------------------------
    print("🎬 STEP 6/7: Assembling final video...")
    print("   This may take a few minutes...")
    logger.info("STEP 6/7: Assembling final video")

    video_assembler = VideoAssembler(config)

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Assemble the video
    final_video_path = video_assembler.assemble(
        scenes=scenes,
        output_path=str(output_file),
        background_music_path=music_path
    )

    logger.info(f"Video assembly complete: {final_video_path}")
    print(f"   ✓ Video rendered")
    print()

    # -------------------------------------------------------------------------
    # STEP 7: Summary
    # -------------------------------------------------------------------------
    print("=" * 70)
    print("✅ VIDEO GENERATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"📁 Output file: {final_video_path}")

    logger.info("=" * 70)
    logger.info("VIDEO GENERATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Output: {final_video_path}")

    # Get video info
    try:
        video_info = video_assembler.get_video_info(final_video_path)
        file_size_mb = Path(final_video_path).stat().st_size / (1024*1024)

        print()
        print("Video details:")
        print(f"  Duration:    {video_info['duration']:.2f} seconds")
        print(f"  Resolution:  {video_info['width']}x{video_info['height']}")
        print(f"  FPS:         {video_info['fps']}")
        print(f"  File size:   {file_size_mb:.2f} MB")

        logger.info(f"Duration: {video_info['duration']:.2f}s, Resolution: {video_info['width']}x{video_info['height']}, Size: {file_size_mb:.2f}MB")

    except Exception as e:
        logger.warning(f"Could not get video info: {e}")

    print()
    print("Scenes processed:")
    print(f"  Total scenes:  {len(scenes)}")
    print(f"  Total duration: {total_duration:.2f} seconds")
    print()
    print("=" * 70)

    logger.info(f"Total scenes: {len(scenes)}, Total duration: {total_duration:.2f}s")
    logger.info("Pipeline execution completed successfully")

    return True


def main():
    """Main application function"""

    # Parse command-line arguments
    args = parse_arguments()

    # Set log level from args (before loading config)
    log_level = None
    if args.quiet:
        log_level = 'ERROR'
    elif args.log_level:
        log_level = args.log_level

    # Initialize logger (will be reconfigured after loading config)
    logger = setup_logger(log_level=log_level)

    # Load configuration
    config = load_config(args.config, logger)

    # Reconfigure logger with proper config
    logger = setup_logger(config, log_level=log_level)

    # Log system info if debug level
    if logger.level <= 10:  # DEBUG
        log_system_info(logger)
        log_config_info(logger, config)

    # Apply CLI overrides
    apply_cli_overrides(config, args, logger)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = f"{config['project']['output_dir']}/video.mp4"

    # Validate input
    validate_input(args.input, logger)

    # Run the pipeline
    try:
        success = run_pipeline(args.input, output_path, config, logger)
        return 0 if success else 1

    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        print("\n\n⚠️  Pipeline interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        print()
        print("=" * 70)
        print("❌ ERROR DURING PROCESSING")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        print("Check the logs for more details:")
        print(f"  {config['logging']['file']}")
        print("=" * 70)

        if logger.level <= 10:  # DEBUG
            import traceback
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    sys.exit(main())
