# ImageFlow API - Инструкция для Make

## ✅ Готово к использованию!

> **Протестировано:** 31.10.2025 - API успешно обрабатывает изображения за ~40-50 секунд

**URL для Make:**
```
https://cardforge.cloud/render
```

### Настройка HTTP модуля в Make

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

### Пример запроса

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

### Ответ

- **Content-Type:** `image/png`
- **Body:** Бинарные данные PNG изображения
- **Headers:** 
  - `Content-Disposition: attachment; filename="cover.png"`
  - CORS заголовки настроены

### Health Check

```bash
curl https://cardforge.cloud/imageflow-health
```

Ответ: `{"status":"ok"}`

### Важно

- ⏱️ Операция может занять 30-60 секунд (из-за Seedream API)
- ⏱️ Таймаут Nginx установлен на 600 секунд
- 📦 Максимальный размер входного изображения: 10MB
- 🔒 SSL сертификат настроен для `cardforge.cloud`

### Статус

- ✅ Сервер ImageFlow работает на порту 8000
- ✅ Nginx проксирование настроено (на основном домене `cardforge.cloud/render`)
- ✅ SSL сертификат работает
- ✅ CORS заголовки настроены
- ✅ Health endpoint доступен

### Troubleshooting

Если получаете ошибку:
1. Проверьте health: `curl https://cardforge.cloud/imageflow-health`
2. Проверьте статус сервера: `sudo systemctl status imageflow`
3. Проверьте логи: `sudo journalctl -u imageflow -n 50`
