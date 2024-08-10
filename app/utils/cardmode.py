# from app.services import card_mode_start
import random

from app.middlewares.i18n_init import i18n

_ = i18n.gettext


def gen_output_text(card_data=None, front=None, extra_text=''):
    emoji = random.choice(('🫠', '🔅', '🔆', '🔥', '✨', '️❗️', '😊', '😂', '🎯', '✴️', '💢', '🤓', '🤔'))
    rating_names = {1: _('again'), 2: _('hard'), 3: _('good'), 4: _('easy')}
    letters = 3 if i18n.current_locale == 'ru' else None
    if card_data:
        front = card_data.get("front_side")
        back = card_data.get("back_side")
        ratings_count = card_data.get("ratings_count")
        ratings_text = " | ".join([f'{value[:letters]}:  {ratings_count[str(key)]}'
                                   for key, value in rating_names.items()]) if ratings_count else ''

        text = _(f'''

{emoji}   <b><i>{front.ljust(20, ' ')}</i></b>




<blockquote>
<b>{back.center(35, ' ')}</b>¬

</blockquote>



{ratings_text}
''')

    elif front:
        front = front
        text = f"""

{emoji}   <b>{front.ljust(20, ' ')}</b>

<blockquote>{extra_text}</blockquote>
"""

    else:
        text = f"""
{extra_text}
"""

    return text if text else _("something_went_wrong_persistent_error")


emoji = ('🌻☀️🐝🌞🍀🔱', '🦋🩵💎🧢🇦🧊', '(◍•ᴗ•◍)', '⋆.˚✮🎧✮˚.⋆', '😎👌🔥🏕️🧔‍♀️', '⋆⭒˚.⋆🪐 ⋆⭒˚.⋆', '✩♬ ₊˚.🎧⋆☾⋆⁺₊✧', '▶︎ •၊၊||၊|။|||| |',
         '𓆉𓆝𓆟 𓆞 𓆝 𓆟𓇼', '𓅰 𓅬 𓅭 𓅮 𓅯', 'ﮩ٨ـﮩﮩ٨ـ♡ﮩ٨ـﮩﮩ٨ـ', '˙✧˖°📷 ༘ ⋆｡˚', '˚ ༘ ೀ⋆｡˚', '¯\_(ツ)_/¯', 'ツ', '•ᴗ•', '◉‿◉',
         '⋆.˚🦋༘⋆', '◝(ᵔᵕᵔ)◜')
