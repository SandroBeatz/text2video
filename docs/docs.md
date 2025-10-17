# Text-to-Video Generator - Документация

## 📋 Содержание
- [Обзор проекта](#обзор-проекта)
- [Системные требования](#системные-требования)
- [Установка и настройка](#установка-и-настройка)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)

---

## 🎯 Обзор проекта

**Text-to-Video Generator** — автоматизированная система для создания видеороликов из текстовых сценариев с использованием:
- Локальной генерации речи (Coqui TTS)
- Автоматических субтитров
- Статичных изображений в качестве фона
- Фоновой музыки
- Сборки через MoviePy/FFmpeg

### Основные возможности
✅ Преобразование текста в озвучку  
✅ Автоматическая синхронизация субтитров  
✅ Поддержка различных форматов видео (16:9, 9:16, 1:1)  
✅ Настройка через YAML конфигурацию  
✅ CLI интерфейс

---

## 💻 Системные требования

### Минимальные требования
- **OS**: Linux / macOS / Windows 10+
- **Python**: 3.9+
- **RAM**: 4 GB (рекомендуется 8 GB)
- **Disk**: 2 GB свободного места
- **FFmpeg**: установлен и доступен в PATH

### Зависимости Python
```txt
TTS>=0.22.0           # Coqui TTS для генерации речи
moviepy>=1.0.3        # Видеомонтаж
pydub>=0.25.1         # Обработка аудио
pysrt>=1.1.2          # Работа с субтитрами
PyYAML>=6.0           # Парсинг конфигурации
argparse              # CLI (входит в стандартную библиотеку)
Pillow>=10.0.0        # Обработка изображений
numpy>=1.24.0         # Численные операции
```

---

## 🚀 Установка и настройка

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/text2video.git
cd text2video
```

### 2. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Установка FFmpeg
**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Скачать с [ffmpeg.org](https://ffmpeg.org/download.html) и добавить в PATH

### 5. Загрузка моделей TTS
```bash
# Первый запуск автоматически скачает модели
python main.py --init
```

### 6. Подготовка ресурсов
```bash
# Создать директории для медиа
mkdir -p assets/images assets/music output

# Добавить фоновые изображения в assets/images/
# Добавить музыку в assets/music/
```

---

## 🏗️ Архитектура

### Структура проекта
```
text2video/
│
├── main.py                 # Точка входа
├── config.yaml             # Конфигурация
├── requirements.txt        # Зависимости Python
├── README.md              # Основная документация
│
├── modules/               # Основные модули
│   ├── __init__.py
│   ├── scene_parser.py       # Парсинг текста на сцены
│   ├── tts_generator.py      # Генерация озвучки
│   ├── subtitle_generator.py # Создание субтитров
│   ├── visual_selector.py    # Выбор изображений
│   ├── music_selector.py     # Подбор музыки
│   └── video_assembler.py    # Финальная сборка
│
├── utils/                 # Вспомогательные утилиты
│   ├── __init__.py
│   ├── logger.py            # Логирование
│   ├── validators.py        # Валидация входных данных
│   └── file_handlers.py     # Работа с файлами
│
├── assets/               # Медиа-ресурсы
│   ├── images/             # Фоновые изображения
│   │   ├── default_bg.jpg
│   │   └── ...
│   ├── music/              # Фоновая музыка
│   │   ├── ambient_01.mp3
│   │   └── ...
│   └── fonts/              # Шрифты для субтитров
│       └── Arial.ttf
│
├── templates/            # Шаблоны стилей
│   └── subtitle_styles.yaml
│
├── tests/               # Тесты
│   ├── __init__.py
│   ├── test_scene_parser.py
│   └── ...
│
└── output/              # Сгенерированные видео
    └── .gitkeep
```

### Диаграмма потока данных

```
[Текст] → SceneParser → [Список сцен]
                             ↓
                     TTSGenerator → [Аудио файлы]
                             ↓
                   SubtitleGenerator → [SRT файлы]
                             ↓
                     VisualSelector → [Изображения]
                             ↓
                     MusicSelector → [Музыкальный трек]
                             ↓
                     VideoAssembler → [Финальное видео]
```

### Пайплайн обработки

1. **Парсинг** (`scene_parser.py`)
    - Читает входной текст
    - Разделяет на сцены по абзацам
    - Очищает и нормализует текст

2. **Генерация речи** (`tts_generator.py`)
    - Использует Coqui TTS локально
    - Создает аудио для каждой сцены
    - Сохраняет метаданные (длительность)

3. **Субтитры** (`subtitle_generator.py`)
    - Рассчитывает тайминги на основе аудио
    - Генерирует SRT файлы
    - Применяет стили из шаблонов

4. **Визуальный ряд** (`visual_selector.py`)
    - Выбирает изображения (рандомно или по ключевым словам)
    - Масштабирует под нужный формат (16:9, 9:16, 1:1)

5. **Музыка** (`music_selector.py`)
    - Выбирает трек из библиотеки
    - Подрезает/зацикливает под длительность видео
    - Микширует с речью

6. **Сборка** (`video_assembler.py`)
    - Композитинг всех элементов
    - Применение переходов между сценами
    - Экспорт финального MP4

---

## ⚡ Быстрый старт

### Базовое использование

```bash
# Создать видео из текстового файла
python main.py --input script.txt --output my_video.mp4

# С кастомной конфигурацией
python main.py -i script.txt -o video.mp4 -c custom_config.yaml

# Указать формат видео
python main.py -i script.txt --aspect-ratio 9:16
```

### Пример текстового сценария (`script.txt`)

```
Добро пожаловать в мир автоматизации создания видео! 
Эта система позволяет превратить любой текст в полноценный видеоролик.

Второй абзац становится второй сценой.
Каждая сцена получает свою озвучку и визуальное оформление.

Наслаждайтесь результатом!
```

### Параметры командной строки

```
usage: main.py [-h] -i INPUT [-o OUTPUT] [-c CONFIG] 
               [--aspect-ratio RATIO] [--no-music] [--voice VOICE]

Аргументы:
  -i, --input INPUT          Путь к текстовому файлу (обязательно)
  -o, --output OUTPUT        Имя выходного видео (по умолчанию: output/video.mp4)
  -c, --config CONFIG        Путь к конфиг-файлу (по умолчанию: config.yaml)
  --aspect-ratio RATIO       Соотношение сторон: 16:9, 9:16, 1:1 (по умолчанию: 16:9)
  --no-music                 Создать видео без фоновой музыки
  --voice VOICE              ID голосовой модели TTS
  --log-level LEVEL          Уровень логирования: DEBUG, INFO, WARNING, ERROR
```

---

## ⚙️ Конфигурация

### config.yaml - основной файл настроек

```yaml
# Общие настройки проекта
project:
  name: "Text2Video Generator"
  version: "1.0.0"
  output_dir: "./output"

# Настройки TTS
tts:
  model: "tts_models/ru/ruslan/fairseq_vits"  # Модель Coqui TTS
  language: "ru"
  speaker: null  # Для мультиголосовых моделей
  speed: 1.0     # Скорость речи (0.5 - 2.0)
  
# Настройки видео
video:
  fps: 30
  resolution:
    width: 1920
    height: 1080
  aspect_ratio: "16:9"  # 16:9, 9:16, 1:1
  codec: "libx264"
  bitrate: "5000k"
  
# Настройки субтитров
subtitles:
  enabled: true
  font: "Arial"
  font_size: 48
  color: "white"
  outline_color: "black"
  outline_width: 2
  position: "bottom"  # top, center, bottom
  max_chars_per_line: 40
  
# Настройки аудио
audio:
  music:
    enabled: true
    volume: 0.2        # Громкость музыки относительно речи
    fade_in: 2.0       # Плавное появление (сек)
    fade_out: 3.0      # Плавное затухание (сек)
  voice:
    volume: 1.0
    normalize: true    # Нормализация громкости
    
# Настройки визуального ряда
visuals:
  images_dir: "./assets/images"
  default_duration: 5  # Длительность показа изображения (сек) если нет речи
  transition:
    enabled: true
    type: "crossfade"  # crossfade, fade, none
    duration: 0.5      # Длительность перехода (сек)
    
# Пути к ресурсам
paths:
  music_dir: "./assets/music"
  fonts_dir: "./assets/fonts"
  temp_dir: "./temp"
  
# Логирование
logging:
  level: "INFO"       # DEBUG, INFO, WARNING, ERROR
  file: "./logs/app.log"
  console: true
```

### Переменные окружения (.env)

```env
# Опционально: API ключи для будущих интеграций
# OPENAI_API_KEY=your_key_here
# ELEVENLABS_API_KEY=your_key_here

# Пути (если нужно переопределить)
OUTPUT_DIR=./output
ASSETS_DIR=./assets
```

---

## 📚 Дополнительные документы

- [Архитектура компонентов](./docs/architecture.md)
- [API модулей](./docs/api.md)
- [Рекомендации по стеку](./docs/stack_recommendations.md)
- [Частые проблемы и решения](./docs/troubleshooting.md)
- [Примеры использования](./docs/examples.md)

---

## 🤝 Вклад в проект

Pull requests приветствуются! Для крупных изменений сначала откройте issue для обсуждения.

## 📄 Лицензия

MIT License - используйте свободно!
