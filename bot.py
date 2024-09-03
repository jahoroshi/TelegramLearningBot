import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM-TOKEN"))
dp = Dispatcher()


