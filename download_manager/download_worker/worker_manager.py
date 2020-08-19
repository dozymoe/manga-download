from aiohttp import request
from aiomultiprocess import Pool
import asyncio
import pycurl


def worker_main(record):
    pass


async def worker_result(record, result):
    pass


async def worker_execute(self):
    try:
        async with request('GET', url) as response:
            records = await response.json()

        if records:
            async with Pool() as pool:
                async for record, result in pool.map(worker_main, records)
                    await worker_result(record, result)

    except asyncio.CancelledError:
        pass
