# Архитектура Text-to-Video Generator

## 🏛️ Общая архитектура

### Принципы дизайна

1. **Модульность** - каждый компонент независим и взаимозаменяем
2. **Расширяемость** - легко добавить новые TTS провайдеры, форматы, стили
3. **Отказоустойчивость** - обработка ошибок на каждом этапе с fallback
4. **Производительность** - асинхронная обработка где возможно
5. **Простота** - минимум зависимостей, чистый код

---

## 📦 Детальное описание модулей

### 1. `main.py` - Точка входа

**Ответственность:**
- Парсинг аргументов командной строки
- Загрузка конфигурации
- Инициализация логгера
- Оркестрация пайплайна
- Обработка ошибок верхнего уровня

**Основной флоу:**
```python
def main():
    # 1. Парсинг CLI аргументов
    args = parse_arguments()
    
    # 2. Загрузка конфигурации
    config = load_config(args.config)
    
    # 3. Инициализация логгера
    logger = setup_logger(config)
    
    # 4. Валидация входных данных
    validate_input(args.input, config)
    
    # 5. Запуск пайплайна
    pipeline = Pipeline(config)
    video_path = pipeline.run(args.input, args.output)
    
    # 6. Финализация
    logger.info(f"✅ Видео создано: {video_path}")
```

---

### 2. `modules/scene_parser.py` - Парсер сцен

**Ответственность:**
- Чтение текстовых файлов (.txt, .md)
- Разделение на сцены по абзацам
- Очистка и нормализация текста
- Извлечение метаданных (опционально)

**Ключевые методы:**
```python
class SceneParser:
    def parse(self, file_path: str) -> List[Scene]:
        """Парсит файл и возвращает список сцен"""
        
    def split_into_scenes(self, text: str) -> List[str]:
        """Разделяет текст на сцены"""
        
    def clean_text(self, text: str) -> str:
        """Убирает лишние пробелы, спецсимволы"""
        
    def extract_metadata(self, text: str) -> dict:
        """Ищет метаданные в комментариях (опционально)"""
```

**Структура Scene:**
```python
@dataclass
class Scene:
    id: int
    text: str
    duration: float = 0.0
    image_path: str = None
    audio_path: str = None
    metadata: dict = field(default_factory=dict)
```

**Особенности:**
- Игнорирует пустые абзацы
- Поддержка маркдаун разметки (заголовки как метаданные)
- Обработка Unicode корректно
- Ограничение на максимальную длину сцены (для предотвращения слишком длинных аудио)

---

### 3. `modules/tts_generator.py` - Генератор речи

**Ответственность:**
- Инициализация Coqui TTS
- Генерация аудио из текста
- Сохранение WAV файлов
- Расчет длительности

**Ключевые методы:**
```python
class TTSGenerator:
    def __init__(self, config: dict):
        """Инициализирует модель TTS"""
        self.tts = TTS(model_name=config['tts']['model'])
        
    def generate(self, scene: Scene, output_dir: str) -> str:
        """Генерирует аудио для сцены, возвращает путь к файлу"""
        
    def get_audio_duration(self, audio_path: str) -> float:
        """Возвращает длительность аудио в секундах"""
        
    def batch_generate(self, scenes: List[Scene]) -> None:
        """Генерирует аудио для списка сцен"""
```

**Важные аспекты:**

1. **Кэширование:**
```python
# Хеш текста + конфиг модели = уникальный ID
cache_key = hashlib.md5(f"{text}_{model}_{speed}".encode()).hexdigest()
if cache_key in cache:
    return cache[cache_key]
```

2. **Обработка ошибок:**
- Fallback на более простую модель при OOM
- Разделение длинных текстов на части
- Retry механизм при временных сбоях

3. **Оптимизация:**
- Lazy загрузка моделей
- Batch обработка если модель поддерживает
- Использование GPU если доступен

---

### 4. `modules/subtitle_generator.py` - Генератор субтитров

**Ответственность:**
- Создание SRT файлов
- Синхронизация с аудио
- Разбивка на строки по длине
- Применение стилей

