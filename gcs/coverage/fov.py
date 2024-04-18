# #sensor size= 22.3 x 14.9 mm
# #focal length 70mm
# import math
# hafov=2*math.atan(22.3/70)
# hfov=2*25.9*math.tan(hafov/2)
# vafov=2*math.atan(14.9/70)
# vfov=2*25.9*math.tan(vafov/2)
# print(hfov)
# print(vfov)
# print(hfov*vfov)

import math
def calculate_ground_dimensions(sensor_width, sensor_height, focal_length, drone_height):
    # Calculate the adjusted FOV
    adjusted_fov_width = 2 * math.atan(sensor_width / (2 * (focal_length + drone_height)))
    adjusted_fov_height = 2 * math.atan(sensor_height / (2 * (focal_length + drone_height)))

    # Calculate the width and height on the ground
    width_on_ground = 2 * (drone_height + focal_length) * math.tan(adjusted_fov_width / 2)
    height_on_ground = 2 * (drone_height + focal_length) * math.tan(adjusted_fov_height / 2)

    return width_on_ground, height_on_ground

# Example usage:
sensor_width = 22.3  # Replace with actual sensor width in millimeters
sensor_height = 14.9  # Replace with actual sensor height in millimeters
focal_length = 70  # Replace with actual focal length in millimeters
drone_height = 25  # Replace with actual drone height in meters

width_on_ground, height_on_ground = calculate_ground_dimensions(
    sensor_width, sensor_height, focal_length, drone_height
)

print(f"Width on Ground: {width_on_ground:.2f} meters")
print(f"Height on Ground: {height_on_ground:.2f} meters")
