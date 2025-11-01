#!/bin/bash
# Скрипт для публикации репозитория на GitHub

REPO_NAME="imageflow-snapshot"
GITHUB_USER="kozinakarina"

echo "=== Публикация репозитория на GitHub ==="
echo ""
echo "Текущий путь: $(pwd)"
echo ""

# Проверяем, есть ли уже remote
if git remote | grep -q origin; then
    echo "⚠️  Remote 'origin' уже существует:"
    git remote -v
    echo ""
    read -p "Заменить? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "Отменено"
        exit 1
    fi
fi

# Запрашиваем имя репозитория
read -p "Имя репозитория на GitHub [$REPO_NAME]: " input_repo
REPO_NAME=${input_repo:-$REPO_NAME}

# Запрашиваем метод подключения
echo ""
echo "Выберите метод подключения:"
echo "1) HTTPS (проще, требует токен)"
echo "2) SSH (требует настроенный SSH ключ)"
read -p "Ваш выбор [1]: " method
method=${method:-1}

if [ "$method" = "2" ]; then
    REMOTE_URL="git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
else
    REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
fi

echo ""
echo "Добавляю remote: $REMOTE_URL"
git remote add origin "$REMOTE_URL"

echo ""
echo "Переименовываю ветку в main..."
git branch -M main

echo ""
echo "=== Готово к публикации! ==="
echo ""
echo "Убедитесь, что репозиторий '$REPO_NAME' создан на GitHub"
echo "Затем выполните:"
echo "  git push -u origin main"
echo ""
echo "Или запустите этот скрипт снова с флагом --push"
