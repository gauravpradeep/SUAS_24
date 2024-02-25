import cv2
import socket
import pickle
import struct
import multiprocessing
import time
from pymavlink import mavutil

SERVER_IP = '192.168.100.198'  # Replace with your server IP
SERVER_PORT = 5050

# Function to capture frames
def capture_frames(frame_queue, mav_queue):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame_queue.put(frame)
        mav_data = get_mavlink_data()  # Function to get MAVLink data
        mav_queue.put(mav_data)

# Function to send frames and MAVLink data and calculate FPS
def send_frames(frame_queue, mav_queue):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    frame_counter = 0
    start_time = time.time()

    while True:
        frame = frame_queue.get()
        mav_data = mav_queue.get()

        data = pickle.dumps((frame, mav_data))
        message_size = struct.pack("<L", len(data))
        try:
            client_socket.sendall(message_size + data)
            frame_counter += 1
            if frame_counter % 10 == 0:
                elapsed_time = time.time() - start_time
                fps = frame_counter / elapsed_time
                print(f"FPS: {fps:.2f}")
        except Exception as e:
            print(f"Error sending frame: {str(e)}")

def get_mavlink_data():
    # Connect to MAVLink
    master = mavutil.mavlink_connection('/dev/ttyACM0')

    # Wait for a heartbeat
    master.wait_heartbeat()

    # Variables to store latitude and longitude
    lat = None
    lon = None

    # Loop to receive messages
    while True:
        msg = master.recv_match(type='GPS_RAW_INT', blocking=True)
        master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
        if msg is not None:
            # Extract latitude and longitude from the message
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            break  # Exit loop once we have the data

    return (lat, lon)

if __name__ == '__main__':
    frame_queue = multiprocessing.Queue()
    mav_queue = multiprocessing.Queue()

    capture_process = multiprocessing.Process(target=capture_frames, args=(frame_queue, mav_queue))
    send_process = multiprocessing.Process(target=send_frames, args=(frame_queue, mav_queue))

    capture_process.start()
    send_process.start()

    capture_process.join()
    send_process.join()