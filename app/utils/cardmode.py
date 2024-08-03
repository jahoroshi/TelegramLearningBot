# from app.handlers import card_mode_start
import asyncio
import random
import re



def gen_output_text(card_data=None, front=None, extra_text=''):
    from app.middlewares.i18n_init import i18n
    _ = i18n.gettext
    emoji = random.choice(('🫠', '🔅', '🔆', '🔥', '✨', '️❗️', '😊', '😂', '🎯', '✴️', '💢', '🤓', '🤔'))
    rating_names = {1: _('again'), 2: _('hard'), 3: _('good'), 4: _('easy')}

    if card_data:
        front = re.escape(card_data.get("front_side"))
        back = re.escape(card_data.get("back_side"))
        ratings_count = card_data.get("ratings_count")
        ratings_text = " \| ".join([f'{value}:  {ratings_count[str(key)]}'
                                    for key, value in rating_names.items()]) if ratings_count else ''

        text = f"""

{emoji}   _*{front.ljust(20, ' ')}*_



>*{_("answer")}*
>🔥🔥 _*{back.center(35, ' ')}*_  




{ratings_text}
"""

    elif front:
        front = re.escape(front)
        text = f"""

{emoji}   _*{front.ljust(20, ' ')}*_  

>{re.escape(extra_text)}
"""

    else:
        text = f"""
>{re.escape(extra_text)}
"""

    return text if text else _("something_went_wrong_persistent_error")


# async def timer_del_msg(message, timer: int = 1):
#     await asyncio.sleep(timer)
#     await message.delete()
#
#
# async def timer_send_msg(message, timer: int = 10):
#     await asyncio.sleep(timer)
#     await message.answer(_('correct_answer_tip'))
