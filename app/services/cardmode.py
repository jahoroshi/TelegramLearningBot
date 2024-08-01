# from app.handlers import card_mode_start
import asyncio
import random
import re


def gen_output_text(card_data=None, front=None, extra_text=''):
    emoji = random.choice(('🫠', '🔅', '🔆', '🔥', '✨', '️❗️', '😊', '😂', '🎯', '✴️', '💢', '🤓', '🤔'))
    rating_names = {1: 'Again', 2: 'Hard', 3: 'Good', 4: 'Easy'}

    if card_data:
        front = re.escape(card_data.get("front_side"))
        back = re.escape(card_data.get("back_side"))
        ratings_count = card_data.get("ratings_count")
        ratings_text = " \| ".join([f'{value}:  {ratings_count[str(key)]}'
                                    for key, value in rating_names.items()]) if ratings_count else ''

        text = f"""

{emoji}   _*{front.ljust(20, ' ')}*_



>*Answer*
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

    return text if text else ("🤯🥳 Something went wrong. "
                              "If this issue persists please contact us through our help center at ankichat.com")


async def timer_del_msg(message, timer: int = 1):
    await asyncio.sleep(timer)
    await message.delete()


async def timer_send_msg(message, timer: int = 10):
    await asyncio.sleep(timer)
    await message.answer('T!!!!!!he correct answer is 🫴  👈')


