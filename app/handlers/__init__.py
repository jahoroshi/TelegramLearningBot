from .cardmode import *
from .start import *
from .deckhub import *
from .cardmanage import *

from .cardmode import cardmode_router as cardmode_router
from .start import router as start_router
from .deckhub import router as deckhub_router
from .cardmanage import router as cardmanage_router

from aiogram import Router

main_router = Router()

main_router.include_router(cardmanage_router)
main_router.include_router(cardmode_router)
main_router.include_router(deckhub_router)
main_router.include_router(start_router)
