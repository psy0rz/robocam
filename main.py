import asyncio

from autoreload import auto_reload_task

import detector
import robot

async def main():

    asyncio.create_task(auto_reload_task(detector))
    await asyncio.create_task(auto_reload_task(robot))
    # import dingen
    # await asyncio.create_task(auto_reload(dingen))



asyncio.run(main())


