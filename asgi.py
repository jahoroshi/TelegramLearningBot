from run import main

def application():
    """
    Creates an ASGI application that wraps the asynchronous `main` coroutine.

    This function returns a callable object (`app`) that can be used by an ASGI server,
    such as Uvicorn, to handle incoming requests. The `app` function will invoke the
    `main` coroutine, which is where the core logic of the application resides.

    This setup allows the `main` coroutine to be executed in an ASGI-compatible environment,
    ensuring that the application can handle asynchronous operations efficiently.

    Returns:
        app (callable): An ASGI application that wraps the `main` coroutine.
    """
    async def app(scope, receive, send):
        await main()
    return app