**Ключевые методы:**
```python
class SubtitleGenerator:
    def generate(self, scene: Scene) -> str:
        """Создает SRT файл для сцены"""
        
    def split_into_lines(self, text: str, max_chars: int) -> List[str]:
        """Разбивает текст на строки для субтитров"""
        
    def calculate_timings(self, text: str, audio_duration: float) -> List[Tuple]:
        """Рассчитывает тайминги для каждой строки"""
        
    def apply_style(self, srt_path: str, style: dict) -> str:
        """Применяет стиль к субтитрам (для ASS формата)"""
```

**Алгоритм расчета таймингов:**
```python
def calculate_timings(text: str, duration: float):
    words = text.split()
    time_per_word = duration / len(words)
    
    lines = split_into_lines(text, max_chars=40)
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

**Формат SRT:**
```
1
00:00:00,000 --> 00:00:03,500
Первая строка субтитров

2
00:00:03,500 --> 00:00:07,000
Вторая строка субтитров
```

---

### 5. `modules/visual_selector.py` - Селектор визуального ряда

**Ответственность:**
- Выбор изображений для сцен
- Масштабирование под формат видео
- Применение эффектов (опционально)

**Ключевые методы:**
```python
class VisualSelector:
    def select_image(self, scene: Scene, images_dir: str) -> str:
        """Выбирает изображение для сцены"""
        
    def scale_image(self, image_path: str, target_resolution: tuple) -> str:
        """Масштабирует изображение под разрешение видео"""
        
    def apply_ken_burns(self, image_path: str, duration: float) -> str:
        """Применяет эффект Кена Бёрнса (zoom/pan) - опционально"""
```

**Стратегии выбора изображений:**

1. **Рандомный выбор** (по умолчанию):
```python
images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png'))]
return random.choice(images)
```

2. **По ключевым словам** (опционально):
```python
keywords = extract_keywords(scene.text)
matching_images = find_images_by_keywords(images_dir, keywords)
return matching_images[0] if matching_images else fallback_image
```

3. **По метаданным** (если указаны в тексте):
```python
# [image: sunset.jpg]
if 'image' in scene.metadata:
    return scene.metadata['image']
```

**Масштабирование:**
- Crop to fit (обрезка по центру)
- Letterbox (черные полосы)
- Stretch (растяжение)

---

### 6. `modules/music_selector.py` - Селектор музыки

**Ответственность:**
- Выбор фоновой музыки
- Подрезка/зацикливание под длину видео
- Микширование с речью
- Fade in/out эффекты

**Ключевые методы:**
```python
class MusicSelector:
    def select_music(self, total_duration: float, mood: str = None) -> str:
        """Выбирает музыкальный трек"""
        
    def adjust_duration(self, music_path: str, target_duration: float) -> str:
        """Подрезает или зацикливает музыку"""
        
    def mix_with_voice(self, music_path: str, voice_path: str, 
                       music_volume: float) -> str:
        """Микширует музыку с голосом"""
```

**Анализ настроения (опционально):**
```python
def detect_mood(text: str) -> str:
    """Простой анализ эмоционального тона"""
    positive_words = ['радость', 'счастье', 'успех']
    negative_words = ['грусть', 'проблема', 'беда']
    
    pos_count = sum(word in text.lower() for word in positive_words)
    neg_count = sum(word in text.lower() for word in negative_words)
    
    if pos_count > neg_count:
        return 'uplifting'
    elif neg_count > pos_count:
        return 'melancholic'
    else:
        return 'neutral'
```

---

### 7. `modules/video_assembler.py` - Сборщик видео

**Ответственность:**
- Композитинг всех элементов
- Применение переходов между сценами
- Рендеринг финального видео
- Оптимизация кодирования

**Ключевые методы:**
```python
class VideoAssembler:
    def assemble(self, scenes: List[Scene], config: dict) -> str:
        """Собирает финальное видео"""
        
    def create_scene_clip(self, scene: Scene) -> VideoClip:
        """Создает клип для одной сцены"""
        
    def apply_transition(self, clip1: VideoClip, clip2: VideoClip) -> VideoClip:
        """Применяет переход между клипами"""
        
    def add_background_music(self, video: VideoClip, music_path: str) -> VideoClip:
        """Добавляет фоновую музыку"""
