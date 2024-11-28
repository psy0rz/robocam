import asyncio

import config
import analyser
from robot import robot


async def goto_overview():
    await robot.move_to_async(config.robot_middle_x-50, config.robot_middle_y, z=config.robot_ground_z + 200, r=90)

async def task():

    await goto_overview()

    while True:

        try:

            # #overview posistion
            await asyncio.sleep(1)

            if analyser.target_box is not None:
                analyser.target_box = None
                await robot.vast_async()
                await robot.move_to_async(analyser.target_center_x_mm, analyser.target_center_y_mm,
                                          config.robot_ground_z + config.calibration_box_height-3, r=90)
                await robot.move_to_async(analyser.target_center_x_mm, analyser.target_center_y_mm,
                                          config.robot_ground_z + config.calibration_box_height + 70, r=90)
                await robot.move_to_async(0, 240, 100, r=90)
                await robot.los_async()
                await goto_overview()

                # await  asyncio.sleep(1)
        except Exception as e:
            await robot.los_async()
            await asyncio.sleep(5)

            print(f"Ignored {e}")
