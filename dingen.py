import asyncio


async def task():
    # try:
        while True:
            await asyncio.sleep(1)
            print ("dingen loop8")
    # except asyncio.CancelledError:
    #     print("CANf")

# task=asyncio.create_task(dingenloop())
#
#
# def on_unload():
#     task.cancel()
#
#
#
# def geert():
#     print ("geert functie")
#
# def __init__():
#     print ("ini")
#
