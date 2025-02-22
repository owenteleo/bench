import asyncio

from loguru import logger

async def server(ctx):
    """
    Long running processes.
    """

    while True:
        await asyncio.sleep(1)
        logger.trace("Server running...")
