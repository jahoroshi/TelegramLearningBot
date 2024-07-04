from .cardmode import *
from .cardmode import router as cardmode_router

from aiogram import Router

main_router = Router()

main_router.include_router(cardmode_router)
