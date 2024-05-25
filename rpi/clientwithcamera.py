#!/usr/bin/env python

import logging
import locale
import os
import subprocess
import sys
import time
import socket
from math import pi
import gphoto2 as gp
from pymavlink import mavutil

def main():
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
   
    # Server host and port
    SERVER_HOST = '192.168.153.198'  # Replace with server IP address
    SERVER_PORT = 12345
   
    while True:
        print('Capturing image')
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
        print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
       
        # Generate custom filename based on MAVLink data
        mav_data = get_mavlink_data()  # Function to get MAVLink data
        filename = generate_filename(mav_data)
        target = os.path.join('testimages', filename + '.jpg')
       
        print('Copying image to', target)
        camera_file = camera.file_get(
            file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(target)
       
        # Send image to server
        send_image_to_server(target, filename, SERVER_HOST, SERVER_PORT)
         # Add a delay between captures (optional)
   
    camera.exit()
    return 0

def generate_filename(mav_data):
    lat, lon, alt, yaw = mav_data
    filename = f"{lat}_{lon}_{alt}_{yaw}"
    return filename

def send_image_to_server(image_path, filename, server_host, server_port):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server
        client_socket.connect((server_host, server_port))
       
        # Send image name length
        client_socket.send(len(filename).to_bytes(4, byteorder='big'))
        # Send image name
        client_socket.send(filename.encode())
        # Send image size
        image_size = os.path.getsize(image_path)
        client_socket.send(image_size.to_bytes(4, byteorder='big'))
        # Send image data
        with open(image_path, 'rb') as f:
            image_data = f.read()
            client_socket.sendall(image_data)
       
        print("Image sent to server:", filename)
       
        # Close the connection
        client_socket.close()
    except Exception as e:
        print("Error sending image to server:", e)

def get_mavlink_data():
    # Connect to MAVLink
    master = mavutil.mavlink_connection('/dev/ttyACM0')

    # Wait for a heartbeat
    master.wait_heartbeat()

    # Variables to store latitude, longitude, altitude, and yaw
    lat = None
    lon = None
    alt = None
    yaw = None

    # Loop to receive messages
    while True:
        msg = master.recv_match(type='GPS_RAW_INT', blocking=True)
        master.mav.request_data_stream_send(master.target_system, master.target_component,
                                            mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
        if msg is not None:
            # Extract latitude, longitude, and altitude from the message
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.alt / 1e3  # Convert altitude to meters
            break  # Exit loop once we have the data

    while True:
        msg = master.recv_match(type='ATTITUDE', blocking=True)
        if msg is not None:
            # Extract yaw from the attitude message
            yaw = msg.yaw*180/pi
            break

    return (lat, lon, alt, yaw)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
