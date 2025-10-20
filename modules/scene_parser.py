"""
Scene Parser Module
Handles parsing text files into Scene objects
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict
import re
from utils.exceptions import SceneParseError, ResourceNotFoundError


@dataclass
class Scene:
    """
    Represents a single scene in the video

    Attributes:
        id: Unique scene identifier
        text: Cleaned text content for the scene
        duration: Audio duration in seconds (calculated later)
        audio_path: Path to generated audio file
        subtitle_path: Path to generated subtitle file
        image_path: Path to selected/scaled image
        metadata: Additional metadata extracted from text
    """
    id: int
    text: str
    duration: float = 0.0
    audio_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    image_path: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class SceneParser:
    """
    Parser for converting text files into Scene objects
    """

    def __init__(self):
        """Initialize the scene parser"""
        pass

    def parse(self, file_path: str) -> List[Scene]:
        """
        Parse a text file and return list of Scene objects

        Args:
            file_path: Path to the text file (.txt or .md)

        Returns:
            List of Scene objects

        Raises:
            ResourceNotFoundError: If the file doesn't exist
            SceneParseError: If the file format is not supported or parsing fails
        """
        try:
            path = Path(file_path)

            if not path.exists():
                raise ResourceNotFoundError(
                    f"Input file not found",
                    resource_path=file_path,
                    details="Please check that the file path is correct"
                )

            if path.suffix not in ['.txt', '.md']:
                raise SceneParseError(
                    f"Unsupported file format: {path.suffix}",
                    file_path=file_path,
                    details="Supported formats: .txt, .md"
                )

            # Read file content
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError as e:
                raise SceneParseError(
                    "Failed to read file - invalid encoding",
                    file_path=file_path,
                    details=f"File must be UTF-8 encoded. Error: {str(e)}"
                )
            except IOError as e:
                raise SceneParseError(
                    "Failed to read file",
                    file_path=file_path,
                    details=str(e)
                )

            # Split into scenes
            scene_texts = self.split_into_scenes(content)

            if not scene_texts:
                raise SceneParseError(
                    "No valid scenes found in file",
                    file_path=file_path,
                    details="File appears to be empty or contains no valid paragraphs"
                )

            # Create Scene objects
            scenes = []
            for idx, text in enumerate(scene_texts, start=1):
                cleaned_text = self.clean_text(text)
                if cleaned_text:  # Ignore empty scenes
                    scene = Scene(id=idx, text=cleaned_text)
                    scenes.append(scene)

            if not scenes:
                raise SceneParseError(
                    "No valid scenes after cleaning",
                    file_path=file_path,
                    details="All paragraphs were empty after text cleaning"
                )

            return scenes

        except (ResourceNotFoundError, SceneParseError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any unexpected errors and wrap them
            raise SceneParseError(
                "Unexpected error during parsing",
                file_path=file_path,
                details=str(e)
            )

    def split_into_scenes(self, text: str) -> List[str]:
        """
        Split text into scenes by paragraphs (separated by double newlines)

        Args:
            text: Raw text content

        Returns:
            List of scene texts
        """
        # Split by double newlines (paragraph separator)
        scenes = re.split(r'\n\s*\n', text)

        # Filter out empty scenes
        scenes = [s.strip() for s in scenes if s.strip()]

        return scenes

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text
