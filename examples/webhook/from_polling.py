import asyncio
import logging
import os

# В существующем большом bot.py ваши импорты, константы, хранилища
# и обработчики остаются на месте. Для перехода на Webhook обычно
# достаточно вынести токен в окружение и заменить нижний запуск.

from maxapi import Bot, Dispatcher
from maxapi.filters import F
from maxapi.types import BotStarted, Command, MessageCreated

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('MAX_BOT_TOKEN', 'тут_ваш_токен')
WEBHOOK_URL = os.getenv('MAX_WEBHOOK_URL')
WEBHOOK_HOST = os.getenv('MAX_WEBHOOK_HOST', '0.0.0.0')
WEBHOOK_PORT = int(os.getenv('MAX_WEBHOOK_PORT', '8080'))

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Привет! Отправь мне /start или любое сообщение.'
    )


@dp.message_created(Command('start'))
async def hello(event: MessageCreated):
    await event.message.answer('Пример чат-бота для MAX работает через Webhook 💙')


@dp.message_created(F.message.body.text)
async def echo(event: MessageCreated):
    await event.message.answer(f'Повторяю за вами: {event.message.body.text}')


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
