"""
Logger Utility
Provides logging functionality for the Text-to-Video Generator
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    config: Optional[dict] = None,
    name: str = 'text2video',
    log_level: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure logger for the application

    Args:
        config: Configuration dictionary with logging settings
        name: Logger name (default: 'text2video')
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance

    Example:
        >>> config = {'logging': {'level': 'INFO', 'file': './logs/app.log', 'console': True}}
        >>> logger = setup_logger(config)
        >>> logger.info("Application started")
    """
    # Get logging configuration
    if config is None:
        config = {}

    log_config = config.get('logging', {})

    # Determine log level
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        level_str = log_config.get('level', 'INFO')
        level = getattr(logging, level_str.upper(), logging.INFO)

    # Get log file path
    log_file = log_config.get('file', './logs/app.log')

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (if enabled)
    console_enabled = log_config.get('console', True)
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger


def get_module_logger(module_name: str, parent_logger: Optional[logging.Logger] = None) -> logging.Logger:
    """
    Get a logger for a specific module

    Args:
        module_name: Name of the module (e.g., 'scene_parser', 'tts_generator')
        parent_logger: Parent logger (if None, uses root text2video logger)

    Returns:
        Logger instance for the module

    Example:
        >>> logger = get_module_logger('scene_parser')
        >>> logger.info("Parsing scene")
    """
    if parent_logger:
        logger_name = f"{parent_logger.name}.{module_name}"
    else:
        logger_name = f"text2video.{module_name}"

    logger = logging.getLogger(logger_name)

    # If parent logger exists, inherit its level and handlers
    if parent_logger:
        logger.setLevel(parent_logger.level)
        # Don't add handlers here - they will be inherited from parent
        logger.propagate = True
    else:
        # If no parent, try to get the text2video logger
        parent = logging.getLogger('text2video')
        if parent.handlers:
            logger.setLevel(parent.level)
            logger.propagate = True

    return logger


def log_system_info(logger: logging.Logger):
    """
    Log system information for debugging

    Args:
        logger: Logger instance
    """
    import sys
    import platform

    logger.debug("=" * 60)
    logger.debug("System Information")
    logger.debug("=" * 60)
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {platform.platform()}")
    logger.debug(f"Machine: {platform.machine()}")
    logger.debug(f"Processor: {platform.processor()}")
    logger.debug("=" * 60)


def log_config_info(logger: logging.Logger, config: dict):
    """
    Log configuration information

    Args:
        logger: Logger instance
        config: Configuration dictionary
    """
    logger.debug("=" * 60)
    logger.debug("Configuration")
    logger.debug("=" * 60)

    # Log key configuration sections
    sections = ['project', 'tts', 'video', 'audio', 'subtitles', 'visuals']

    for section in sections:
        if section in config:
            logger.debug(f"{section.upper()}:")
            for key, value in config[section].items():
                # Don't log entire nested dicts, just summarize
                if isinstance(value, dict):
                    logger.debug(f"  {key}: {{{len(value)} items}}")
                else:
                    logger.debug(f"  {key}: {value}")

    logger.debug("=" * 60)


class LoggerContext:
    """
    Context manager for temporary log level changes

    Example:
        >>> logger = setup_logger()
        >>> logger.setLevel(logging.INFO)
        >>> with LoggerContext(logger, logging.DEBUG):
        ...     logger.debug("This will be logged")
        >>> logger.debug("This won't be logged")
    """

    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.new_level = level
        self.old_level = logger.level

    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)
        return False


def add_file_handler(logger: logging.Logger, log_file: str, level: Optional[int] = None):
    """
    Add an additional file handler to a logger

    Args:
        logger: Logger instance
        log_file: Path to log file
        level: Log level for this handler (if None, uses logger's level)
    """
    # Create directory if needed
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create handler
    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setLevel(level if level else logger.level)

    # Use same formatter as existing handlers
    if logger.handlers:
        handler.setFormatter(logger.handlers[0].formatter)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

    logger.addHandler(handler)


def close_logger(logger: logging.Logger):
    """
    Close all handlers for a logger

    Args:
        logger: Logger instance
    """
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
