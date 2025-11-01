# ImageFlow API для Make

## URL для использования в Make

**Основной endpoint:**
```
https://cardforge.cloud/render
```

**Health check:**
```
https://cardforge.cloud/imageflow-health
```

## Настройка HTTP модуля в Make

1. **Method:** `POST`
2. **URL:** `https://cardforge.cloud/render`
3. **Headers:**
   ```
   Content-Type: application/json
   ```
4. **Body (JSON):**
   ```json
   {
     "image_url": "{{URL_ИЗОБРАЖЕНИЯ}}",
     "game_title": "{{НАЗВАНИЕ_ИГРЫ}}",
     "provider": "{{ПРОВАЙДЕР}}"
   }
   ```

## Пример запроса

```bash
curl -X POST https://cardforge.cloud/render \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "game_title": "Hot Bonus",
    "provider": "Pragmatic Play"
  }' \
  --output result.png
```

## Ответ

- **Content-Type:** `image/png`
- **Body:** Бинарные данные PNG изображения
- **Headers:** 
  - `Content-Disposition: attachment; filename="cover.png"`

## Важно

- Операция может занять 30-60 секунд (из-за Seedream API)
- Таймаут Nginx установлен на 600 секунд
- Максимальный размер входного изображения: 10MB

## Troubleshooting

Если получаете ошибку "IP address is not valid":
- Используйте домен `https://cardforge.cloud/render` вместо IP-адреса
- Убедитесь, что сервер запущен: `ps aux | grep imageflow`
- Проверьте health: `curl https://cardforge.cloud/imageflow-health`




