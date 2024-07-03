from app.database.models import async_db_session
from app.database.models import User, Category, Item, UserConfig
from sqlalchemy import select



async def get_user_config(tg_id):
    async with async_db_session() as session:
        config = await session.scalar(select(UserConfig.config).where(UserConfig.telegram_id == tg_id))
        return config


async def set_user_config(tg_id, data):
    async with async_db_session() as session:
        user = await session.scalar(select(UserConfig.config).where(UserConfig.telegram_id == tg_id))
        print('database   ', user)
        if user:
            user.config = data
        else:
            user = UserConfig(telegram_id=tg_id, config=data)

        session.add(user)
        await session.commit()




async def set_user(tg_id):
    async with async_db_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_categories():
    async with async_db_session() as session:
        return await session.scalars(select(Category))


async def get_category_item(category_id):
    async with async_db_session() as session:
        return await session.scalars(select(Item).where(Item.category == int(category_id)))


async def get_item(item_id):
    async with async_db_session() as session:
        return await session.scalar(select(Item).where(Item.id == int(item_id)))