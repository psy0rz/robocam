import asyncio

import config
import analyser
from robot import robot





async def task():

    while True:

        #overview posistion
        robot.move_to_nowait(config.robot_middle_x, config.robot_middle_y , z=config.robot_ground_z + 150, r=90)
        await asyncio.sleep(1)

        if analyser.target_box is not None:
            #move camera closer to target
            robot.move_to_nowait(analyser.target_center_x_mm, analyser.target_center_y_mm, config.robot_ground_z+config.calibration_box_height)
            analyser.target_center_x_mm = None
            await  asyncio.sleep(1)

