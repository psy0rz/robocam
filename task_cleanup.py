import asyncio

import config
import analyser
from robot import robot





async def task():

    while True:

        try:

            # #overview posistion
            robot.move_to(config.robot_middle_x, config.robot_middle_y , z=config.robot_ground_z + 200,r=90)
            await asyncio.sleep(1)

            if analyser.target_box is not None:
                analyser.target_box=None
                robot.suck(True, True)
                robot.move_to(analyser.target_center_x_mm, analyser.target_center_y_mm, config.robot_ground_z+config.calibration_box_height, r=90)
                robot.move_to(analyser.target_center_x_mm, analyser.target_center_y_mm, config.robot_ground_z+config.calibration_box_height+70, r=90)
                robot.move_to(0, -240, 100)
                robot.suck(False, False)


                # await  asyncio.sleep(1)
        except Exception as e:
            print(f"Ignored {e}")


