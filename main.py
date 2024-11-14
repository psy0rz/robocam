import asyncio

from autoreload import auto_reload

import detector


async def main():

    await asyncio.create_task(auto_reload(detector))
    # import dingen
    # await asyncio.create_task(auto_reload(dingen))



asyncio.run(main())


