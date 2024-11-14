import asyncio

from autoreload import auto_reload



async def main():

    import detector
    await asyncio.create_task(auto_reload(detector))

asyncio.run(main())


