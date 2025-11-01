# Настройка удаленного репозитория

Если вы хотите разместить этот репозиторий на GitHub или GitLab:

## GitHub

1. Создайте новый репозиторий на GitHub (не инициализируйте его)

2. Добавьте remote:
```bash
cd ~/imageflow-snapshot
git remote add origin https://github.com/YOUR_USERNAME/imageflow-snapshot.git
git branch -M main
git push -u origin main
```

## GitLab

1. Создайте новый проект на GitLab

2. Добавьте remote:
```bash
cd ~/imageflow-snapshot
git remote add origin https://gitlab.com/YOUR_USERNAME/imageflow-snapshot.git
git branch -M main
git push -u origin main
```

## Локальная копия

Просто скопируйте директорию:
```bash
cp -r ~/imageflow-snapshot /path/to/backup/location/
```

Или создайте архив:
```bash
cd ~
tar -czf imageflow-snapshot-$(date +%Y%m%d).tar.gz imageflow-snapshot/
```
