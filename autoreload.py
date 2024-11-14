# - starts asyncio task task() in module.
# - when module changes it will cancel the task, reload the module, and restart the task


import asyncio
import importlib
import sys
import os
import traceback

from watchfiles import awatch


def task_done(task):
    task.result()  # Raises the exception if one occurred

#start module task, watch for changes, and restart task if needed
async def auto_reload(module):

    #create initial task
    print(f"autoreload: Starting main task() for '{module.__name__}'")
    task=asyncio.create_task(module.task())
    task.add_done_callback(task_done)

    module_file = os.path.abspath(module.__file__)
    async for changes in awatch(os.path.dirname(module_file)):
        for change_type, changed_file in changes:
            if os.path.abspath(changed_file) == module_file:
                print(f"autoreload: Reloading module '{module.__name__}' ...")

                #cancel old task
                task.cancel()

                try:
                    importlib.reload(module)
                except Exception as e:
                    print("autoreload failed: (restarting old task)")
                    traceback.print_exc()

                #recreate task
                task=asyncio.create_task(module.task())
                task.add_done_callback(task_done)

                print("autoreload: done")

# async def auto_reload(module):
#     try:
#         await watch_module(module)
#     except KeyboardInterrupt:
#         print("Stopping module watcher...")

