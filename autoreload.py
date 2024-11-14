# async hot module reloading with unload() function

import importlib
import sys
import os
from watchfiles import awatch

async def watch_module(module):


    module_file = os.path.abspath(module.__file__)
    async for changes in awatch(os.path.dirname(module_file)):
        for change_type, changed_file in changes:
            if os.path.abspath(changed_file) == module_file:
                print(f"Detected changes in {module}:")

                # Check if the module has an 'on_unload' method and call it
                if hasattr(module, "on_unload"):
                    print(f"Calling on_unload for {module}...")
                    module.on_unload()
                print(f"Reloading {module}...")
                importlib.reload(module)

async def auto_reload(module):
    try:
        await watch_module(module)
    except KeyboardInterrupt:
        print("Stopping module watcher...")

