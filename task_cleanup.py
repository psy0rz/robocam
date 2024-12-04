import asyncio

import config
import analyser
from dobot.dobotfun.pydobot.dobot import DobotException
from robot import robot

rotate = 0


async def goto_overview():
    await robot.move_to_async(config.robot_middle_x - 50, config.robot_middle_y, z=config.robot_ground_z + 220, r=rotate)


async def task():
    await goto_overview()
    return
    while True:

        try:
            await asyncio.sleep(1)
            analyser.mouse_clicked[0] = config.cam_center_x_pixels
            analyser.mouse_clicked[1] = config.cam_center_y_pixels

            if analyser.target_box is not None:
                # step 1: hover camera, next the target will be at the bottom
                x = analyser.target_center_x_mm
                y = analyser.target_center_y_mm

                #look at bottom middle
                analyser.target_box = None
                analyser.mouse_clicked[0]=320
                analyser.mouse_clicked[1]=400
                await robot.move_to_async(x, y, config.robot_ground_z +  130, r=rotate)

                #wait for box
                while analyser.target_box is None:
                    await  asyncio.sleep(0.1)

                x = analyser.target_center_x_mm
                y = analyser.target_center_y_mm

                analyser.target_box = None

                #pak
                await robot.vast_async()
                await robot.move_to_async(x,y,                   config.robot_ground_z + config.calibration_box_height -2, r=rotate)
                await robot.move_to_async(x,y,                   config.robot_ground_z + config.calibration_box_height +100, r=rotate)
                await robot.move_to_async(0, 240, 100, r=rotate)
                await robot.los_async()
                await goto_overview()
                # return

                # await  asyncio.sleep(1)
        except DobotException as e:
            print(f"Ignored {e}")
            await robot.los_async()
            await goto_overview()
            await asyncio.sleep(5)

