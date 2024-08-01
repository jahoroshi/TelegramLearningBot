from .cardmode import *
from .start import *
from .deckhub import *
from .cardmanage import *

from .cardmode import cardmode_router
from .start import router as start_router
from .deckhub import deckhub_router
from .cardmanage import cardmanage_router
from .cardmanage import router_quick_card_create

from aiogram import Router

main_router = Router()

main_router.include_router(cardmanage_router)
main_router.include_router(cardmode_router)
main_router.include_router(deckhub_router)
main_router.include_router(start_router)
main_router.include_router(router_quick_card_create)
