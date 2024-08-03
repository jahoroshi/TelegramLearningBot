import app.keyboards as kb
from app.middlewares.i18n_init import i18n

_ = i18n.gettext

async def generate_help_response():
    """
    Generates the help response text and keyboard markup.

    Returns:
        tuple: A tuple containing the help text and reply markup.
    """
    # Localize the help description
    text = _("help_description")
    # Get the keyboard for navigation
    reply_markup = await kb.back()

    return text, reply_markup
