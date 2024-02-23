import os
import matplotlib.pyplot as plt
from matplotlib.image import imread
from pyproj import Proj, transform
import socket
import json

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

def process_image(filename, all_waypoints,base_filename):
    lat, lon = map(float, base_filename[:-4].split('_'))
    original_utm_x, original_utm_y = gps_to_utm(lat, lon)
    is_northern = lat >= 0

    image = imread(filename)
    image_height, image_width, _ = image.shape
    fig, ax = plt.subplots()
    ax.imshow(image)

    def onclick(event):
        ix, iy = event.xdata, event.ydata
        ground_res_x = (altitude * sensor_width) / (focal_length * image_width)
        ground_res_y = (altitude * sensor_height) / (focal_length * image_height)
        offset_x = (ix - (image_width / 2)) * ground_res_x
        offset_y = (iy - (image_height / 2)) * ground_res_y
        clicked_utm_x = original_utm_x + offset_x
        clicked_utm_y = original_utm_y - offset_y
        clicked_lat, clicked_lon = utm_to_gps(clicked_utm_x, clicked_utm_y, 43, is_northern)
        all_waypoints.append({"latitude": clicked_lat, "longitude": clicked_lon})
        plt.close(fig)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    
def send_data(data, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(data).encode('utf-8'))
        s.sendall("END_OF_DATA".encode('utf-8'))
        
        
folder_path = "../images/"
waypoints = []

for filename in os.listdir(folder_path):
    if filename.endswith(".jpg"):
        base_filename = os.path.basename(filename)
        process_image(os.path.join(folder_path, filename), waypoints,base_filename)

data_to_send = {"waypoints": waypoints}

# Network parameters - adjust these to suit your setup
host = '127.0.0.1'  # IP address of the receiving computer
port = 6969            # Port number

send_data(data_to_send, host, port)