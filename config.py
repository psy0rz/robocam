import robot

# robot middle in real word, and when it touches the ground
robot_middle_x = 300
robot_middle_y = 0
robot_ground_z = -50
suction_cup_diameter=20
robot_min_radius=225
robot_max_radius=360

# pixel center of cam
cam_center_x_pixels = 320
cam_center_y_pixels = 240
cam_lag_s = 0.25

calibration_box_height=25




if robot.id=='36ffd9054155383410591257':
    robot_name="Robot 1"

    # results of calibrate-offsets:
    cam_offset_x=52.96559143066406
    cam_offset_y=1.0864660739898682
    cam_tilt_x_mm=0.0127410888671875
    cam_tilt_y_mm=-0.026492351666092873
    cam_tilt_base=-25


    #result of calibrate-camera:
    cam_offset_z=123.09851837158203
    low_cam_height=68.09851837158203
    low_x_pix_per_mm=8.325435638427734
