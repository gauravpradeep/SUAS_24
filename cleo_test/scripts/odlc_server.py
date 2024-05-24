import cv2
import socket
import pickle
import struct
import os

SERVER_IP = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 5050
IMAGE_FOLDER = 'testimages'

def receive_frames():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)

    print("Server is listening...")
    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    try:
        while True:
            data = b''
            payload_size = struct.calcsize("<L")

            while len(data) < payload_size:
                data += conn.recv(4096)

            packed_msg_size = data[:payload_size]
            
            data = data[payload_size:]
            msg_size = struct.unpack("<L", packed_msg_size)[0]

            while len(data) < msg_size:
                data += conn.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame, mav_data = pickle.loads(frame_data)
            save_image(frame, mav_data)  

    finally:
        conn.close()
        server_socket.close()



def save_image(frame, mav_data):
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    lat, lon = mav_data
    filename = f"{lat}_{lon}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)
    cv2.imwrite(filepath, frame)
    print(f"Image saved: {filename}")

if __name__ == '__main__':
    receive_frames()