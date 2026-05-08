## Вебхуки

 - [Бот, перенесённый с Long Polling на Webhook](https://github.com/love-apples/maxapi/tree/main/examples/webhook/from_polling.py)
 - [Инструкция для переноса существующего `bot.py`](https://github.com/love-apples/maxapi/tree/main/examples/webhook/convert_existing_bot.md)
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


### Если у вас уже есть большой `bot.py`

Для существующего проекта не нужно переписывать первые сотни строк с импортами, константами,
хранилищами и dataclass-моделями. Оставьте их в текущем `bot.py`, уберите дублирующиеся блоки импортов
и замените только нижний запуск `dp.start_polling(bot)` на `dp.handle_webhook(...)`. Подробный вариант
с переменными окружения и командами запуска описан в `convert_existing_bot.md`.
