import logging
import random
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, exceptions
from aiogram.types import TelegramObject, CallbackQuery

from bot import bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GettingStartedTips(BaseMiddleware):
    def __init__(self):
        self._last_msg = 0
        self._messages = {
            'deck_details_': 'Добро пожаловать в управление категорией.\nЧтобы начать изучать карточки, нажмите "Учить".\nКнопка "Смотреть карточки" покажет все карточки в этой категории.\nДля добавления сразу множества карточек используйте кнопку "Импортировать".',
            'show_cards_': 'Это меню управления карточками.\nНажмите "Add card", чтобы добавить новую карточку.\nКнопка "Edit card" позволяет изменить содержимое выбранной карточки.\nДля удаления карточки используйте кнопку "Delete card".',
            'delete_card': 'Если хотите удалить одну карточку, просто введите её номер из списка. Чтобы удалить сразу несколько карточек, перечислите их номера через пробел или запятую.',
            'add_card_': 'Сначала введите сторону карточки, которую хотите изучать.\nОна будет показана первой в процессе изучения. Если хотите учить обе стороны карточки, укажите это в конце процесса добавления карточки.',
            'edit_card': 'Чтобы изменить карточку, введите её номер из списка.\n Затем последовательно введите новую переднюю и заднюю стороны.\n Если какая-то сторона не требует изменений, просто скопируйте её значение из списка — поле пустым оставлять нельзя.\n В конце можно выбрать, хотите ли вы учить обе стороны карточки.',
            'import_cards_': 'В этом окне ты можешь добавить сразу несколько карточек в категорию.\nРазделяй переднюю и заднюю стороны карточки символом ;.\nКаждую новую карточку начинай с новой строки.\nМаксимальная длина сообщения — 4096 символов.',
            'choose_study_format_': 'Здесь ты можешь выбрать, как будет отображаться лицевая сторона карточки.\nЕсли выберешь текст, то она будет выводиться в виде текста.\nЕсли выберешь звук, то лицевая сторона будет воспроизводиться голосом. Это поможет тренировать восприятие на слух.',
            'start_studying_': 'Это режим изучения карточек.\nЕсли ты уже знаешь эту карточку и не хочешь её дальше повторять, нажми "already known" в самом низу.\nЧтобы увидеть заднюю сторону карточки, нажми "show back".',
            'button_show_back': 'После того как вспомнишь ответ, оцени сложность воспоминания карточки от "Again" (самое сложное) до "Easy" (самое лёгкое).\nПосле оценки появится следующая карточка.',
            'rating': random.choice(('Если не можешь вспомнить значение карточки,\nпрежде чем нажимать "show back", используй одну из подсказок, чтобы помочь себе вспомнить.\nНа основе твоей оценки наш алгоритм поймет, когда лучше снова показать эту карточку для лучшего запоминания.', 'Нажми "show back" или воспользуйся подсказкой, а затем оцени, насколько легко было вспомнить.')),
            '': '',
            '': '',
            '': '',
            '': '',
        }
        self._tips_count = {tip: 1 for tip in self._messages}
        self._tips_count['rating'] = 5

    @property
    def last_msg(self):
        return self._last_msg

    @last_msg.setter
    def last_msg(self, msg: int):
        self._last_msg = msg

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        if isinstance(event, CallbackQuery):
            message = event.message
            trigger = event.data
        else:
            message = event
            trigger = event.text

        event_handler = await handler(event, data)

        self.chat_id = message.chat.id
        if trigger.startswith('back_to_decks') or trigger.startswith('deck_details_'):
            await self._delete_message()

        tip_message = await self._message_handler(trigger)
        if tip_message:
            if self._last_msg != 0:
                await self._delete_message()
            emoji = random.choice(('🚨', '💡', '☝️', '🚀', '🚩'))
            msg = await message.answer(f'{emoji} Tip! {tip_message}')
            self._last_msg = msg.message_id

        return event_handler

    async def _message_handler(self, trigger: str):
        for trig, tip in self._messages.items():
            if trigger in ('Again', 'Hard', 'Good', 'Easy'):
                trigger = 'rating'
            if trigger.startswith(trig):
                if self._tips_count[trig] == 0:
                    return
                else:
                    self._tips_count[trig] -= 1
                    print(self._tips_count)
                    if sum(self._tips_count.values()) == 0:
                        await self._unregister_middleware()
                    return tip

    async def _unregister_middleware(self):
        from app.handlers import main_router
        main_router.message.middleware.unregister(self)
        main_router.callback_query.middleware.unregister(self)

    async def _delete_message(self):
        try:
            await bot.delete_message(chat_id=self.chat_id, message_id=self._last_msg)
        except Exception as e:
            logger.error(f"Failed to delete message {self._last_msg} in chat {self.chat_id}: {e}")