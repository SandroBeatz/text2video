# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Text-to-Video Generator** - An automated system that converts text scripts into video content with:
- Local speech generation using Coqui TTS
- Automatic subtitle generation and synchronization
- Static background images
- Background music integration
- Video assembly via MoviePy/FFmpeg

The project is currently in the planning/design phase with comprehensive documentation but minimal code implementation.

## System Requirements

- Python 3.9+
- FFmpeg (must be installed and available in PATH)
- RAM: 4GB minimum, 8GB recommended

## Key Commands

### Development Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Initialize TTS models (after implementation)
python main.py --init
```

### Running the Application (Planned)
```bash
# Basic usage
python main.py --input script.txt --output my_video.mp4

# With custom configuration
python main.py -i script.txt -o video.mp4 -c custom_config.yaml

# Specify video format
python main.py -i script.txt --aspect-ratio 9:16

# Without background music
python main.py -i script.txt --no-music

# Different language
python main.py -i script.txt --language en
```

### Docker Usage (Planned)
```bash
# Build image
docker build -t text2video:latest .

# Run with volumes
docker run -v $(pwd)/input:/app/input \
           -v $(pwd)/output:/app/output \
           -v $(pwd)/assets:/app/assets \
           -v $(pwd)/config.yaml:/app/config.yaml \
           text2video:latest -i /app/input/script.txt

# Using docker-compose
docker-compose up
```

### Testing (When Implemented)
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scene_parser.py

# Run with coverage
pytest --cov=modules tests/
```

## Architecture

### Processing Pipeline

The system follows a sequential pipeline architecture:

1. **SceneParser** (`modules/scene_parser.py`)
   - Reads text files (.txt, .md)
   - Splits content into scenes by paragraphs
   - Cleans and normalizes text
   - Returns list of Scene objects

2. **TTSGenerator** (`modules/tts_generator.py`)
   - Initializes Coqui TTS with configured model
   - Generates WAV audio files for each scene
   - Calculates audio duration
   - Supports caching for performance

3. **SubtitleGenerator** (`modules/subtitle_generator.py`)
   - Creates SRT subtitle files
   - Calculates timings based on audio duration
   - Splits text into lines (max 40 chars per line)
   - Synchronizes with audio

4. **VisualSelector** (`modules/visual_selector.py`)
   - Selects background images (random or keyword-based)
   - Scales images to target resolution
   - Supports crop-to-fit, letterbox, or stretch modes

5. **MusicSelector** (`modules/music_selector.py`)
   - Selects background music tracks
   - Adjusts duration (trim or loop)
   - Mixes with voice audio
   - Applies fade in/out effects

6. **VideoAssembler** (`modules/video_assembler.py`)
   - Composites all elements (image, audio, subtitles)
   - Applies transitions between scenes
   - Adds background music
   - Renders final MP4 video

### Data Flow

```
Text Script → Scenes → Audio Files → Subtitles → Images → Music → Final Video
```

Each scene maintains state through a Scene dataclass with properties:
- `id`: Scene identifier
- `text`: Cleaned text content
- `duration`: Audio duration in seconds
- `audio_path`: Path to generated WAV file
- `subtitle_path`: Path to SRT subtitle file
- `image_path`: Path to selected/scaled image

### Directory Structure

```
text2video/
├── main.py                    # CLI entry point and pipeline orchestration
├── config.yaml               # Main configuration file
├── modules/                  # Core processing modules
│   ├── scene_parser.py      # Text parsing and scene extraction
│   ├── tts_generator.py     # Speech synthesis
│   ├── subtitle_generator.py # Subtitle creation and timing
│   ├── visual_selector.py   # Image selection and scaling
│   ├── music_selector.py    # Music selection and mixing
│   └── video_assembler.py   # Final video composition
├── utils/                   # Helper utilities
│   ├── logger.py           # Logging setup
│   ├── validators.py       # Input validation
│   └── file_handlers.py    # File I/O operations
├── assets/                 # Media resources
│   ├── images/            # Background images
│   ├── music/             # Background music tracks
│   └── fonts/             # Subtitle fonts
├── output/                # Generated videos
├── temp/                  # Temporary processing files
├── tests/                 # Test suite
└── docs/                  # Project documentation
    ├── docs.md           # Main documentation (Russian)
    ├── architecture.md   # Architecture details (Russian)
    └── plan.md           # Development plan (Russian)
```

## Configuration

The project uses YAML-based configuration (`config.yaml`) with sections for:

