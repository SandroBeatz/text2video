"""
Validation utilities for Text-to-Video Generator.

This module provides validation functions for files, directories,
and configuration settings.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging


logger = logging.getLogger(__name__)


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists.

    Args:
        file_path: Path to the file to check

    Returns:
        True if file exists, False otherwise
    """
    if not file_path:
        logger.warning("Empty file path provided")
        return False

    path = Path(file_path)
    exists = path.exists() and path.is_file()

    if not exists:
        logger.warning(f"File does not exist: {file_path}")

    return exists


def validate_file_format(file_path: str, allowed_formats: List[str]) -> bool:
    """
    Validate that a file has an allowed format/extension.

    Args:
        file_path: Path to the file to check
        allowed_formats: List of allowed file extensions (e.g., ['.txt', '.md'])

    Returns:
        True if file format is allowed, False otherwise
    """
    if not file_path:
        logger.warning("Empty file path provided")
        return False

    if not allowed_formats:
        logger.warning("No allowed formats specified")
        return False

    # Normalize extensions to lowercase with leading dot
    normalized_formats = []
    for fmt in allowed_formats:
        fmt = fmt.lower()
        if not fmt.startswith('.'):
            fmt = '.' + fmt
        normalized_formats.append(fmt)

    path = Path(file_path)
    extension = path.suffix.lower()

    is_valid = extension in normalized_formats

    if not is_valid:
        logger.warning(
            f"Invalid file format: {extension}. "
            f"Allowed formats: {', '.join(normalized_formats)}"
        )

    return is_valid


