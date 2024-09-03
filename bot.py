import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the Bot with the token retrieved from environment variables
bot = Bot(token=os.getenv("TELEGRAM-TOKEN"))

# Initialize the Dispatcher to manage updates and handlers
dp = Dispatcher()
