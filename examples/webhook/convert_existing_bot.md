# Перенос существующего `bot.py` с Long Polling на Webhook

Этот файл описывает точечные изменения для большого бота, который уже содержит импорты, константы,
хранилища, `Bot(...)`, `Dispatcher()` и все обработчики. Первые 300+ строк с описанием меню,
`AcceptanceStore`, dataclass-сессий и обработчиков переносить в новый пример не нужно — они остаются
в вашем `bot.py` без изменений.

## 1. Уберите секреты из кода

Вместо токена в исходниках используйте переменные окружения. Блок с токеном и служебными ID можно
оставить рядом с текущими константами:

```python
import os

BOT_TOKEN = os.environ['MAX_BOT_TOKEN']
ADMIN_USER_ID = int(os.getenv('MAX_ADMIN_USER_ID', '16439444'))
ADMIN_CHAT_ID = int(os.getenv('MAX_ADMIN_CHAT_ID', '-70804898799764'))
WHITE_CHECK_CHAT_ID = int(os.getenv('MAX_WHITE_CHECK_CHAT_ID', '-70809030254740'))

WEBHOOK_URL = os.getenv('MAX_WEBHOOK_URL')
WEBHOOK_HOST = os.getenv('MAX_WEBHOOK_HOST', '0.0.0.0')
WEBHOOK_PORT = int(os.getenv('MAX_WEBHOOK_PORT', '8080'))
```

После этого существующие строки остаются прежними:

```python
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
```

## 2. Не дублируйте верх файла

В присланном фрагменте блок импортов и констант повторяется два раза. В рабочем `bot.py` оставьте
только один такой блок: повторный импорт, повторная инициализация `store = AcceptanceStore(...)`,
`bot = Bot(...)` и `dp = Dispatcher()` могут сбросить уже зарегистрированные обработчики или состояние.

## 3. Замените только запуск внизу файла

Все декораторы `@dp.message_created(...)`, `@dp.message_callback(...)`, `@dp.bot_started()` и другие
обработчики можно оставить как есть. Нужно заменить только функцию запуска, где раньше был Long Polling:

```python
async def main():
    await dp.start_polling(bot)
```

на Webhook-запуск:

```python
async def main():
    if WEBHOOK_URL:
        await bot.subscribe_webhook(WEBHOOK_URL)

    await dp.handle_webhook(
        bot=bot,
        host=WEBHOOK_HOST,
        port=WEBHOOK_PORT,
        log_level='critical',
    )


if __name__ == '__main__':
    asyncio.run(main())
```

Если подписка на webhook уже создана вручную, `MAX_WEBHOOK_URL` можно не задавать: бот просто поднимет
сервер и будет принимать входящие POST-запросы.

## 4. Команды запуска

Установите зависимости для Webhook:

```bash
pip install 'maxapi[webhook]'
```

Запустите бота с публичным URL, который указывает на ваш сервер и порт:

```bash
export MAX_BOT_TOKEN='ваш_токен'
export MAX_WEBHOOK_URL='https://example.com/'
export MAX_WEBHOOK_HOST='0.0.0.0'
export MAX_WEBHOOK_PORT='8080'
python bot.py
```

Webhook URL должен быть доступен снаружи. Если запускаете за nginx или другим reverse proxy, публичный
`MAX_WEBHOOK_URL` должен указывать на внешний HTTPS-адрес, а `MAX_WEBHOOK_HOST`/`MAX_WEBHOOK_PORT` — на
локальный интерфейс и порт, где слушает приложение.
