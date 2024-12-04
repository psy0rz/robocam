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
    # return
    while True:

        try:
            if await analyser.wait_for_target(config.cam_center_x_pixels, config.cam_center_y_pixels, 3):
                x = analyser.target_center_x_mm
                y = analyser.target_center_y_mm

                #look at bottom middle
                await robot.move_to_async(x, y, config.robot_ground_z +  120, r=rotate)

                if await analyser.wait_for_target(320,400, 3):

                    x = analyser.target_center_x_mm
                    y = analyser.target_center_y_mm

                    #pak
                    await robot.vast_async()
                    await robot.move_to_async(x,y,                   config.robot_ground_z + config.calibration_box_height -2, r=rotate)
                    await robot.move_to_async(x,y,                   config.robot_ground_z + config.calibration_box_height +100, r=rotate)
                    await robot.move_to_async(0, 240, 100, r=rotate)
                    await robot.los_async()

            await goto_overview()



        except DobotException as e:
            print(f"Ignored {e}")
            await robot.los_async()
            await goto_overview()
            await asyncio.sleep(5)




