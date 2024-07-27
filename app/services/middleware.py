from app.middlewares.getting_started_tips import GettingStartedTips

middleware = GettingStartedTips()


async def set_tips_middleware():
    from app.handlers import main_router
    main_router.message.middleware(middleware)
    main_router.callback_query.middleware(middleware)

async def del_tips_middleware():
    from app.handlers import main_router
    main_router.message.middleware.unregister(middleware)
    main_router.callback_query.middleware.unregister(middleware)