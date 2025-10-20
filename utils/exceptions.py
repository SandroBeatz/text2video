"""
Custom exceptions for Text-to-Video Generator.

This module defines custom exception classes for different
error scenarios in the video generation pipeline.
"""


class Text2VideoException(Exception):
    """
    Base exception for all Text-to-Video Generator errors.

    All custom exceptions in this project inherit from this class.
    """

    def __init__(self, message: str, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            details: Additional error details (optional)
        """
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class SceneParseError(Text2VideoException):
    """
    Exception raised when scene parsing fails.

    This can occur when:
    - Input file cannot be read
    - File format is not supported
    - Text content is invalid
    - Parsing logic encounters unexpected data
    """

    def __init__(self, message: str, file_path: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            file_path: Path to the file that caused the error
            details: Additional error details
        """
        self.file_path = file_path
        if file_path:
            message = f"{message} (file: {file_path})"
        super().__init__(message, details)


class TTSError(Text2VideoException):
    """
    Exception raised when text-to-speech generation fails.

    This can occur when:
    - TTS model fails to initialize
    - Audio generation fails
    - Model is not available for the requested language
    - Generated audio file is invalid
    """

    def __init__(self, message: str, language: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            language: Language code that caused the error
            details: Additional error details
        """
        self.language = language
        if language:
            message = f"{message} (language: {language})"
        super().__init__(message, details)


class SubtitleError(Text2VideoException):
    """
    Exception raised when subtitle generation fails.

    This can occur when:
    - SRT file creation fails
    - Timing calculation fails
    - Text splitting encounters errors
    - Invalid subtitle format
    """

    def __init__(self, message: str, scene_id: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            scene_id: ID of the scene that caused the error
            details: Additional error details
        """
        self.scene_id = scene_id
        if scene_id:
            message = f"{message} (scene: {scene_id})"
        super().__init__(message, details)


class VisualError(Text2VideoException):
    """
    Exception raised when visual/image processing fails.

    This can occur when:
    - Image file cannot be read
    - Image format is not supported
    - Image scaling/cropping fails
    - No images available in the images directory
    - Invalid image resolution
    """

    def __init__(self, message: str, image_path: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            image_path: Path to the image that caused the error
            details: Additional error details
        """
        self.image_path = image_path
        if image_path:
            message = f"{message} (image: {image_path})"
        super().__init__(message, details)


class MusicError(Text2VideoException):
    """
    Exception raised when music processing fails.

    This can occur when:
    - Music file cannot be read
    - Audio format is not supported
    - Duration adjustment fails
    - Fade effects cannot be applied
    - Volume adjustment fails
    - Mixing with voice fails
    - No music files available
    """

    def __init__(self, message: str, music_path: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            music_path: Path to the music file that caused the error
            details: Additional error details
        """
        self.music_path = music_path
        if music_path:
            message = f"{message} (music: {music_path})"
        super().__init__(message, details)


class VideoAssemblyError(Text2VideoException):
    """
    Exception raised when video assembly fails.

    This can occur when:
    - Video clip creation fails
    - Scene concatenation fails
    - Audio/video sync issues
    - Subtitle rendering fails
    - Final video encoding fails
    - FFmpeg errors
    - Insufficient disk space
    """

    def __init__(self, message: str, output_path: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            output_path: Path where output was expected
            details: Additional error details
        """
        self.output_path = output_path
        if output_path:
            message = f"{message} (output: {output_path})"
        super().__init__(message, details)


class ConfigError(Text2VideoException):
    """
    Exception raised when configuration is invalid.

    This can occur when:
    - Config file cannot be read
    - Config file has invalid YAML syntax
    - Required configuration fields are missing
    - Configuration values are invalid
    - Config file path doesn't exist
    """

    def __init__(self, message: str, config_path: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            config_path: Path to the config file that caused the error
            details: Additional error details
        """
        self.config_path = config_path
        if config_path:
            message = f"{message} (config: {config_path})"
        super().__init__(message, details)


class ValidationError(Text2VideoException):
    """
    Exception raised when input validation fails.

    This can occur when:
    - File path is invalid
    - File format is not allowed
    - Directory doesn't exist
    - Parameter values are out of range
    - Required fields are missing
    """

    def __init__(self, message: str, field_name: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            field_name: Name of the field that failed validation
            details: Additional error details
        """
        self.field_name = field_name
        if field_name:
            message = f"{message} (field: {field_name})"
        super().__init__(message, details)


class DependencyError(Text2VideoException):
    """
    Exception raised when required dependencies are missing.

    This can occur when:
    - FFmpeg is not installed
    - Required Python packages are missing
    - TTS models are not downloaded
    - System requirements are not met
    """

    def __init__(self, message: str, dependency: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            dependency: Name of the missing dependency
            details: Additional error details (e.g., installation instructions)
        """
        self.dependency = dependency
        if dependency:
            message = f"{message} (dependency: {dependency})"
        super().__init__(message, details)


class ResourceNotFoundError(Text2VideoException):
    """
    Exception raised when a required resource is not found.

    This can occur when:
    - Input file doesn't exist
    - Asset directory is empty
    - Font file is missing
    - Required files were deleted during processing
    """

    def __init__(self, message: str, resource_path: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            resource_path: Path to the missing resource
            details: Additional error details
        """
        self.resource_path = resource_path
        if resource_path:
            message = f"{message} (resource: {resource_path})"
        super().__init__(message, details)


class ProcessingError(Text2VideoException):
    """
    Exception raised when a processing step fails.

    This is a generic exception for processing errors that don't
    fit into more specific categories.
    """

    def __init__(self, message: str, step: str = None, details: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            step: Name of the processing step that failed
            details: Additional error details
        """
        self.step = step
        if step:
            message = f"{message} (step: {step})"
        super().__init__(message, details)
