from aiogram import Router

from .bot import router as bot_router
from .cardmanage import router as cardmanage_router
from .cardmanage import router_quick_card_create
from .cardmode import router as cardmode_router
from .deckhub import router as deckhub_router

main_router = Router()

main_router.include_router(bot_router)
main_router.include_router(cardmanage_router)
main_router.include_router(cardmode_router)
main_router.include_router(deckhub_router)
main_router.include_router(router_quick_card_create)

