import socket
import time

HOST = '0.0.0.0'  
PORT = 25565      


gps_data = [
"$GPGGA,092750.000,5321.6802,N,00630.3372,W,1,8,1.03,61.7,M,55.2,M,,*76",
"$GPGSA,A,3,10,07,05,02,29,04,08,13,,,,,1.72,1.03,1.38*0A",
"$GPGSV,3,1,11,10,63,137,17,07,61,098,15,05,59,290,20,08,54,157,30*70",
"$GPGSV,3,2,11,02,39,223,19,13,28,070,17,26,23,252,,04,14,186,14*79",
"$GPGSV,3,3,11,29,09,301,24,16,09,020,,36,,,*76",
"$GPRMC,092750.000,A,5321.6802,N,00630.3372,W,0.02,31.66,280511,,,A*43",
"$GPGGA,092751.000,5321.6802,N,00630.3371,W,1,8,1.03,61.7,M,55.3,M,,*75",
"$GPGSA,A,3,10,07,05,02,29,04,08,13,,,,,1.72,1.03,1.38*0A",
"$GPGSV,3,1,11,10,63,137,17,07,61,098,15,05,59,290,20,08,54,157,30*70",
"$GPGSV,3,2,11,02,39,223,16,13,28,070,17,26,23,252,,04,14,186,15*77",
"$GPGSV,3,3,11,29,09,301,24,16,09,020,,36,,,*76",
"$GPRMC,092751.000,A,5321.6802,N,00630.3371,W,0.06,31.66,280511,,,A*45"
]

def create_server(host=HOST, port=PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Listening on {host}:{port}")
    return server_socket

def send_gps_data(client_socket):
    try:
        data_with_crlf = ""
        for data in gps_data:
            # Add CRLF to the end of each GPS data string
            data_with_crlf += data + '\r\n'
            # break
        time.sleep(2)  # Wait for 2 seconds before sending the next data
        client_socket.sendall(data_with_crlf.encode('utf-8'))
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        client_socket.close()


# Main function to run the server
def main():
    server_socket = create_server()
    try:
        while True:
            print("Waiting for a connection...")
            client_socket, addr = server_socket.accept()
            print(f"Connected to {addr}")
            send_gps_data(client_socket)
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()


# Note: This script will terminate after sending the GPS data to one client.
# To handle multiple clients, you would need to implement a loop to accept new connections.
