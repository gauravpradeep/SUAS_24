import cv2
import socket
import pickle
import struct
import multiprocessing
import time

SERVER_IP = '192.168.42.198'  # Replace with your server IP
SERVER_PORT = 5050

# Function to capture frames
def capture_frames(frame_queue):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame_queue.put(frame)

# Function to send frames and calculate FPS
def send_frames(frame_queue):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    frame_counter = 0
    start_time = time.time()

    while True:
        frame = frame_queue.get()
        data = pickle.dumps(frame)
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

if __name__ == '__main__':
    frame_queue = multiprocessing.Queue()

    capture_process = multiprocessing.Process(target=capture_frames, args=(frame_queue,))
    send_process = multiprocessing.Process(target=send_frames, args=(frame_queue,))

    capture_process.start()
    send_process.start()

    capture_process.join()
    send_process.join()