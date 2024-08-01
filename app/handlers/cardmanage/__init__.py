from .add_card_quick import *
from .create_update_delete import *
from .import_cards import *
from .show_cards import *

# from .add_card_quick import router as add_card_quick_router
# from .add_card_quick import router_quick_addcard_text
from .create_update_delete import router as create_update_delete_router
# from .create_update_delete import router_quick_card_create
from .import_cards import router as import_cards_router
from .show_cards import router as show_cards_router

from aiogram import Router

cardmanage_router = Router()

# cardmanage_router.include_router(add_card_quick_router)
cardmanage_router.include_router(create_update_delete_router)
cardmanage_router.include_router(import_cards_router)
cardmanage_router.include_router(show_cards_router)
