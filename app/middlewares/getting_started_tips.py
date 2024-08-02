import asyncio
import logging
import random
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, exceptions
from aiogram.enums import ParseMode
from aiogram.types import TelegramObject, CallbackQuery

from app.services import set_initial_user_language
from bot import bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GettingStartedTips(BaseMiddleware):
    def __init__(self):
        self._last_msg = 0
        self._messages = {
            'deck_details_': 'Добро пожаловать в управление категорией.\n🤓 Чтобы начать изучать карточки, нажмите <b>«Учить»</b>.\n🧐 Кнопка <b>«Смотреть карточки»</b> покажет все карточки в этой категории.\n🚚 Для добавления сразу множества карточек используйте кнопку <b>«Импортировать»</b>.',
            'show_cards_': 'Это меню управления карточками.\nНажмите <b>«Add card»</b>, чтобы добавить новую карточку.\nКнопка <b>«Edit card»</b> позволяет изменить содержимое выбранной карточки.\nДля удаления карточки используйте кнопку <b>«Delete card»</b>.',
            'delete_card': 'Если хотите удалить одну карточку, просто введите её номер из списка. Чтобы удалить сразу несколько карточек, перечислите их номера через пробел или запятую.',
            'add_card_': ('Мы сделали добавление карточки еще проще. Просто отправьте мне два сообщения подряд:\n\n1. В первом напишите текст, который хотите видеть на <b>лицевой стороне</b> карточки. 📝\n2. Во втором - текст для <b>обратной стороны</b>. ✨\n\nКак только я получу оба сообщения, я пойму, что вы хотите добавить новую карточку, и предложу выбрать подходящую <b>категорию</b>. Всё <b>просто</b> и <b>быстро</b>! Если у вас есть вопросы, не стесняйтесь спрашивать. Удачи! 😊\n\n<i>Пока жду ваше первое сообщение для лицевой стороны карточки!</i> ↴', '🃏 Сначала введите сторону карточки, которую хотите изучать.\nОна будет показана первой в процессе изучения.\n\n🎴 Если хотите учить обе стороны карточки, укажите это в конце процесса добавления карточки.'),
            'edit_card': 'Вот как вы можете изменить карточку:\n\n1. Выберите карточку, введя ее номер из списка.\n2. Введите новый текст для передней и задней сторон карточки. Если не хотите менять какую-либо сторону, просто напишите три точки (  ...  ) .\n3. Внимание: поля не могут быть пустыми. Используйте три точки для сторон без изменений.\n4. После этого вы сможете выбрать, хотите ли вы изучать обе стороны карточки.\n\nНачинаем! Пожалуйста, введите номер карточки. ⤵️',
            'import_cards_': 'В этом окне ты можешь добавить сразу несколько карточек в нужную категорию.\nПросто следуй инструкциям выше, и у тебя всё получится. 🏆',
            'choose_study_format_': 'Здесь ты можешь выбрать, как будет отображаться лицевая сторона карточки.\n🇦 Если выберешь текст, то она будет выводиться в виде текста.\n🗣️ Если выберешь звук, то лицевая сторона будет воспроизводиться голосом. Это поможет тренировать 🏋️‍♂️ восприятие на слух.',
            'start_studying_': 'Это режим изучения карточек.\n🧐 Если ты уже знаешь эту карточку и не хочешь её дальше учить, нажми <b>«already known»</b> в самом низу.\n👀 Чтобы увидеть заднюю сторону карточки, нажми <b>«show back»</b>.',
            'button_show_back': '💯 Пора оценить, насколько сложно тебе было вспомнить ответ на эту карточку. Вот как это работает:\n\n🥵 <b>Again</b>: Если было очень трудно, выбирай эту опцию.\n😤 <b>Hard</b>: Если ты вспоминал с трудом, но всё-таки вспомнил.\n🤗 <b>Good</b>: Если всё прошло гладко, но всё же пришлось немного задуматься.\n😎 <b>Easy</b>: Если ответ пришел мгновенно, как по щелчку пальцев.\n\nПосле того как оценишь, АнкиБот 🤖 сразу покажет следующую карточку. Наш умный алгоритм подберёт время для следующего показа:\n\n⏰ <b>Again, Hard, Good</b>: карточка появится в ближайшее время, чтобы освежить память.\n⏰💥 <b>Easy</b>: карточка появится снова через 24 часа или даже через несколько дней, чтобы закрепить знания. Надеюсь, ты отлично справляешься! 💪',
            'rating': ('👉 Нажми <b>«show back»</b> или воспользуйся подсказкой, а затем оцени, насколько легко было вспомнить.', '🚧 Если ты не можешь вспомнить значение карточки, не спеши нажимать «Show Back».\n🚀Попробуй воспользоваться одной из наших подсказок, чтобы немного помочь себе.\n🥇После этого оцени, насколько сложно было вспомнить ответ.'),
            '/addcard': 'Есть и другой способ добавить карточку быстрее! Просто отправьте боту два сообщения: в первом сообщении текст с лицевой стороны карточки, а во втором — текст с задней стороны. 📝✨\n\nКак только бот получит оба сообщения, он поймёт, что вы хотите добавить карточку, и предложит вам выбрать подходящую категорию. Это легко и быстро! Удачи! 😊\n\n<i>а пока продолжим ввод главной стороны карточки</i> ↴',
            '': '',
            '': '',
            '': '',
        }
        self._tips_count = {tip: 1 for tip in self._messages}
        self._tips_count['rating'] = 2
        self._tips_count['add_card_'] = 2

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
        state = data['state']
        self.telegram_id = state.key.user_id
        if trigger.startswith('back_to_decks') or trigger.startswith('deck_details_'):
            await self._delete_message()

        tip_message = await self._message_handler(trigger)
        if tip_message:
            if self._last_msg != 0:
                await self._delete_message()
            emoji = random.choice(('🚨', '💡', '☝️', '🚀', '🚩'))
            msg = await message.answer(f'{emoji} Tip!\n<blockquote>{tip_message}</blockquote>', parse_mode=ParseMode.HTML)
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
                    if isinstance(tip, tuple):
                        tip = tip[self._tips_count[trig] - 1]
                    self._tips_count[trig] -= 1
                    print(self._tips_count)
                    if sum(self._tips_count.values()) == 0:
                        await self._unregister_middleware()
                    elif sum(self._tips_count.values()) == 4:
                        await self._pre_disable_getting_started_tips()
                    return tip

    async def _unregister_middleware(self):
        from app.handlers import main_router
        main_router.message.middleware.unregister(self)
        main_router.callback_query.middleware.unregister(self)

    async def _delete_message(self):
        try:
            await asyncio.create_task(bot.delete_message(chat_id=self.chat_id, message_id=self._last_msg))
        except Exception as e:
            logger.error(f"Failed to delete message {self._last_msg} in chat {self.chat_id}: {e}")

    async def _pre_disable_getting_started_tips(self):
        from app.middlewares.locales import i18n_middleware
        language = await i18n_middleware.get_lang()
        await set_initial_user_language(self.telegram_id, language.lower())
