import socket
import json
import os

def start_server(host, port, save_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = b''
                while True:
                    part = conn.recv(1024)
                    if "END_OF_DATA".encode('utf-8') in part:
                        # Remove the end-of-data message from the data
                        part = part.replace("END_OF_DATA".encode('utf-8'), b'')
                        data += part
                        break
                    data += part

                json_data = json.loads(data.decode('utf-8'))
                print("Received data:")
                print(json.dumps(json_data, indent=4))

                # Save the data as a JSON file
                file_path = os.path.join(save_path, f"airdrops.json")
                with open(file_path, 'w') as file:
                    json.dump(json_data, file, indent=4)
                print(f"Data saved to {file_path}")
                conn.close()
                break
            break
        s.close()

# Network parameters - adjust these to suit your setup
host = '0.0.0.0'  # Listen on all available interfaces
port = 6969      # The port number to listen on

# Specify the folder where you want to save the JSON files
save_folder = "../images"  # Change this to your desired folder path

start_server(host, port, save_folder)
