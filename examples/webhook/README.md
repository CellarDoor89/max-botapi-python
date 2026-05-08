## Вебхуки

 - [Бот, перенесённый с Long Polling на Webhook](https://github.com/love-apples/maxapi/tree/main/examples/webhook/from_polling.py)
 - [Высокоуровневый](https://github.com/love-apples/maxapi/tree/main/examples/webhook/high_level.py)
 - [Низкоуровневый](https://github.com/love-apples/maxapi/tree/main/examples/webhook/low_level.py)

### Перенос бота с Long Polling

В файле `from_polling.py` сохранены те же обработчики, что обычно используются при `dp.start_polling(bot)`, но запуск заменён на `dp.handle_webhook(...)`.

Для автоматической подписки задайте публичный URL вебхука в переменной окружения `MAX_WEBHOOK_URL`:

```bash
export MAX_BOT_TOKEN='ваш_токен'
export MAX_WEBHOOK_URL='https://example.com/'
python examples/webhook/from_polling.py
```

Если подписка уже создана вручную, `MAX_WEBHOOK_URL` можно не указывать — пример просто поднимет сервер для входящих событий.