```

**Пайплайн сборки:**
```python
def assemble(scenes, config):
    clips = []
    
    # 1. Создание клипов для каждой сцены
    for scene in scenes:
        # Фон (изображение)
        bg = ImageClip(scene.image_path).set_duration(scene.duration)
        
        # Аудио (озвучка)
        audio = AudioFileClip(scene.audio_path)
        
        # Субтитры
        subtitles = SubtitlesClip(scene.subtitle_path, 
                                   generator=lambda txt: TextClip(txt, ...))
        
        # Композиция
        clip = CompositeVideoClip([bg, subtitles.set_position(('center', 'bottom'))])
        clip = clip.set_audio(audio)
        
        clips.append(clip)
    
    # 2. Применение переходов
    clips_with_transitions = []
    for i in range(len(clips) - 1):
        clips_with_transitions.append(clips[i])
        transition = crossfadein(clips[i+1], duration=0.5)
        clips_with_transitions.append(transition)
    
    # 3. Конкатенация
    final = concatenate_videoclips(clips_with_transitions)
    
    # 4. Фоновая музыка
    if config['audio']['music']['enabled']:
        music = AudioFileClip(music_path).volumex(0.2)
        final_audio = CompositeAudioClip([final.audio, music])
        final = final.set_audio(final_audio)
    
    # 5. Рендеринг
    final.write_videofile(output_path, 
                          fps=config['video']['fps'],
                          codec=config['video']['codec'])
    
    return output_path
```

---

## 🔄 Поток данных через систему

```
1. INPUT: script.txt
   └─> SceneParser
       └─> [Scene 1, Scene 2, Scene 3]

2. TTSGenerator
   Scene 1 → audio_scene1.wav (duration: 5.2s)
   Scene 2 → audio_scene2.wav (duration: 7.8s)
   Scene 3 → audio_scene3.wav (duration: 4.1s)

3. SubtitleGenerator
   audio_scene1.wav + Scene 1.text → subtitles_scene1.srt
   audio_scene2.wav + Scene 2.text → subtitles_scene2.srt
   audio_scene3.wav + Scene 3.text → subtitles_scene3.srt

4. VisualSelector
   Scene 1 → assets/images/bg_001.jpg
   Scene 2 → assets/images/bg_045.jpg
   Scene 3 → assets/images/bg_012.jpg

5. MusicSelector
   total_duration: 17.1s → assets/music/ambient_03.mp3 (adjusted)

6. VideoAssembler
   [clips] + [transitions] + [music] → output/final_video.mp4
```

---

## 🛡️ Обработка ошибок

### Стратегия по уровням

**Уровень модуля:**
```python
class TTSGenerator:
    def generate(self, scene: Scene):
        try:
            return self._generate_internal(scene)
        except OutOfMemoryError:
            # Fallback: разделить текст на части
            return self._generate_in_chunks(scene)
        except ModelLoadError:
            # Fallback: использовать запасную модель
            self.load_backup_model()
            return self._generate_internal(scene)
```

**Уровень пайплайна:**
```python
class Pipeline:
    def run(self, input_file, output_file):
        try:
            scenes = self.scene_parser.parse(input_file)
            # ... остальные шаги
        except Exception as e:
            logger.error(f"Ошибка в пайплайне: {e}")
            raise
```

---

## 🐳 Docker конфигурация

### Dockerfile
```dockerfile
FROM python:3.11-slim

# Установка FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p output temp logs

# Предзагрузка моделей TTS (опционально)
RUN python -c "from TTS.api import TTS; TTS('tts_models/ru/ruslan/fairseq_vits')"

CMD ["python", "main.py", "--help"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  text2video:
    build: .
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./assets:/app/assets
      - ./config.yaml:/app/config.yaml
    environment:
      - LOG_LEVEL=INFO
    command: python main.py -i /app/input/script.txt -o /app/output/video.mp4
```

---

## 🌍 Мультиязычность

### Конфигурация языков в config.yaml

```yaml
tts:
  language: "ru"  # ru | en
  models:
    ru: "tts_models/ru/ruslan/fairseq_vits"
    en: "tts_models/en/ljspeech/tacotron2-DDC"
  
subtitles:
  language: "ru"  # Язык субтитров (авто из tts.language)
```

### Переключение языка
```python
class TTSGenerator:
    def __init__(self, config):
        self.language = config['tts']['language']
        model_path = config['tts']['models'][self.language]
        self.tts = TTS(model_path)
```
