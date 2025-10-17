# План разработки Text-to-Video Generator

## 📋 Оглавление
- [Этап 0: Подготовка окружения](#этап-0-подготовка-окружения)
- [Этап 1: Базовая структура](#этап-1-базовая-структура)
- [Этап 2: Парсинг и TTS](#этап-2-парсинг-и-tts)
- [Этап 3: Субтитры и визуалы](#этап-3-субтитры-и-визуалы)
- [Этап 4: Сборка видео](#этап-4-сборка-видео)
- [Этап 5: Конфигурация и CLI](#этап-5-конфигурация-и-cli)
- [Этап 6: Docker и финализация](#этап-6-docker-и-финализация)
- [Этап 7: Тестирование и оптимизация](#этап-7-тестирование-и-оптимизация)

---

## 🎯 Этап 0: Подготовка окружения

**Цель:** Настроить локальное окружение для разработки

**Задачи:**

### 0.1 Установка базовых инструментов
- [ ] Установить Python 3.11
- [ ] Установить FFmpeg
- [ ] Установить Docker Desktop
- [ ] Установить Git

### 0.2 Создание проекта
```bash
mkdir text2video
cd text2video
git init
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
```

### 0.3 Создание базовых файлов
- [ ] `.gitignore`
- [ ] `README.md`
- [ ] `requirements.txt` (пустой пока)
- [ ] `requirements-dev.txt`

**Критерии выполнения:**
- ✅ Python окружение активно
- ✅ FFmpeg доступен через `ffmpeg -version`
- ✅ Docker запущен
- ✅ Git репозиторий инициализирован

**Время:** 30-60 минут

---

## 🏗️ Этап 1: Базовая структура проекта

**Цель:** Создать скелет проекта с пустыми модулями

**Задачи:**

### 1.1 Создать структуру директорий
```bash
mkdir -p modules utils assets/{images,music,fonts} output temp logs tests
touch modules/__init__.py utils/__init__.py tests/__init__.py
```

### 1.2 Создать файлы модулей (пустые классы)
- [ ] `modules/scene_parser.py` - класс `SceneParser`
- [ ] `modules/tts_generator.py` - класс `TTSGenerator`
- [ ] `modules/subtitle_generator.py` - класс `SubtitleGenerator`
- [ ] `modules/visual_selector.py` - класс `VisualSelector`
- [ ] `modules/music_selector.py` - класс `MusicSelector`
- [ ] `modules/video_assembler.py` - класс `VideoAssembler`

### 1.3 Создать утилиты
- [ ] `utils/logger.py` - функция `setup_logger()`
- [ ] `utils/validators.py` - валидация путей, файлов
- [ ] `utils/file_handlers.py` - чтение/запись файлов

### 1.4 Создать main.py
```python
# main.py - базовая структура
def main():
    print("Text2Video Generator")
    # TODO: добавить логику

if __name__ == "__main__":
    main()
```

### 1.5 Создать базовый config.yaml
```yaml
# config.yaml - минимальная версия
project:
  name: "Text2Video"
  output_dir: "./output"

tts:
  language: "ru"
  
video:
  fps: 30
  resolution:
    width: 1920
    height: 1080
```

**Критерии выполнения:**
- ✅ Все директории созданы
- ✅ Все модули импортируются без ошибок
- ✅ `python main.py` выполняется без ошибок

**Время:** 30 минут

---

## 🔤 Этап 2: Парсинг текста и генерация речи

**Цель:** Реализовать чтение текста и генерацию озвучки

**Задачи:**

### 2.1 Установить зависимости
```bash
pip install TTS PyYAML
```

Обновить `requirements.txt`:
```txt
TTS==0.22.0
PyYAML==6.0.1
```

### 2.2 Реализовать SceneParser

**Файл:** `modules/scene_parser.py`

**Функционал:**
- [ ] Метод `parse(file_path: str) -> List[Scene]`
- [ ] Чтение .txt и .md файлов
- [ ] Разделение по абзацам (`\n\n`)
- [ ] Очистка текста (лишние пробелы, спецсимволы)
- [ ] Создание объектов Scene

**Структура данных:**
```python
from dataclasses import dataclass

@dataclass
class Scene:
    id: int
    text: str
    duration: float = 0.0
    audio_path: str = None
    subtitle_path: str = None
    image_path: str = None
```

**Тесты:**
- [ ] Парсинг простого текста из 3 абзацев
- [ ] Обработка пустых строк
- [ ] Обработка спецсимволов

### 2.3 Реализовать TTSGenerator

**Файл:** `modules/tts_generator.py`

**Функционал:**
- [ ] Инициализация Coqui TTS с русской моделью
- [ ] Метод `generate(scene: Scene, output_dir: str) -> str`
- [ ] Генерация WAV файлов
- [ ] Расчет длительности аудио
- [ ] Кэширование (опционально на потом)

**Модели:**
```python
MODELS = {
    "ru": "tts_models/ru/ruslan/fairseq_vits",
    "en": "tts_models/en/ljspeech/tacotron2-DDC"
}
```

**Тесты:**
- [ ] Генерация аудио из короткого текста (1 предложение)
- [ ] Проверка формата файла (WAV)
- [ ] Проверка длительности

### 2.4 Интеграция в main.py

```python
# main.py
from modules.scene_parser import SceneParser
from modules.tts_generator import TTSGenerator
import yaml

def main():
    # Загрузка конфига
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Парсинг текста
    parser = SceneParser()
    scenes = parser.parse('input/test_script.txt')
    print(f"Найдено сцен: {len(scenes)}")
    
    # Генерация речи
    tts = TTSGenerator(config)
    for scene in scenes:
        audio_path = tts.generate(scene, output_dir='temp')
        scene.audio_path = audio_path
        print(f"Сцена {scene.id}: аудио создано - {audio_path}")

if __name__ == "__main__":
    main()
```

### 2.5 Создать тестовый скрипт

**Файл:** `input/test_script.txt`
```txt
Добро пожаловать в мир автоматизации!
Эта система превращает текст в видео.

Вторая сцена нашего теста.
Озвучка генерируется автоматически.

Финальная сцена.
Все работает отлично!
```

**Критерии выполнения:**
- ✅ `python main.py` парсит текст и создает аудио файлы
- ✅ В папке `temp/` появляются WAV файлы
- ✅ Консоль выводит прогресс

**Время:** 2-3 часа

---

## 📝 Этап 3: Субтитры и визуальный ряд

**Цель:** Добавить генерацию субтитров и выбор изображений

**Задачи:**

### 3.1 Установить зависимости
```bash
pip install pysrt Pillow
```

### 3.2 Реализовать SubtitleGenerator

**Файл:** `modules/subtitle_generator.py`

**Функционал:**
- [ ] Метод `generate(scene: Scene) -> str`
- [ ] Разбивка текста на строки (макс 40 символов)
- [ ] Расчет таймингов на основе длительности аудио
- [ ] Создание SRT файлов

**Алгоритм таймингов:**
```python
def calculate_timings(text: str, duration: float, max_chars: int):
    words = text.split()
    time_per_word = duration / len(words)
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    timings = []
    current_time = 0.0
    for line in lines:
        word_count = len(line.split())
        line_duration = word_count * time_per_word
        start = current_time
        end = current_time + line_duration
        timings.append((start, end, line))
        current_time = end
    
    return timings
```

**Тесты:**
- [ ] Генерация SRT для короткого текста
- [ ] Проверка формата SRT
- [ ] Проверка таймингов (start < end)

### 3.3 Реализовать VisualSelector

**Файл:** `modules/visual_selector.py`

**Функционал:**
- [ ] Метод `select_image(scene: Scene, images_dir: str) -> str`
- [ ] Рандомный выбор изображения из папки
- [ ] Метод `scale_image(image_path: str, resolution: tuple) -> str`
- [ ] Масштабирование под 1920x1080 (crop to fit)

**Масштабирование:**
```python
from PIL import Image

def scale_image(image_path: str, target_width: int, target_height: int):
    img = Image.open(image_path)
    
    # Вычисляем соотношения
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height
    
    if img_ratio > target_ratio:
        # Изображение шире - обрезаем по бокам
        new_height = target_height
        new_width = int(target_height * img_ratio)
    else:
        # Изображение выше - обрезаем сверху/снизу
        new_width = target_width
        new_height = int(target_width / img_ratio)
    
    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Обрезка по центру
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    
    img = img.crop((left, top, right, bottom))
    
    output_path = image_path.replace('.jpg', '_scaled.jpg')
    img.save(output_path)
    return output_path
```

**Тесты:**
- [ ] Выбор случайного изображения
- [ ] Масштабирование под 1920x1080
- [ ] Проверка размеров выходного изображения

### 3.4 Подготовить тестовые ресурсы

- [ ] Добавить 5-10 изображений в `assets/images/`
    - Скачать бесплатные с Unsplash/Pexels
    - Разные пропорции (горизонтальные, вертикальные, квадратные)

### 3.5 Интеграция в main.py

```python
# Добавить после генерации аудио
from modules.subtitle_generator import SubtitleGenerator
from modules.visual_selector import VisualSelector

# В main()
subtitle_gen = SubtitleGenerator(config)
visual_selector = VisualSelector(config)

for scene in scenes:
    # Субтитры
    subtitle_path = subtitle_gen.generate(scene, output_dir='temp')
    scene.subtitle_path = subtitle_path
    
    # Изображение
    image_path = visual_selector.select_image(scene, 'assets/images')
    scene.image_path = image_path
    
    print(f"Сцена {scene.id}: субтитры и изображение готовы")
```

**Критерии выполнения:**
- ✅ Генерируются SRT файлы с корректными таймингами
- ✅ Изображения масштабируются под 1920x1080
- ✅ Все данные сцены заполнены (audio, subtitle, image)

**Время:** 2-3 часа

---

## 🎬 Этап 4: Сборка видео

**Цель:** Собрать все элементы в финальное видео

**Задачи:**

### 4.1 Установить зависимости
```bash
pip install moviepy pydub
```

### 4.2 Реализовать MusicSelector

**Файл:** `modules/music_selector.py`

**Функционал:**
- [ ] Метод `select_music(music_dir: str) -> str`
- [ ] Рандомный выбор трека из папки
- [ ] Метод `adjust_duration(music_path: str, target_duration: float) -> str`
- [ ] Обрезка или зацикливание музыки
- [ ] Метод `apply_fade(audio_path: str, fade_in: float, fade_out: float) -> str`

**Обработка длительности:**
```python
from pydub import AudioSegment

def adjust_duration(music_path: str, target_duration: float):
    music = AudioSegment.from_file(music_path)
    target_ms = int(target_duration * 1000)
    
    if len(music) > target_ms:
        # Обрезка
        music = music[:target_ms]
    elif len(music) < target_ms:
        # Зацикливание
        loops_needed = (target_ms // len(music)) + 1
        music = music * loops_needed
        music = music[:target_ms]
    
    output_path = 'temp/music_adjusted.mp3'
    music.export(output_path, format='mp3')
    return output_path
```

**Тесты:**
- [ ] Выбор случайной музыки
- [ ] Обрезка длинного трека
- [ ] Зацикливание короткого трека

### 4.3 Реализовать VideoAssembler

**Файл:** `modules/video_assembler.py`

**Функционал:**
- [ ] Метод `assemble(scenes: List[Scene], config: dict) -> str`
- [ ] Создание видео клипов из изображений
- [ ] Добавление аудио к клипам
- [ ] Наложение субтитров
- [ ] Конкатенация сцен
- [ ] Добавление фоновой музыки
- [ ] Экспорт финального видео

**Базовая реализация:**
```python
from moviepy.editor import *
import pysrt

class VideoAssembler:
    def __init__(self, config):
        self.config = config
    
    def assemble(self, scenes, music_path=None):
        clips = []
        
        for scene in scenes:
            # 1. Создать клип из изображения
            image_clip = ImageClip(scene.image_path).set_duration(scene.duration)
            
            # 2. Добавить аудио
            audio = AudioFileClip(scene.audio_path)
            image_clip = image_clip.set_audio(audio)
            
            # 3. Добавить субтитры
            if scene.subtitle_path:
                subtitle_clip = self._create_subtitle_clip(
                    scene.subtitle_path, 
                    scene.duration
                )
                image_clip = CompositeVideoClip([image_clip, subtitle_clip])
            
            clips.append(image_clip)
        
        # 4. Конкатенация всех клипов
        final_video = concatenate_videoclips(clips, method="compose")
        
        # 5. Добавить фоновую музыку
        if music_path and self.config['audio']['music']['enabled']:
            music = AudioFileClip(music_path).volumex(
                self.config['audio']['music']['volume']
            )
            final_audio = CompositeAudioClip([final_video.audio, music])
            final_video = final_video.set_audio(final_audio)
        
        # 6. Экспорт
        output_path = self.config['project']['output_dir'] + '/video.mp4'
        final_video.write_videofile(
            output_path,
            fps=self.config['video']['fps'],
            codec=self.config['video']['codec'],
            audio_codec='aac',
            threads=4,
            preset='medium'
        )
        
        return output_path
    
    def _create_subtitle_clip(self, subtitle_path, duration):
        """Создает клип с субтитрами"""
        subs = pysrt.open(subtitle_path)
        subtitle_clips = []
        
        for sub in subs:
            start = sub.start.ordinal / 1000.0
            end = sub.end.ordinal / 1000.0
            
            txt_clip = TextClip(
                sub.text,
                fontsize=self.config['subtitles']['font_size'],
                color=self.config['subtitles']['color'],
                font=self.config['subtitles']['font'],
                stroke_color=self.config['subtitles']['outline_color'],
                stroke_width=self.config['subtitles']['outline_width'],
                method='caption',
                size=(1600, None)  # Ширина для переноса
            )
            
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(start).set_duration(end - start)
            subtitle_clips.append(txt_clip)
        
        return CompositeVideoClip(subtitle_clips, size=(1920, 1080))
```

**Тесты:**
- [ ] Сборка видео из 1 сцены
- [ ] Сборка видео из 3 сцен
- [ ] Проверка наличия аудио
- [ ] Проверка длительности финального видео

### 4.4 Подготовить тестовые ресурсы

- [ ] Добавить 2-3 фоновых трека в `assets/music/`
    - Скачать royalty-free музыку (incompetech.com)
    - Формат: MP3
    - Длительность: 2-5 минут

### 4.5 Полная интеграция в main.py

```python
# Полный пайплайн
def main():
    # Загрузка конфига
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 1. Парсинг
    parser = SceneParser()
    scenes = parser.parse('input/test_script.txt')
    
    # 2. TTS
    tts = TTSGenerator(config)
    for scene in scenes:
        audio_path = tts.generate(scene, output_dir='temp')
        scene.audio_path = audio_path
        # Получить длительность
        from wave import open as wave_open
        with wave_open(audio_path, 'r') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            scene.duration = frames / float(rate)
    
    # 3. Субтитры
    subtitle_gen = SubtitleGenerator(config)
    for scene in scenes:
        subtitle_path = subtitle_gen.generate(scene, output_dir='temp')
        scene.subtitle_path = subtitle_path
    
    # 4. Визуалы
    visual_selector = VisualSelector(config)
    for scene in scenes:
        image_path = visual_selector.select_image(scene, 'assets/images')
        scene.image_path = image_path
    
    # 5. Музыка
    music_selector = MusicSelector(config)
    total_duration = sum(s.duration for s in scenes)
    music_path = music_selector.select_music('assets/music')
    music_path = music_selector.adjust_duration(music_path, total_duration)
    
    # 6. Сборка
    assembler = VideoAssembler(config)
    video_path = assembler.assemble(scenes, music_path)
    
    print(f"✅ Видео готово: {video_path}")
```

**Критерии выполнения:**
- ✅ Создается полноценный MP4 файл
- ✅ Видео содержит изображения, озвучку, субтитры, музыку
- ✅ Длительность соответствует сумме сцен
- ✅ Файл воспроизводится в VLC/других плеерах

**Время:** 4-5 часов

---

## ⚙️ Этап 5: Конфигурация и CLI

**Цель:** Добавить полноценную конфигурацию и CLI интерфейс

**Задачи:**

### 5.1 Расширить config.yaml

**Файл:** `config.yaml`

```yaml
project:
  name: "Text2Video Generator"
  version: "1.0.0"
  output_dir: "./output"

tts:
  language: "ru"  # ru | en
  models:
    ru: "tts_models/ru/ruslan/fairseq_vits"
    en: "tts_models/en/ljspeech/tacotron2-DDC"
  speed: 1.0
  
video:
  fps: 30
  resolution:
    width: 1920
    height: 1080
  aspect_ratio: "16:9"  # 16:9 | 9:16 | 1:1
  codec: "libx264"
  bitrate: "5000k"
  
subtitles:
  enabled: true
  font: "Arial"
  font_size: 48
  color: "white"
  outline_color: "black"
  outline_width: 2
  position: "bottom"
  max_chars_per_line: 40
  
audio:
  music:
    enabled: true
    volume: 0.2
    fade_in: 2.0
    fade_out: 3.0
  voice:
    volume: 1.0
    normalize: true
    
visuals:
  images_dir: "./assets/images"
  transition:
    enabled: false  # TODO: Этап 7
    type: "crossfade"
    duration: 0.5
    
paths:
  music_dir: "./assets/music"
  fonts_dir: "./assets/fonts"
  temp_dir: "./temp"
  
logging:
  level: "INFO"
  file: "./logs/app.log"
  console: true
```

### 5.2 Реализовать logger

**Файл:** `utils/logger.py`

```python
import logging
import os
from datetime import datetime

def setup_logger(config):
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    
    # Создать директорию для логов
    log_file = log_config.get('file', './logs/app.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Формат
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Основной логгер
    logger = logging.getLogger('text2video')
    logger.setLevel(level)
    
    # Handler для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler для консоли
    if log_config.get('console', True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger
```

### 5.3 Добавить CLI с argparse

**Обновить:** `main.py`

```python
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Text-to-Video Generator - превращает текст в видео',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  python main.py -i script.txt
  python main.py -i script.txt -o my_video.mp4
  python main.py -i script.txt --aspect-ratio 9:16 --no-music
        '''
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Путь к текстовому файлу (.txt или .md)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output/video.mp4',
        help='Имя выходного видео (по умолчанию: output/video.mp4)'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Путь к конфиг-файлу (по умолчанию: config.yaml)'
    )
    
    parser.add_argument(
        '--aspect-ratio',
        choices=['16:9', '9:16', '1:1'],
        help='Соотношение сторон видео'
    )
    
    parser.add_argument(
        '--no-music',
        action='store_true',
        help='Создать видео без фоновой музыки'
    )
    
    parser.add_argument(
        '--language',
        choices=['ru', 'en'],
        help='Язык озвучки (переопределяет config.yaml)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Уровень логирования'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Загрузить TTS модели и выйти'
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Загрузка конфига
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Файл конфигурации не найден: {args.config}")
        sys.exit(1)
    
    # Переопределение из CLI
    if args.aspect_ratio:
        config['video']['aspect_ratio'] = args.aspect_ratio
    if args.no_music:
        config['audio']['music']['enabled'] = False
    if args.language:
        config['tts']['language'] = args.language
    if args.log_level:
        config['logging']['level'] = args.log_level
    
    # Настройка логгера
    logger = setup_logger(config)
    logger.info("=" * 50)
    logger.info("Text2Video Generator запущен")
    logger.info(f"Входной файл: {args.input}")
    logger.info(f"Выходной файл: {args.output}")
    
    # Режим инициализации
    if args.init:
        logger.info("Загрузка TTS моделей...")
        from TTS.api import TTS
        for lang, model in config['tts']['models'].items():
            logger.info(f"Загрузка модели для {lang}: {model}")
            TTS(model)
        logger.info("✅ Модели загружены")
        return
    
    # Валидация
    if not os.path.exists(args.input):
        logger.error(f"Входной файл не найден: {args.input}")
        sys.exit(1)
    
    # Запуск пайплайна
    try:
        run_pipeline(args, config, logger)
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}", exc_info=True)
        sys.exit(1)

def run_pipeline(args, config, logger):
    """Основной пайплайн обработки"""
    # [Весь код из предыдущего main()]
    # Добавить logger.info() на каждом шаге
    
    logger.info("Этап 1/6: Парсинг текста...")
    # ...
    
    logger.info("Этап 2/6: Генерация озвучки...")
    # ...
    
    logger.info(f"✅ Видео готово: {args.output}")
```

**Критерии выполнения:**
- ✅ `python main.py --help` показывает справку
- ✅ CLI аргументы переопределяют config.yaml
- ✅ Логи пишутся в файл и консоль
- ✅ `--init` загружает модели

**Время:** 2 часа

---

## 🐳 Этап 6: Docker и финализация

**Цель:** Контейнеризация приложения

**Задачи:**

### 6.1 Создать Dockerfile

```dockerfile
FROM python:3.11-slim

# Метаданные
LABEL maintainer="your-email@example.com"
LABEL version="1.0.0"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Предзагрузка TTS моделей (опционально, увеличивает размер образа)
# RUN python -c "from TTS.api import TTS; TTS('tts_models/ru/ruslan/fairseq_vits'); TTS('tts_models/en/ljspeech/tacotron2-DDC')"

# Копирование кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p output temp logs input

# Точка входа
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
```

### 6.2 Создать docker-compose.yml

```yaml
version: '3.8'

services:
  text2video:
    build: .
    container_name: text2video-generator
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./assets:/app/assets
      - ./config.yaml:/app/config.yaml
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
    # Пример запуска (раскомментировать и изменить)
    # command: -i /app/input/script.txt -o /app/output/video.mp4
```

### 6.3 Создать .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Временные файлы
temp/
*.log
logs/

# Output
output/

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### 6.4 Обновить README.md

Добавить секции:
- [ ] Docker установка
- [ ] Docker использование
- [ ] Примеры команд
- [ ] Troubleshooting

### 6.5 Финальное тестирование

**Локально:**
```bash
python main.py -i input/test_script.txt -o output/test_video.mp4
```

**Docker:**
```bash
# Сборка образа
docker build -t text2video:latest .

# Запуск
docker run -v $(pwd)/input:/app/input \
           -v $(pwd)/output:/app/output \
           -v $(pwd)/assets:/app/assets \
           -v $(pwd)/config.yaml:/app/config.yaml \
           text2video:latest -i /app/input/test_script.txt
```

**Docker Compose:**
```bash
docker-compose up
```

**Критерии выполнения:**
- ✅ Docker образ успешно собирается
- ✅ Контейнер создает видео
- ✅ Volumes работают корректно
- ✅ Размер образа < 5GB

**Время:** 2-3 часа

---

## 🧪 Этап 7: Тестирование и оптимизация

**Цель:** Покрытие тестами и оптимизация производительности

**Задачи:**

### 7.1 Написать unit-тесты

**Файл:** `tests/test_scene_parser.py`

```python
import pytest
from modules.scene_parser import SceneParser

def test_parse_simple_text(tmp_path):
    # Создать временный файл
    test_file = tmp_path / "test.txt"
    test_file.write_text("Первый абзац.\n\nВторой абзац.")
    
    parser = SceneParser()
    scenes = parser.parse(str(test_file))
    
    assert len(scenes) == 2
    assert scenes[0].text == "Первый абзац."
    assert scenes[1].text == "Второй абзац."

def test_clean_text():
    parser = SceneParser()
    dirty = "  Текст   с    лишними    пробелами  "
    clean = parser.clean_text(dirty)
    assert clean == "Текст с лишними пробелами"
```

**Аналогично для других модулей:**
- [ ] `tests/test_tts_generator.py`
- [ ] `tests/test_subtitle_generator.py`
- [ ] `tests/test_visual_selector.py`
- [ ] `tests/test_video_assembler.py`

### 7.2 Добавить интеграционные тесты

**Файл:** `tests/test_integration.py`

```python
def test_full_pipeline(tmp_path):
    """Тест полного пайплайна от текста до видео"""
    # Создать тестовый сценарий
    script = tmp_path / "script.txt"
    script.write_text("Тестовая сцена для проверки.")
    
    # Запустить пайплайн
    output = tmp_path / "video.mp4"
    # ... run_pipeline()
    
    # Проверки
    assert output.exists()
    assert output.stat().st_size > 0
```

### 7.3 Оптимизация производительности

**Кэширование TTS:**
```python
import hashlib
import os

class CachedTTSGenerator(TTSGenerator):
    def __init__(self, config, cache_dir='./cache'):
        super().__init__(config)
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def generate(self, scene, output_dir):
        # Создать хеш текста
        cache_key = hashlib.md5(
            f"{scene.text}_{self.language}".encode()
        ).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.wav")
        
        # Проверить кэш
        if os.path.exists(cache_path):
            self.logger.info(f"Используется кэш для сцены {scene.id}")
            return cache_path
        
        # Генерация
        audio_path = super().generate(scene, output_dir)
        
        # Сохранить в кэш
        shutil.copy(audio_path, cache_path)
        
        return audio_path
```

**Профилирование:**
```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} выполнена за {end - start:.2f} сек")
        return result
    return wrapper

# Применить к методам
@timing_decorator
def generate(self, scene, output_dir):
    ...
```

### 7.4 Добавить прогресс-бар

```bash
pip install tqdm
```

```python
from tqdm import tqdm

# В run_pipeline()
for scene in tqdm(scenes, desc="Генерация озвучки"):
    audio_path = tts.generate(scene, output_dir='temp')
    scene.audio_path = audio_path
```

### 7.5 Обработка ошибок

**Создать:** `utils/exceptions.py`

```python
class Text2VideoException(Exception):
    """Базовое исключение"""
    pass

class SceneParseError(Text2VideoException):
    """Ошибка парсинга сцен"""
    pass

class TTSError(Text2VideoException):
    """Ошибка генерации речи"""
    pass

class VideoAssemblyError(Text2VideoException):
    """Ошибка сборки видео"""
    pass
```

**Использование:**
```python
try:
    scenes = parser.parse(input_file)
except Exception as e:
    raise SceneParseError(f"Не удалось распарсить файл: {e}")
```

**Критерии выполнения:**
- ✅ Покрытие тестами > 70%
- ✅ Все тесты проходят
- ✅ Добавлено кэширование TTS
- ✅ Добавлен прогресс-бар
- ✅ Обработка всех критичных ошибок

**Время:** 3-4 часа

---

## 📊 Общая оценка времени

| Этап | Описание | Время |
|------|----------|-------|
| 0 | Подготовка окружения | 0.5-1 ч |
| 1 | Базовая структура | 0.5 ч |
| 2 | Парсинг и TTS | 2-3 ч |
| 3 | Субтитры и визуалы | 2-3 ч |
| 4 | Сборка видео | 4-5 ч |
| 5 | Конфигурация и CLI | 2 ч |
| 6 | Docker | 2-3 ч |
| 7 | Тестирование | 3-4 ч |
| **ИТОГО** | | **16-22 часа** |

---

## ✅ Чек-лист финальной версии

### Функционал
- [ ] Парсинг текста из .txt/.md файлов
- [ ] Генерация речи на русском и английском
- [ ] Автоматические субтитры с таймингами
- [ ] Статичные изображения как фоны
- [ ] Фоновая музыка
- [ ] Сборка финального видео
- [ ] CLI интерфейс
- [ ] Конфигурация через YAML
- [ ] Логирование

### Качество кода
- [ ] Модульная архитектура
- [ ] Типизация (type hints)
- [ ] Docstrings для классов/методов
- [ ] Обработка ошибок
- [ ] Unit-тесты
- [ ] Интеграционные тесты

### Документация
- [ ] README.md с примерами
- [ ] Комментарии в коде
- [ ] Примеры конфигов
- [ ] Troubleshooting guide

### Деплой
- [ ] requirements.txt актуален
- [ ] Dockerfile работает
- [ ] docker-compose.yml настроен
- [ ] .dockerignore создан
- [ ] .gitignore создан

### Тестирование
- [ ] Локальный запуск работает
- [ ] Docker контейнер работает
- [ ] Тестовое видео создается корректно
- [ ] Все форматы видео (16:9, 9:16, 1:1) работают
- [ ] Оба языка (ru, en) работают

---

## 🚀 Следующие шаги (после MVP)

### Улучшения
1. **Переходы между сценами**
    - Crossfade
    - Fade to black
    - Slide transitions

2. **Эффект Кена Бёрнса**
    - Zoom in/out
    - Pan left/right

3. **Анализ тона текста**
    - Определение настроения
    - Автоподбор музыки по эмоции

4. **Интро/аутро**
    - Шаблоны начала/конца
    - Анимированный текст

5. **Web-интерфейс**
    - Flask/FastAPI
    - Простая форма загрузки
    - Отображение прогресса

6. **API для интеграций**
    - REST API
    - Webhook уведомления

7. **Пакетная обработка**
    - Генерация серии видео
    - Автоматизация из CSV

---

## 📝
