# robot middle in real word, and when it touches the ground
robot_middle_x = (190 + 380) / 2
robot_middle_y = 0
robot_ground_z = -48

# pixel center of cam
cam_center_x_pixels = 320
cam_center_y_pixels = 240
cam_lag_s = 0.25

# approximate cam x, y offset (for auto calibrating)
cam_approx_offset_x = 50
cam_approx_offset_y = 0

### x and y offset calibration:
# results of calibrate-offsets:
cam_offset_x=51.63000000000005
cam_offset_y=2.5399999999999965

### camera calibration
# size of camera calibration square
calibration_square=50
calibration_box_height=23

#result of calibrate-camera:
cam_offset_z=118.90998077392578
low_cam_height=70.90998077392578
low_x_pix_per_mm=7.9345383644104
