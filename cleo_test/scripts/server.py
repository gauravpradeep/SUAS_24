import socket
import cv2
import pickle
import struct
from pymavlink import mavutil
import shutil
import time


port = '/dev/ttyACM0'  # Adjust the port name as needed

# Start a connection on the specified serial port
the_connection = mavutil.mavlink_connection(port)

SERVER_PORT = 5050
# Create a socket to listen for incoming connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', SERVER_PORT))  # Replace with your desired port
server_socket.listen(10)
image_counter = 1
the_connection.wait_heartbeat()
print("Heartbeat received from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    data = b""
    payload_size = struct.calcsize("<L")

    while True:
        while len(data) < payload_size:
            data += client_socket.recv(8192*3)


        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("<L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(8192*3)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Deserialize the frame and save it to a folder
        frame = pickle.loads(frame_data)
        msg1 = the_connection.recv_match(type='GPS_RAW_INT', blocking=True)
        the_connection.mav.request_data_stream_send(the_connection.target_system, the_connection.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
        if msg1 is not None:
            lat = (msg1.lat/1e7)
            lon = (msg1.lon/1e7)
            alt = (msg1.alt)
        image_counter += 1
        image_filename = f"/home/naman/testimages/{image_counter}_{lat}_{lon}.jpg"

        if cv2.imwrite(image_filename, frame):  # Save the image
            print(f"Saved image to {image_filename}")
        else:
            print(f"Failed to save image to {image_filename}")
        
        time.sleep(2)
        
        

# Close the server socket when done
server_socket.close()