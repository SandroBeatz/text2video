#!/usr/bin/env python3
"""
Demo: SceneParser + TTSGenerator Integration
Demonstrates parsing a text script and generating audio for each scene
"""

import yaml
from pathlib import Path
from modules.scene_parser import SceneParser
from modules.tts_generator import TTSGenerator


def main():
    """Main demo function"""
    print("=" * 60)
    print("Demo: Text-to-Video Generator - Scene Parser + TTS Integration")
    print("=" * 60)
    print()

    # Load configuration
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Step 1: Parse the script
    print("Step 1: Parsing the script...")
    script_path = Path(__file__).parent / "input" / "test_script.txt"

    parser = SceneParser()
    scenes = parser.parse(str(script_path))

    print(f"✓ Parsed {len(scenes)} scenes from the script")
    print()

    # Display parsed scenes
    print("Parsed scenes:")
    print("-" * 60)
    for scene in scenes:
        print(f"Scene {scene.id}:")
        print(f"  Text: {scene.text[:50]}..." if len(scene.text) > 50 else f"  Text: {scene.text}")
        print(f"  Audio: {scene.audio_path or 'Not generated yet'}")
        print(f"  Duration: {scene.duration:.2f}s")
        print()

    # Step 2: Generate audio (optional - requires TTS models)
    print("-" * 60)
    print("Step 2: Audio Generation")
    print()
    print("Note: To generate audio, TTS models need to be downloaded.")
    print("This can be done by running:")
    print("  ./venv/bin/python -c \"from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')\"")
    print()

    # Check if TTS is available
    try:
        from TTS.api import TTS
        print("✓ TTS library is installed")

        # Ask user if they want to generate audio
        response = input("Generate audio for scenes? (y/N): ").strip().lower()

        if response == 'y':
            print()
            print("Generating audio...")

            output_dir = Path(__file__).parent / "output" / "demo_audio"
            output_dir.mkdir(parents=True, exist_ok=True)

            tts_generator = TTSGenerator(config)
            tts_generator.batch_generate(scenes, str(output_dir))

            print()
            print("Audio generation complete!")
            print()
            print("Generated files:")
            print("-" * 60)
            for scene in scenes:
                print(f"Scene {scene.id}:")
                print(f"  Audio: {scene.audio_path}")
                print(f"  Duration: {scene.duration:.2f}s")
                print()
        else:
            print("Skipping audio generation.")

    except ImportError:
        print("✗ TTS library not installed")
        print("  Install with: ./venv/bin/pip install TTS")

    print()
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