def validate_directory_exists(dir_path: str, create_if_missing: bool = False) -> bool:
    """
    Validate that a directory exists.

    Args:
        dir_path: Path to the directory to check
        create_if_missing: If True, create directory if it doesn't exist

    Returns:
        True if directory exists (or was created), False otherwise
    """
    if not dir_path:
        logger.warning("Empty directory path provided")
        return False

    path = Path(dir_path)

    if path.exists() and path.is_dir():
        return True

    if create_if_missing:
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            return False
    else:
        logger.warning(f"Directory does not exist: {dir_path}")
        return False


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that a configuration dictionary has all required fields.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if configuration is valid, False otherwise
    """
    if not config:
        logger.error("Empty configuration provided")
        return False

    # Required top-level sections
    required_sections = ['project', 'video', 'tts', 'subtitles', 'audio', 'paths']

    for section in required_sections:
        if section not in config:
            logger.error(f"Missing required configuration section: {section}")
            return False

    # Validate project section
    if 'name' not in config['project']:
        logger.error("Missing 'name' in project section")
        return False

    # Validate video section
    video_required = ['fps', 'resolution', 'codec']
    for field in video_required:
        if field not in config['video']:
            logger.error(f"Missing '{field}' in video section")
            return False

    # Validate resolution structure
    if 'width' not in config['video']['resolution'] or 'height' not in config['video']['resolution']:
        logger.error("Missing 'width' or 'height' in video resolution")
        return False

    # Validate TTS section
    if 'language' not in config['tts']:
        logger.error("Missing 'language' in TTS section")
        return False

    # Validate paths section
    paths_required = ['music_dir', 'temp_dir']
    for field in paths_required:
        if field not in config['paths']:
            logger.error(f"Missing '{field}' in paths section")
            return False

    logger.debug("Configuration validation successful")
    return True


def validate_resolution(width: int, height: int) -> bool:
    """
    Validate video resolution values.

    Args:
        width: Video width in pixels
        height: Video height in pixels

    Returns:
        True if resolution is valid, False otherwise
    """
    if width <= 0 or height <= 0:
        logger.error(f"Invalid resolution: {width}x{height}. Values must be positive.")
        return False

    if width > 7680 or height > 4320:  # Max 8K resolution
        logger.warning(
            f"Resolution {width}x{height} is very high. "
            "This may cause performance issues."
        )
        return True  # Still valid, just warn

    if width < 320 or height < 240:  # Min reasonable resolution
        logger.warning(
            f"Resolution {width}x{height} is very low. "
            "Output quality may be poor."
        )
        return True  # Still valid, just warn

    return True


def validate_aspect_ratio(aspect_ratio: str) -> bool:
    """
    Validate aspect ratio string.

    Args:
        aspect_ratio: Aspect ratio string (e.g., '16:9', '9:16', '1:1')

    Returns:
        True if aspect ratio is valid, False otherwise
    """
    valid_ratios = ['16:9', '9:16', '1:1', '4:3', '21:9']

    if aspect_ratio not in valid_ratios:
        logger.error(
            f"Invalid aspect ratio: {aspect_ratio}. "
            f"Allowed values: {', '.join(valid_ratios)}"
        )
        return False

    return True


def validate_language(language: str) -> bool:
    """
    Validate language code.

    Args:
        language: Language code (e.g., 'ru', 'en')

    Returns:
        True if language is supported, False otherwise
    """
    supported_languages = ['ru', 'en']

    if language not in supported_languages:
        logger.error(
            f"Unsupported language: {language}. "
            f"Supported languages: {', '.join(supported_languages)}"
        )
        return False

    return True


def validate_fps(fps: int) -> bool:
    """
    Validate frames per second value.

    Args:
        fps: Frames per second

    Returns:
        True if FPS is valid, False otherwise
    """
    if fps <= 0:
        logger.error(f"Invalid FPS: {fps}. Value must be positive.")
        return False

    if fps < 10 or fps > 120:
        logger.warning(
            f"FPS {fps} is outside normal range (10-120). "
            "This may cause issues."
        )
        return True  # Still valid, just warn

    return True


def validate_volume(volume: float, param_name: str = "volume") -> bool:
    """
    Validate audio volume value (0.0 to 1.0).

    Args:
        volume: Volume level (0.0 to 1.0)
        param_name: Name of the parameter for error messages

    Returns:
        True if volume is valid, False otherwise
    """
    if volume < 0.0 or volume > 1.0:
        logger.error(
            f"Invalid {param_name}: {volume}. "
            "Value must be between 0.0 and 1.0."
        )
        return False

    return True


def validate_duration(duration: float) -> bool:
    """
    Validate duration value.

    Args:
        duration: Duration in seconds

    Returns:
        True if duration is valid, False otherwise
    """
    if duration <= 0:
        logger.error(f"Invalid duration: {duration}. Value must be positive.")
        return False

    if duration > 3600:  # 1 hour
        logger.warning(
            f"Duration {duration}s is very long (>1 hour). "
            "Processing may take a long time."
        )
        return True  # Still valid, just warn

    return True


def validate_path_is_safe(path: str) -> bool:
    """
    Validate that a path is safe and doesn't try to escape the project directory.

    Args:
        path: Path to validate

    Returns:
        True if path is safe, False otherwise
    """
    if not path:
        logger.warning("Empty path provided")
        return False

    # Check for path traversal attempts
    if '..' in path or path.startswith('/'):
        logger.error(f"Unsafe path detected: {path}")
        return False

    # Check for absolute paths on Windows
    if os.name == 'nt' and ':' in path and path[1] == ':':
        logger.warning(f"Absolute Windows path detected: {path}")
        # This is not necessarily unsafe, just log it

    return True


def validate_text_content(text: str, min_length: int = 1, max_length: int = 100000) -> bool:
    """
    Validate text content length.

    Args:
        text: Text content to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        True if text is valid, False otherwise
    """
    if not text:
        logger.error("Empty text content provided")
        return False

    text_length = len(text)

    if text_length < min_length:
        logger.error(
            f"Text too short: {text_length} characters. "
            f"Minimum: {min_length} characters."
        )
        return False

    if text_length > max_length:
        logger.error(
            f"Text too long: {text_length} characters. "
            f"Maximum: {max_length} characters."
        )
        return False

    return True
