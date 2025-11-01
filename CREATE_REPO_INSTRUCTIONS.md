# Инструкция по созданию репозитория на GitHub

## Шаг 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. **Repository name:** `imageflow-snapshot`
3. **Description:** (опционально) ImageFlow pipeline snapshot
4. Выберите **Private** или **Public**
5. **НЕ добавляйте**:
   - ❌ README file
   - ❌ .gitignore  
   - ❌ License
   (Все это уже есть в локальном репозитории)

6. Нажмите **"Create repository"**

## Шаг 2: Публикация кода

После создания репозитория выполните:

```bash
cd ~/imageflow-snapshot

# Если remote уже настроен (проверьте: git remote -v)
git branch -M main
git push -u origin main

# Если remote не настроен или нужно изменить:
git remote set-url origin https://github.com/kozinakarina/imageflow-snapshot.git
git branch -M main
git push -u origin main
```

## Проверка

После успешной публикации репозиторий появится на:
https://github.com/kozinakarina/imageflow-snapshot

## Проблемы с аутентификацией

Если Git запросит логин/пароль:
- Используйте **Personal Access Token** вместо пароля
- Создайте токен: https://github.com/settings/tokens
- Или используйте SSH: `git@github.com:kozinakarina/imageflow-snapshot.git`
