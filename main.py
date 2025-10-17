#!/usr/bin/env python3
"""
Text-to-Video Generator
Главная точка входа в приложение
"""

import sys
from pathlib import Path


def main():
    """Основная функция приложения"""
    print("=" * 50)
    print("Text2Video Generator")
    print("=" * 50)
    print()
    print("Статус: В разработке (MVP)")
    print()
    print("Для запуска используйте:")
    print("  python main.py --input script.txt --output video.mp4")
    print()
    print("Для справки:")
    print("  python main.py --help")
    print()
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
