## Решение проблемы 405 Method Not Allowed

Если вы получаете ошибку 405 при обращении к `/render`, используйте прямой доступ к серверу:

**URL для Make:**
```
http://YOUR_SERVER_IP:8000/render
```

Или настройте проксирование через другой домен/поддомен.

**Проверка:**
1. Сервер работает: `sudo systemctl status imageflow`
2. Локальный доступ работает: `curl -X POST http://localhost:8000/render -H "Content-Type: application/json" -d '{"image_url":"test","game_title":"test","provider":"test"}'`

**Временное решение:**
Используйте прямой IP-адрес сервера с портом 8000 в Make вместо домена через nginx.




