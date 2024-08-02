from .start import *
from .help import *

from .start import router as start_router
from .help import router as help_router

bot_router = Router()

bot_router.include_router(start_router)
bot_router.include_router(help_router)
