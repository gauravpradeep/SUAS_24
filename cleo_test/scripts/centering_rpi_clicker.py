import logging
import locale
import os
import socket
from math import pi
import gphoto2 as gp
from pymavlink import mavutil


def generate_filename(mav_data):
    lat, lon, alt, yaw = mav_data
    filename = f"{lat}_{lon}_{alt}_{yaw}"
    return filename

def send_image_to_server(image_path, filename, server_host, server_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))
        client_socket.send(len(filename).to_bytes(4, byteorder='big'))
        client_socket.send(filename.encode())
        image_size = os.path.getsize(image_path)
        client_socket.send(image_size.to_bytes(4, byteorder='big'))
        with open(image_path, 'rb') as f:
            image_data = f.read()
            client_socket.sendall(image_data)
       
        print("Image sent to server:", filename)
        client_socket.close()
    
    except Exception as e:
        print("Error sending image to server:", e)

def get_mavlink_data():
    master = mavutil.mavlink_connection('/dev/ttyACM0')

    master.wait_heartbeat()
    
    lat = None
    lon = None
    alt = None
    yaw = None

    while True:
        msg = master.recv_match(type='GPS_RAW_INT', blocking=True)
        if msg is not None:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.alt / 1e3
            break
    while True:
        msg = master.recv_match(type='ATTITUDE', blocking=True)
        if msg is not None:
            yaw = msg.yaw * 180 / pi
            break

    return (lat, lon, alt, yaw)

def main():
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    camera = gp.Camera()
    camera.init()

    SERVER_HOST = '192.168.153.198'
    SERVER_PORT = 12345

    print('Capturing image')
    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

    mav_data = get_mavlink_data()
    filename = generate_filename(mav_data)
    target = os.path.join('testimages', filename + '.jpg')

    print('Copying image to', target)
    camera_file = camera.file_get(
        file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
    camera_file.save(target)

    send_image_to_server(target, filename, SERVER_HOST, SERVER_PORT)
    os.remove(target)

    camera.exit()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
