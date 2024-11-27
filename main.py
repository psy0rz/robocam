import asyncio
import sys

from autoreload import auto_reload_task

import detector

async def main():

    asyncio.create_task(auto_reload_task(detector))


    if "calibrate-offsets" in sys.argv:
        import calibrate_offsets
        await asyncio.create_task(auto_reload_task(calibrate_offsets))

    elif "calibrate-camera" in sys.argv:
        import calibrate_cam
        await asyncio.create_task(auto_reload_task(calibrate_cam))

    else:
        import analyser
        asyncio.create_task(auto_reload_task(analyser))

        import task_cleanup
        await asyncio.create_task(auto_reload_task(task_cleanup))




asyncio.run(main())


