"""
Tests for Visual Selector Module
"""

import pytest
import os
from pathlib import Path
from PIL import Image
from modules.scene_parser import Scene
from modules.visual_selector import VisualSelector


@pytest.fixture
def create_test_images(tmp_path):
    """Create test images with different aspect ratios"""
    images_dir = tmp_path / "test_images"
    images_dir.mkdir()

    # Create horizontal image (landscape) 1600x900
    horizontal_img = Image.new('RGB', (1600, 900), color='blue')
    horizontal_path = images_dir / "horizontal.jpg"
    horizontal_img.save(horizontal_path)

    # Create vertical image (portrait) 900x1600
    vertical_img = Image.new('RGB', (900, 1600), color='red')
    vertical_path = images_dir / "vertical.jpg"
    vertical_img.save(vertical_path)

    # Create square image 1000x1000
    square_img = Image.new('RGB', (1000, 1000), color='green')
    square_path = images_dir / "square.jpg"
    square_img.save(square_path)

    # Create PNG image
    png_img = Image.new('RGB', (800, 600), color='yellow')
    png_path = images_dir / "test.png"
    png_img.save(png_path)

    return {
        'dir': str(images_dir),
        'horizontal': str(horizontal_path),
        'vertical': str(vertical_path),
        'square': str(square_path),
        'png': str(png_path)
    }


