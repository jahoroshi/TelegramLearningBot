from .cardmode_launcher import *
from .create_deck import *
from .deckdetails import *
from .decklist import *
from .delete_deck import *
from .manage_deck import *
from .rename_deck import *
from .reset_deck_stats import *

from .cardmode_launcher import router as cardmode_launcher_router
from .create_deck import router as create_deck_router
from .deckdetails import router as deckdetails_router
from .decklist import router as decklist_router
from .delete_deck import router as delete_deck_router
from .manage_deck import router as manage_deck_router
from .rename_deck import router as rename_deck_router
from .reset_deck_stats import router as reset_deck_stats_router

from aiogram import Router

deckhub_router = Router()

deckhub_router.include_router(cardmode_launcher_router)
deckhub_router.include_router(create_deck_router)
deckhub_router.include_router(deckdetails_router)
deckhub_router.include_router(decklist_router)
deckhub_router.include_router(delete_deck_router)
deckhub_router.include_router(manage_deck_router)
deckhub_router.include_router(rename_deck_router)
deckhub_router.include_router(reset_deck_stats_router)
