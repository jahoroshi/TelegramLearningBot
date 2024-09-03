import asyncio
import logging
from dotenv import load_dotenv
from app.handlers import main_router
from app.middlewares import TestMiddleware
from bot import bot, dp

async def main():
    """
    Main function to configure and start the Telegram bot.

    This function loads environment variables, sets up middleware, includes
    the main router with handlers, and starts the bot's polling process to
    receive updates from Telegram.
    """
    load_dotenv()  # Load environment variables from a .env file

    # Set up middleware
    mw = TestMiddleware()
    main_router.message.middleware(mw)
    main_router.callback_query.middleware(mw)

    # Include the main router with registered handlers
    dp.include_router(main_router)

    # Log the start of bot polling
    logging.info("Starting bot polling")

    # Start polling to receive updates from Telegram
    await dp.start_polling(bot)

if __name__ == '__main__':
    """
    Entry point of the application. Configures logging and starts the main
    asynchronous function.
    """
    logging.basicConfig(level=logging.INFO)  # Configure logging
    asyncio.run(main())  # Run the main function asynchronously
