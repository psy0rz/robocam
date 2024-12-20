import asyncio

import config
import analyser
from dobot.dobotfun.pydobot.dobot import DobotException
from robot import robot

rotate = 0


async def goto_overview():
    await robot.move_to_async(config.robot_middle_x - 50, config.robot_middle_y, z=config.robot_ground_z + 220,
                              r=rotate)


async def task():
    robot.suck(False, False)
    # robot.home()

    while True:

        try:

            await goto_overview()

            target = await analyser.wait_for_target(config.cam_center_x_pixels, config.cam_center_y_pixels, 3)

            if target:
                x, y = target

                # zoom in
                await robot.move_to_async(x, y, config.robot_ground_z + 120, r=rotate)

                # target is at bottom now
                target = await analyser.wait_for_target(320, 400, 3)
                if target:
                    x, y = target

                    # pak
                    await robot.move_to_async(x, y, config.robot_ground_z + config.calibration_box_height - 4, r=rotate)
                    await robot.vast_async()
                    await robot.move_to_async(x, y, config.robot_ground_z + config.calibration_box_height + 100,
                                              r=rotate)

                    # pleur weg
                    await robot.move_to_async(0, 240, 100, r=rotate)
                    await robot.los_async()

            await goto_overview()

        except DobotException as e:
            print(f"Error, waiting for retry...")
            await asyncio.sleep(5)
