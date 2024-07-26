from .btn_first_letter import *
from .btn_scramble_letters import *
from .btn_similar_words import *
from .btns_set_rating import *
from .buttons_misc import *
from .cardmode_start import *
from .speech import *

from .btn_first_letter import router as btn_first_letter_router
from .btn_scramble_letters import router as btn_scramble_letters_router
from .btn_similar_words import router as btn_similar_words_router
from .btns_set_rating import router as btns_set_rating_router
from .buttons_misc import router as buttons_misc_router
from .cardmode_start import router as cardmode_start_router
from .speech import router as speech_router

from aiogram import Router

cardmode_router = Router()

cardmode_router.include_router(btn_first_letter_router)
cardmode_router.include_router(btn_scramble_letters_router)
cardmode_router.include_router(btn_similar_words_router)
cardmode_router.include_router(btns_set_rating_router)
cardmode_router.include_router(buttons_misc_router)
cardmode_router.include_router(cardmode_start_router)
cardmode_router.include_router(speech_router)
