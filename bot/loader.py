from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from logger import logger

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logger.info("🤖 Бот инициализирован")