- **project**: Basic project metadata and output directory
- **tts**: Text-to-speech settings (model, language, speed)
- **video**: Video format settings (fps, resolution, aspect ratio, codec)
- **subtitles**: Subtitle styling (font, size, color, position)
- **audio**: Audio mixing settings (music volume, voice normalization)
- **visuals**: Image selection and transition settings
- **paths**: Directory paths for resources
- **logging**: Log level and output configuration

CLI arguments can override config.yaml settings.

## Key Implementation Details

### TTS Model Configuration

Supported languages and models:
- Russian: `tts_models/ru/ruslan/fairseq_vits`
- English: `tts_models/en/ljspeech/tacotron2-DDC`

Models are downloaded automatically on first use or via `--init` flag.

### Subtitle Timing Algorithm

Timings are calculated proportionally:
1. Split audio duration by word count to get time-per-word
2. Break text into lines respecting max character limit
3. Assign duration to each line based on word count
4. Generate sequential timings with no gaps

### Video Formats

Supported aspect ratios:
- 16:9 (1920x1080) - Horizontal/YouTube
- 9:16 (1080x1920) - Vertical/TikTok/Reels
- 1:1 (1080x1080) - Square/Instagram

Images are automatically scaled using crop-to-fit by default.

### Error Handling Strategy

- Module-level: Fallback mechanisms (backup models, chunking)
- Pipeline-level: Graceful failure with informative logging
- Custom exceptions in `utils/exceptions.py` for different failure modes

## Development Notes

### Current Project State

This repository contains **comprehensive planning documentation** but minimal actual code implementation. The documentation is in Russian and includes:

- Complete architecture design (docs/architecture.md)
- Detailed implementation plan with 7 phases (docs/plan.md)
- Full documentation of planned features (docs/docs.md)

Before implementing features, review these documents to understand the intended design.

### When Implementing New Features

1. Follow the phased development plan in `docs/plan.md`
2. Maintain the modular architecture - each module should be independent
3. Add comprehensive logging at each pipeline step
4. Implement error handling with custom exceptions
5. Create corresponding tests in `tests/` directory
6. Update `config.yaml` if new configuration options are needed

### Code Style Expectations

- Use type hints for all function parameters and return values
- Include docstrings for all classes and public methods
- Follow the pipeline pattern - each module processes and passes data forward
- Use dataclasses for structured data (like Scene)
- Prefer composition over inheritance

### Testing Approach

- Unit tests for each module independently
- Integration tests for full pipeline execution
- Use pytest with temporary directories for file operations
- Test with both Russian and English content
- Verify generated files (audio, subtitles, video) exist and have valid format

### Performance Considerations

- Implement caching for TTS generation (hash-based on text + config)
- Support batch processing where models allow
- Use lazy loading for heavy dependencies (TTS models)
- Consider GPU acceleration if available for TTS
- Add timing decorators to identify bottlenecks

### Dependencies to Install

Core dependencies (when implementing):
```
TTS>=0.22.0              # Coqui TTS for speech generation
moviepy>=1.0.3           # Video editing
pydub>=0.25.1            # Audio processing
pysrt>=1.1.2             # Subtitle handling
PyYAML>=6.0              # Config parsing
Pillow>=10.0.0           # Image processing
numpy>=1.24.0            # Numerical operations
tqdm                     # Progress bars
```

Development dependencies:
```
pytest
pytest-cov
```

## Troubleshooting

### Common Issues

**FFmpeg not found**
- Ensure FFmpeg is installed and in system PATH
- Test with: `ffmpeg -version`

**TTS model download fails**
- Check internet connection
- Models are cached in `~/.local/share/tts/` (Linux/macOS)
- Manually download and place in cache directory if needed

**Out of memory during TTS**
- Reduce scene text length (split longer paragraphs)
- Use smaller/faster TTS model
- Enable text chunking in TTSGenerator

**Video encoding slow**
- Reduce resolution in config.yaml
- Use faster codec preset (currently 'medium')
- Disable transitions if not needed

**Subtitle timing issues**
- Verify audio duration is correctly calculated
- Check max_chars_per_line isn't too small
- Review timing algorithm in subtitle_generator.py

## Future Enhancements (Post-MVP)

Planned features documented in plan.md:
- Scene transitions (crossfade, fade to black)
- Ken Burns effect (zoom/pan on images)
- Sentiment analysis for automatic music selection
- Intro/outro templates
- Web interface (Flask/FastAPI)
- REST API for integrations
- Batch processing from CSV
