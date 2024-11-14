import asyncio

from autoreload import auto_reload_task

import detector


async def main():

    await asyncio.create_task(auto_reload_task(detector))
    # import dingen
    # await asyncio.create_task(auto_reload(dingen))



asyncio.run(main())


