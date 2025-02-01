"""
file: src/queue.py
description: queue for synchronous and asynchronous communication
"""

import asyncio


class Queue:
    """
    This class provides a queue that can be used to communicate between
    synchronous and asynchronous code.

    Original code shared by user4815162342 on StackOverflow:
    https://stackoverflow.com/a/59650685/8662931
    """

    def __init__(self, loop=None):
        self._loop = loop
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue()

    def sync_put_nowait(self, item):
        self._loop.call_soon(self._queue.put_nowait, item)

    def sync_put(self, item):
        asyncio.run_coroutine_threadsafe(self._queue.put(item), self._loop).result()

    def sync_get(self):
        return asyncio.run_coroutine_threadsafe(self._queue.get(), self._loop).result()

    def async_put_nowait(self, item):
        self._queue.put_nowait(item)

    async def async_put(self, item):
        await self._queue.put(item)

    async def async_get(self):
        return await self._queue.get()
