# Text-to-Video Generator

Автоматизированная система для создания видеороликов из текстовых сценариев с использованием локальной генерации речи, автоматических субтитров и фоновой музыки.

## 🎯 Возможности

- ✅ Преобразование текста в озвучку (Coqui TTS)
- ✅ Автоматическая синхронизация субтитров
- ✅ Поддержка различных форматов видео (16:9, 9:16, 1:1)
- ✅ Фоновая музыка с регулировкой громкости
- ✅ Настройка через YAML конфигурацию
- ✅ CLI интерфейс

## 🚀 Быстрый старт

### Требования

- Python 3.9+
- FFmpeg (установлен и доступен в PATH)
- 4-8 GB RAM

### Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd text2video

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установить зависимости
pip install -r requirements.txt

# Проверить установку FFmpeg
ffmpeg -version
```

### Использование

```bash
# Базовое использование
python main.py --input script.txt --output video.mp4

# С кастомной конфигурацией
python main.py -i script.txt -o video.mp4 -c config.yaml

# Указать формат видео
python main.py -i script.txt --aspect-ratio 9:16

# Без фоновой музыки
python main.py -i script.txt --no-music

# Выбрать язык озвучки
python main.py -i script.txt --language en
```

## 📁 Структура проекта

```
text2video/
├── main.py                 # Точка входа
├── config.yaml             # Конфигурация
├── requirements.txt        # Зависимости
├── modules/                # Основные модули
│   ├── scene_parser.py     # Парсинг текста
│   ├── tts_generator.py    # Генерация речи
│   ├── subtitle_generator.py # Субтитры
│   ├── visual_selector.py  # Выбор изображений
│   ├── music_selector.py   # Выбор музыки
│   └── video_assembler.py  # Сборка видео
├── utils/                  # Утилиты
├── assets/                 # Медиа-ресурсы
│   ├── images/            # Фоновые изображения
│   ├── music/             # Фоновая музыка
│   └── fonts/             # Шрифты
├── output/                # Сгенерированные видео
├── temp/                  # Временные файлы
└── tests/                 # Тесты

```

## 🎬 Пример сценария

Создайте файл `script.txt`:

```
Добро пожаловать в мир автоматизации создания видео!
Эта система позволяет превратить любой текст в полноценный видеоролик.

Второй абзац становится второй сценой.
Каждая сцена получает свою озвучку и визуальное оформление.

Наслаждайтесь результатом!
```

Каждый абзац, разделённый пустой строкой, становится отдельной сценой в видео.

## ⚙️ Конфигурация

Основные настройки в `config.yaml`:

```yaml
# Настройки TTS
tts:
  language: "ru"  # ru | en
  speed: 1.0

# Настройки видео
video:
  fps: 30
  aspect_ratio: "16:9"  # 16:9 | 9:16 | 1:1
  resolution:
    width: 1920
    height: 1080

# Настройки субтитров
subtitles:
  enabled: true
  font_size: 48
  color: "white"
  max_chars_per_line: 40

# Настройки аудио
audio:
  music:
    enabled: true
    volume: 0.2  # Громкость относительно речи
```

## 🧪 Разработка

```bash
# Установить dev зависимости
pip install -r requirements-dev.txt

# Запустить тесты
pytest

# Запустить тесты с coverage
pytest --cov=modules --cov=utils tests/

# Форматирование кода
black .

# Проверка кода
flake8 .
```

## 📚 Документация

Подробная документация доступна в:
- [Архитектура](docs/architecture.md)
- [Полная документация](docs/docs.md)
- [План разработки](docs/plan.md)
- [CLAUDE.md](CLAUDE.md) - гайд для AI ассистентов

## 🤝 Участие в проекте

Pull requests приветствуются! Для крупных изменений сначала откройте issue для обсуждения.

## 📄 Лицензия

MIT License

## 🛠️ Статус разработки

**Текущий статус:** 🚧 В разработке (MVP)

Отслеживайте прогресс в [TASKS.md](TASKS.md)
