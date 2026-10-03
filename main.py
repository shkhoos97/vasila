import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import settings
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def setup_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота / главное меню"),
        BotCommand(command="help", description="Как пользоваться ботом"),
        BotCommand(command="rules", description="Золотые правила переписки"),
    ]
    await bot.set_my_commands(commands)

async def main():
    if not settings.telegram_bot_token:
        logger.error("КРИТИЧЕСКАЯ ОШИБКА: TELEGRAM_BOT_TOKEN не задан! Укажите его в файле .env")
        print("\n[!] ОШИБКА: Переменная TELEGRAM_BOT_TOKEN отсутствует в файле .env.")
        print("Пожалуйста, создайте бота через @BotFather, получите токен и впишите в .env\n")
        return

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()
    dp.include_router(router)

    await setup_commands(bot)
    logger.info("Бот 'Пикап Мастер & НЛП' успешно запущен и готов анализировать переписки!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
