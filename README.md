# ImageFlow Snapshot

Git репозиторий с сохранением текущего состояния пайплайна обработки изображений.

## Что включено

- ✅ Полный рабочий пайплайн обработки изображений
- ✅ Все модули и зависимости
- ✅ Документация и примеры конфигурации
- ✅ Текущие настройки градиента и текста

## Быстрый старт

```bash
# Клонирование (если будет размещен на GitHub/GitLab)
git clone <repository-url>
cd imageflow-snapshot

# Или использование локального репозитория
cd ~/imageflow-snapshot

# Установка зависимостей
pip install -r imageflow/requirements.txt

# Настройка .env
cp imageflow/.env.example imageflow/.env 2>/dev/null || echo "PORT=8000" > imageflow/.env
echo "FAL_API_KEY=your_key_here" >> imageflow/.env

# Запуск
cd imageflow
python3 run.py
```

## Версия

**Snapshot от:** 2025-10-31

**Основные параметры:**
- Градиент: transition_start=360, transition_end=960, blur_size=300
- Текст: расстояние 34px между игрой и провайдером
- Автоматическое форматирование названий игр
- Извлечение цветов строго из фона

## Структура

```
imageflow-snapshot/
├── README.md           # Этот файл
├── CHANGELOG.md        # История изменений
├── SETUP_GIT_REMOTE.md # Инструкции по публикации
├── .gitignore          # Исключения Git
└── imageflow/          # Основной код проекта
    ├── app.py
    ├── pipeline.py
    └── ...
```

## Дополнительная информация

Подробное описание проекта смотрите в `imageflow/README.md`.

## Публикация на GitHub/GitLab

См. `SETUP_GIT_REMOTE.md` для инструкций.
