# ImageFlow API

Python API сервис для обработки изображений по ComfyUI workflow.

## Установка

1. Установите зависимости:
```bash
cd /var/www/cardforge.cloud/imageflow
pip3 install -r requirements.txt
```

2. Создайте файл `.env` в директории `imageflow/`:
```bash
cd /var/www/cardforge.cloud/imageflow
cat > .env << EOF
FAL_API_KEY=c2718dfc-1d63-481b-ab1f-4e7983acb5b1:02ce987c304aa408f77dfb41066b79b6
PORT=8000
EOF
```

3. Проверьте установку зависимостей:
```bash
python3 check_deps.py
```

## Запуск

### Локально (простой способ)
```bash
cd /var/www/cardforge.cloud
python3 imageflow/run.py
```

### Через модуль Python
```bash
cd /var/www/cardforge.cloud
python3 -m imageflow.app
```

### Через uvicorn напрямую
```bash
cd /var/www/cardforge.cloud
uvicorn imageflow.app:app --host 0.0.0.0 --port 8000
```

### Через systemd (рекомендуется для продакшена)
```bash
# Скопируйте unit файл
sudo cp /var/www/cardforge.cloud/imageflow/imageflow.service /etc/systemd/system/

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable imageflow

# Запустите сервис
sudo systemctl start imageflow

# Проверьте статус
sudo systemctl status imageflow

# Просмотр логов
sudo journalctl -u imageflow -f
# или
tail -f /var/www/cardforge.cloud/imageflow/imageflow.log
```

## API Endpoints

### POST /render

Обработать изображение по полному пайплайну.

**Request Body (JSON):**
```json
{
  "image_url": "https://example.com/image.jpg",
  "game_title": "Hot Bonus",
  "provider": "Pragmatic Play"
}
```

**Response:**
- Content-Type: `image/png`
- Body: Бинарные данные PNG изображения

**Пример curl:**
```bash
curl -X POST http://localhost:8000/render \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "game_title": "Hot Bonus",
    "provider": "Pragmatic Play"
  }' \
  --output result.png
```

**Пример для Make/Zapier:**
```json
{
  "method": "POST",
  "url": "https://cardforge.cloud:8000/render",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "image_url": "{{image_url}}",
    "game_title": "{{game_title}}",
    "provider": "{{provider}}"
  }
}
```

### GET /health

Проверка здоровья сервиса.

**Response:**
```json
{
  "status": "ok"
}
```

## Пайплайн обработки

1. **Seedream очистка** - удаление подписей, текста, рамок через Fal AI
2. **Remove Background** - удаление фона через rembg (RMBG-2.0)
3. **Mask Processing** - инверсия, рост (7px), размытие (5px)
4. **Inpainting** - заполнение фона через cv2.inpaint (TELEA, radius=64)
5. **Color Extraction** - извлечение 2 доминантных цветов через KMeans
6. **Gradient Background** - создание вертикального градиента (linear RGB)
7. **Compositing** - наложение обработанного изображения на градиент
8. **Text Overlays** - добавление двух текстовых слоёв:
   - Верхний: `game_title` (font_size=230, opacity=1.0)
   - Нижний: `provider` (font_size=180, opacity=0.7)

## Технологии

- **FastAPI** - веб-фреймворк
- **rembg** - удаление фона
- **OpenCV** - обработка изображений и инпейнтинг
- **scikit-learn** - извлечение цветов через KMeans
- **Pillow** - работа с изображениями
- **Fal AI Seedream** - очистка изображений

## Структура проекта

```
imageflow/
├── __init__.py
├── app.py              # FastAPI приложение
├── pipeline.py         # Основной пайплайн
├── seedream_api.py     # Интеграция с Seedream
├── rmbg.py            # Удаление фона
├── masks.py           # Обработка масок
├── inpaint.py         # Инпейнтинг
├── colors.py          # Извлечение цветов
├── gradient.py        # Генерация градиента
├── compose.py         # Композиция изображений
├── textdraw.py        # Текстовые оверлеи
├── utils.py           # Утилиты
├── requirements.txt
└── README.md
```

## Переменные окружения

- `FAL_API_KEY` - API ключ для Fal AI (обязательно)
- `PORT` - Порт для запуска сервера (по умолчанию 8000)

## Troubleshooting

### Ошибка "FAL_API_KEY не настроен"
Убедитесь, что файл `.env` существует и содержит `FAL_API_KEY`.

### Ошибка импорта модулей
Убедитесь, что запускаете из правильной директории или используйте:
```bash
python -m imageflow.app
```

### Шрифт не найден
Если `blackrumbleregular.ttf` не найден, система использует fallback шрифт. 
Поместите файл шрифта в директорию проекта или `/usr/share/fonts/`.

### Seedream timeout
Увеличьте timeout в `seedream_api.py` или проверьте подключение к интернету.