class TestVisualSelector:
    """Tests for VisualSelector class"""

    def test_selector_initialization(self):
        """Test creating a VisualSelector"""
        config = {
            'visuals': {
                'images_dir': './assets/images',
                'default_duration': 5
            },
            'video': {
                'resolution': {
                    'width': 1920,
                    'height': 1080
                }
            }
        }
        selector = VisualSelector(config)
        assert selector is not None
        assert selector.images_dir == './assets/images'
        assert selector.default_duration == 5
        assert selector.target_width == 1920
        assert selector.target_height == 1080

    def test_selector_default_settings(self):
        """Test default settings when config is minimal"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)
        assert selector.images_dir == './assets/images'
        assert selector.default_duration == 5
        assert selector.target_width == 1920
        assert selector.target_height == 1080

    def test_get_image_files(self, create_test_images):
        """Test getting list of image files"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        image_files = selector._get_image_files(create_test_images['dir'])

        assert len(image_files) == 4
        # Should be sorted
        assert all('.jpg' in f or '.png' in f for f in image_files)

    def test_get_image_files_empty_directory(self, tmp_path):
        """Test getting image files from empty directory"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        image_files = selector._get_image_files(str(empty_dir))
        assert len(image_files) == 0

    def test_select_image_random(self, create_test_images):
        """Test selecting a random image"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        scene = Scene(id=1, text="Test scene")
        image_path = selector.select_image(scene, create_test_images['dir'])

        assert os.path.exists(image_path)
        assert image_path in [
            create_test_images['horizontal'],
            create_test_images['vertical'],
            create_test_images['square'],
            create_test_images['png']
        ]

    def test_select_image_no_directory(self):
        """Test selecting image when directory doesn't exist"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        scene = Scene(id=1, text="Test")

        with pytest.raises(FileNotFoundError, match="Images directory not found"):
            selector.select_image(scene, "/nonexistent/directory")

    def test_select_image_empty_directory(self, tmp_path):
        """Test selecting image from empty directory"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        scene = Scene(id=1, text="Test")

        with pytest.raises(FileNotFoundError, match="No images found"):
            selector.select_image(scene, str(empty_dir))

    def test_scale_image_horizontal(self, create_test_images, tmp_path):
        """Test scaling horizontal image to target resolution"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"
        scaled_path = selector.scale_image(
            create_test_images['horizontal'],
            target_resolution=(1920, 1080),
            output_dir=str(output_dir)
        )

        assert os.path.exists(scaled_path)

        # Check scaled image dimensions
        with Image.open(scaled_path) as img:
            assert img.width == 1920
            assert img.height == 1080

    def test_scale_image_vertical(self, create_test_images, tmp_path):
        """Test scaling vertical image to target resolution"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"
        scaled_path = selector.scale_image(
            create_test_images['vertical'],
            target_resolution=(1920, 1080),
            output_dir=str(output_dir)
        )

        assert os.path.exists(scaled_path)

        with Image.open(scaled_path) as img:
            assert img.width == 1920
            assert img.height == 1080

    def test_scale_image_square(self, create_test_images, tmp_path):
        """Test scaling square image to target resolution"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"
        scaled_path = selector.scale_image(
            create_test_images['square'],
            target_resolution=(1920, 1080),
            output_dir=str(output_dir)
        )

        assert os.path.exists(scaled_path)

        with Image.open(scaled_path) as img:
            assert img.width == 1920
            assert img.height == 1080

    def test_scale_image_creates_output_directory(self, create_test_images, tmp_path):
        """Test that scale_image creates output directory if it doesn't exist"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "nonexistent" / "scaled"

        # Directory doesn't exist yet
        assert not output_dir.exists()

        scaled_path = selector.scale_image(
            create_test_images['horizontal'],
            output_dir=str(output_dir)
        )

        # Directory should be created
        assert output_dir.exists()
        assert os.path.exists(scaled_path)

    def test_scale_image_nonexistent_file(self):
        """Test scaling image that doesn't exist"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        with pytest.raises(FileNotFoundError, match="Image not found"):
            selector.scale_image("/nonexistent/image.jpg")

    def test_scale_image_filename_format(self, create_test_images, tmp_path):
        """Test that scaled image has correct filename format"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"
        scaled_path = selector.scale_image(
            create_test_images['horizontal'],
            target_resolution=(1920, 1080),
            output_dir=str(output_dir)
        )

        # Should contain dimensions in filename
        assert "horizontal_scaled_1920x1080" in scaled_path

    def test_scale_image_different_resolutions(self, create_test_images, tmp_path):
        """Test scaling to different target resolutions"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"

        # Test 9:16 vertical video
        scaled_path_vertical = selector.scale_image(
            create_test_images['horizontal'],
            target_resolution=(1080, 1920),
            output_dir=str(output_dir)
        )

        with Image.open(scaled_path_vertical) as img:
            assert img.width == 1080
            assert img.height == 1920

        # Test 1:1 square video
        scaled_path_square = selector.scale_image(
            create_test_images['horizontal'],
            target_resolution=(1080, 1080),
            output_dir=str(output_dir)
        )

        with Image.open(scaled_path_square) as img:
            assert img.width == 1080
            assert img.height == 1080

    def test_scale_image_png_format(self, create_test_images, tmp_path):
        """Test scaling PNG images"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"
        scaled_path = selector.scale_image(
            create_test_images['png'],
            output_dir=str(output_dir)
        )

        assert os.path.exists(scaled_path)
        assert scaled_path.endswith('.png')

    def test_scale_image_rgba_to_rgb(self, tmp_path):
        """Test that RGBA images are converted to RGB"""
        # Create RGBA image
        rgba_img = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
        rgba_path = tmp_path / "rgba_test.png"
        rgba_img.save(rgba_path)

        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"
        scaled_path = selector.scale_image(
            str(rgba_path),
            output_dir=str(output_dir)
        )

        # Check that output is RGB
        with Image.open(scaled_path) as img:
            assert img.mode == 'RGB'

    def test_get_image_info(self, create_test_images):
        """Test getting image information"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        info = selector.get_image_info(create_test_images['horizontal'])

        assert info['width'] == 1600
        assert info['height'] == 900
        assert info['format'] == 'JPEG'
        assert info['mode'] == 'RGB'
        assert info['size'] > 0

    def test_get_image_info_nonexistent(self):
        """Test getting info for nonexistent image"""
        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        with pytest.raises(FileNotFoundError, match="Image not found"):
            selector.get_image_info("/nonexistent/image.jpg")

    def test_batch_process(self, create_test_images, tmp_path):
        """Test batch processing multiple scenes"""
        config = {
            'visuals': {'images_dir': create_test_images['dir']},
            'video': {},
            'paths': {'temp_dir': str(tmp_path / "temp")}
        }
        selector = VisualSelector(config)

        scenes = [
            Scene(id=1, text="First scene"),
            Scene(id=2, text="Second scene"),
            Scene(id=3, text="Third scene"),
        ]

        output_dir = tmp_path / "batch_output"
        selector.batch_process(scenes, images_dir=create_test_images['dir'], output_dir=str(output_dir))

        # Check that all scenes have image_path set
        for scene in scenes:
            assert scene.image_path is not None
            assert os.path.exists(scene.image_path)

            # Check image dimensions
            with Image.open(scene.image_path) as img:
                assert img.width == 1920
                assert img.height == 1080

    def test_scale_preserves_center(self, tmp_path):
        """Test that crop-to-fit preserves center of image"""
        # Create image with distinct regions
        img = Image.new('RGB', (2000, 1000), color='white')

        # Draw colored borders to test cropping
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 100, 1000], fill='red')  # Left border
        draw.rectangle([1900, 0, 2000, 1000], fill='blue')  # Right border

        test_image_path = tmp_path / "test_crop.jpg"
        img.save(test_image_path)

        config = {'visuals': {}, 'video': {}}
        selector = VisualSelector(config)

        output_dir = tmp_path / "scaled"
        scaled_path = selector.scale_image(
            str(test_image_path),
            target_resolution=(1920, 1080),
            output_dir=str(output_dir)
        )

        # Scaled image should be mostly white (center preserved)
        # Red and blue borders should be cropped out
        with Image.open(scaled_path) as scaled_img:
            # Sample center pixel
            center_pixel = scaled_img.getpixel((960, 540))
            # Should be white or very close to white
            assert center_pixel[0] > 200  # R
            assert center_pixel[1] > 200  # G
            assert center_pixel[2] > 200  # B
