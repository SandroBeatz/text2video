"""
Visual Selector Module
Handles image selection and scaling for video scenes
"""

import os
import re
import random
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image
from modules.scene_parser import Scene


class VisualSelector:
    """
    Selector for choosing and processing images for video scenes
    """

    # Supported image formats
    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    def __init__(self, config: dict):
        """
        Initialize visual selector

        Args:
            config: Configuration dictionary with visual settings
        """
        self.config = config
        visuals_config = config.get('visuals', {})
        video_config = config.get('video', {})

        self.images_dir = visuals_config.get('images_dir', './assets/images')
        self.default_duration = visuals_config.get('default_duration', 5)
        self.selection_mode = visuals_config.get('selection_mode', 'random')

        # Get target resolution from config
        resolution = video_config.get('resolution', {})
        self.target_width = resolution.get('width', 1920)
        self.target_height = resolution.get('height', 1080)

    def select_image(self, scene: Scene, images_dir: str = None) -> str:
        """
        Select a random image from the images directory

        Args:
            scene: Scene object (can be used for metadata-based selection in future)
            images_dir: Directory containing images (uses config default if None)

        Returns:
            Path to selected image

        Raises:
            FileNotFoundError: If images directory doesn't exist or is empty
        """
        if images_dir is None:
            images_dir = self.images_dir

        # Check if directory exists
        if not os.path.exists(images_dir):
            raise FileNotFoundError(f"Images directory not found: {images_dir}")

        # Get list of image files
        image_files = self._get_image_files(images_dir)

        if not image_files:
            raise FileNotFoundError(
                f"No images found in {images_dir}. "
                f"Supported formats: {self.SUPPORTED_FORMATS}"
            )

        # For now, select randomly
        # TODO: In future, can use scene.metadata for smart selection
        selected_image = random.choice(image_files)

        return selected_image

    def _get_image_files(self, directory: str) -> List[str]:
        """
        Get list of image files from directory

        Args:
            directory: Path to directory

        Returns:
            List of full paths to image files
        """
        image_files = []

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)

            # Check if it's a file and has supported extension
            if os.path.isfile(filepath) and filename.lower().endswith(self.SUPPORTED_FORMATS):
                image_files.append(filepath)

        return sorted(image_files)  # Sort for consistent ordering

    def _parse_image_filename(self, filename: str) -> Tuple[Optional[int], Optional[float]]:
        """
        Parse image filename to extract scene number and optional duration

        Args:
            filename: Image filename (e.g., '1.jpg', 'scene-2.jpg', '3_5.jpg', 'scene-4_10.5.jpg')

        Returns:
            Tuple of (scene_number, duration)
            - scene_number: int if found, None otherwise
            - duration: float if found in filename, None otherwise

        Supported formats:
            - 1.jpg -> (1, None)
            - scene-2.jpg -> (2, None)
            - 3_5.jpg -> (3, 5.0)
            - scene-4_10.5.jpg -> (4, 10.5)
            - image_1_3.5.jpg -> (1, 3.5)
        """
        base_name = os.path.splitext(filename)[0]  # Remove extension

        # Try to extract duration (format: _NUMBER or _NUMBER.NUMBER before extension)
        duration = None
        duration_match = re.search(r'_(\d+(?:\.\d+)?)$', base_name)
        if duration_match:
            duration = float(duration_match.group(1))
            # Remove duration part for scene number extraction
            base_name = base_name[:duration_match.start()]

        # Try to extract scene number
        # Pattern 1: scene-NUMBER or scene_NUMBER
        scene_match = re.search(r'scene[-_](\d+)', base_name, re.IGNORECASE)
        if scene_match:
            scene_number = int(scene_match.group(1))
            return (scene_number, duration)

        # Pattern 2: Just NUMBER at start or end
        number_match = re.search(r'^\d+$|^(\d+)[-_]|[-_](\d+)$', base_name)
        if number_match:
            # Extract the number from whichever group matched
            number_str = number_match.group(1) or number_match.group(2) or number_match.group(0)
            scene_number = int(number_str)
            return (scene_number, duration)

        # No scene number found
        return (None, duration)

    def select_image_ordered(
        self,
        scene: Scene,
        images_dir: str = None
    ) -> Tuple[str, Optional[float]]:
        """
        Select image based on scene number from filename

        Args:
            scene: Scene object with id
            images_dir: Directory containing images

        Returns:
            Tuple of (image_path, duration)
            - image_path: Path to selected image
            - duration: Duration from filename if specified, None otherwise

        Raises:
            FileNotFoundError: If no matching image found for scene number
        """
        if images_dir is None:
            images_dir = self.images_dir

        if not os.path.exists(images_dir):
            raise FileNotFoundError(f"Images directory not found: {images_dir}")

        # Get all image files
        image_files = self._get_image_files(images_dir)

        if not image_files:
            raise FileNotFoundError(
                f"No images found in {images_dir}. "
                f"Supported formats: {self.SUPPORTED_FORMATS}"
            )

        # Parse all filenames and create mapping
        scene_images = {}  # scene_number -> (image_path, duration)
        for image_path in image_files:
            filename = os.path.basename(image_path)
            scene_number, duration = self._parse_image_filename(filename)

            if scene_number is not None:
                scene_images[scene_number] = (image_path, duration)

        # Find image for this scene
        if scene.id in scene_images:
            return scene_images[scene.id]
        else:
            raise FileNotFoundError(
                f"No image found for scene {scene.id}. "
                f"Expected filename formats: {scene.id}.jpg, scene-{scene.id}.jpg, or {scene.id}_DURATION.jpg. "
                f"Available scene numbers: {sorted(scene_images.keys())}"
            )

    def scale_image(
        self,
        image_path: str,
        target_resolution: Tuple[int, int] = None,
        output_dir: str = None
    ) -> str:
        """
        Scale image to target resolution using crop-to-fit algorithm

        Args:
            image_path: Path to source image
            target_resolution: Target (width, height), uses config default if None
            output_dir: Directory to save scaled image

        Returns:
            Path to scaled image file

        Raises:
            FileNotFoundError: If source image doesn't exist
            RuntimeError: If image processing fails

        Algorithm:
            1. Calculate aspect ratios of source and target
            2. Resize image so that it covers target area
            3. Crop center to exact target dimensions
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if target_resolution is None:
            target_resolution = (self.target_width, self.target_height)

        target_width, target_height = target_resolution

        try:
            # Open image
            img = Image.open(image_path)

            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Get original dimensions
            orig_width, orig_height = img.size

            # Calculate aspect ratios
            orig_aspect = orig_width / orig_height
            target_aspect = target_width / target_height

            # Determine resize dimensions (cover the target area)
            if orig_aspect > target_aspect:
                # Image is wider - match height and crop width
                new_height = target_height
                new_width = int(target_height * orig_aspect)
            else:
                # Image is taller - match width and crop height
                new_width = target_width
                new_height = int(target_width / orig_aspect)

            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Calculate crop coordinates (center crop)
            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
            right = left + target_width
            bottom = top + target_height

            # Crop to target dimensions
            img_cropped = img_resized.crop((left, top, right, bottom))

            # Generate output filename
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(image_path), 'scaled')

            os.makedirs(output_dir, exist_ok=True)

            # Create output filename
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            output_filename = f"{name}_scaled_{target_width}x{target_height}{ext}"
            output_path = os.path.join(output_dir, output_filename)

            # Save scaled image
            img_cropped.save(output_path, quality=95)

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to scale image {image_path}: {e}")

    def batch_process(
        self,
        scenes: List[Scene],
        images_dir: str = None,
        output_dir: str = None
    ) -> None:
        """
        Process images for multiple scenes

        Args:
            scenes: List of Scene objects
            images_dir: Directory containing source images
            output_dir: Directory to save scaled images

        Note:
            This method updates each scene's image_path and duration (if specified in filename)
        """
        if output_dir is None:
            output_dir = os.path.join(self.config.get('paths', {}).get('temp_dir', './temp'), 'images')

        for scene in scenes:
            # Select image based on mode
            if self.selection_mode == 'ordered':
                # Ordered selection: match by scene number in filename
                image_path, custom_duration = self.select_image_ordered(scene, images_dir)

                # Apply custom duration if specified in filename
                if custom_duration is not None:
                    scene.duration = custom_duration
            else:
                # Random selection (default)
                image_path = self.select_image(scene, images_dir)

            # Scale image
            scaled_image_path = self.scale_image(image_path, output_dir=output_dir)

            # Update scene
            scene.image_path = scaled_image_path

    def get_image_info(self, image_path: str) -> dict:
        """
        Get information about an image

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with image information (width, height, format, mode)

        Raises:
            FileNotFoundError: If image doesn't exist
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size': os.path.getsize(image_path)
                }
        except Exception as e:
            raise RuntimeError(f"Failed to get image info: {e}")
