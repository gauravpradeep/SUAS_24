import matplotlib.pyplot as plt
from matplotlib.image import imread
from pyproj import Proj, transform
from PIL import Image
import sys

focal_length = 0.01  
sensor_width = 0.014  
sensor_height = 0.007   
altitude = 9.15

def gps_to_utm(lat, lon):
    proj_utm = Proj(proj='utm', zone=43, ellps='WGS84')
    utm_x, utm_y = proj_utm(lon, lat)
    return utm_x, utm_y

def utm_to_gps(utm_x, utm_y, zone, northern):
    proj_utm = Proj(proj='utm', zone=zone, ellps='WGS84', south=not northern)
    lon, lat = proj_utm(utm_x, utm_y, inverse=True)
    return lat, lon

def onclick(event):
    ix, iy = event.xdata, event.ydata
    print(f"Clicked coordinates: (x={ix}, y={iy})")

    ground_res_x = (altitude * sensor_width) / (focal_length * image_width)
    ground_res_y = (altitude * sensor_height) / (focal_length * image_height)

    offset_x = (ix - (image_width / 2)) * ground_res_x
    offset_y = (iy - (image_height / 2)) * ground_res_y

    clicked_utm_x = original_utm_x + offset_x
    clicked_utm_y = original_utm_y - offset_y 
    clicked_lat, clicked_lon = utm_to_gps(clicked_utm_x, clicked_utm_y, 43, is_northern)

    print(f"GPS Coordinates of clicked point: Latitude: {clicked_lat}, Longitude: {clicked_lon}")
    sys.exit(0)

filename = "13.347727_74.792189.jpg"  
lat, lon = map(float, filename[:-4].split('_'))  
print(lat,lon)
original_utm_x, original_utm_y = gps_to_utm(lat, lon)
is_northern = lat >= 0

image = imread(filename)
image_height, image_width, _ = image.shape
fig, ax = plt.subplots()
ax.imshow(image)

cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()
