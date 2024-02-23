import sys
import math
import clr
import time
import System
from System import Byte
import json
clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities") # includes the Utilities class
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink") # includes the Utilities class
import MAVLink
import socket
import json
import os


# '''

# Params:
# M_TO_FT : Conversion factor for feet to metres since all altitudes in mission planner are in metres but we will mention altitudes in feet
# ALT : Initial takeoff altitude

# '''


FT_TO_MT=3.28084
ALT=100
count=0

def haversine_dist(lat1, lon1, lat2, lon2):
    R = 6371000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

def arm_and_takeoff(alt):
    Script.ChangeMode('Stabilize')
    Script.Sleep(1000)
    print("Arming Motors")
    MAV.doARM(True)

    while not cs.armed:
        MAV.doARM(True)
        Script.Sleep(1000)

    print(f"Taking off to {alt} feet")
    Script.ChangeMode('Guided')
    MAV.doCommand(MAVLink.MAV_CMD.TAKEOFF,0,0,0,0,0,0,alt/FT_TO_MT)
    while cs.alt < 0.95*alt/FT_TO_MT:
        Script.Sleep(500)

    print("Reached Target Altitude")

def load_waypoints(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]

def load_coverage_wps(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]

def load_airdrop_wps(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]

def check_status(final_lat,final_lon):

    while True:
        current_location = f"{cs.lat},{cs.lng}"
        if haversine_dist(cs.lat,cs.lng,final_lat,final_lon) <= 0.5:
            break
        else:
            
            Script.Sleep(500)

def upload_mission(waypoints):
    print("Uploading initial waypoints + coverage waypoints")
    global count
    idmavcmd = MAVLink.MAV_CMD.WAYPOINT
    id = int(idmavcmd)

    home = Locationwp().Set(cs.lat, cs.lng, 0, id)

    MAV.setWPTotal(len(waypoints) + 1)
    MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

    # Upload waypoints from JSON file
    for i, wp in enumerate(waypoints):
        count+=1
        waypoint = Locationwp().Set(wp['latitude'], wp['longitude'], wp['altitude']/FT_TO_MT, id)
        MAV.setWP(waypoint, i + 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

    MAV.setWPACK()
    Script.Sleep(2000)

def airdrops(airdrop_wps):
    Script.ChangeMode("Guided")
    item = MissionPlanner.Utilities.Locationwp() # creating waypoint
    Locationwp.lat.SetValue(item,airdrop_wps['latitude']) # sets latitude
    Locationwp.lng.SetValue(item,airdrop_wps['longitude']) # sets longitude
    Locationwp.alt.SetValue(item,50/FT_TO_MT) # sets altitude

    MAV.setGuidedModeWP(item)

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
                file_path = os.path.join(save_path, f"airdrops_suas.json")
                with open(file_path, 'w') as file:
                    json.dump(json_data, file, indent=4)
                print(f"Data saved to {file_path}")
                conn.close()
                break
            break
        s.close()
        print("airdrop json created")

waypoints_json = 'C:/Users/maxim/gaurav/suas24/cleo_test/missions/waypoints/test_wps.json'
coverage_wps_json = 'C:/Users/maxim/gaurav/suas24/cleo_test/missions/coverage_wps/test_coverage_wps.json'

mission = load_waypoints(waypoints_json)
coverage_waypoints = load_coverage_wps(coverage_wps_json)
mission.extend(coverage_waypoints)

arm_and_takeoff(50)
upload_mission(mission)
print("Starting Mission")
Script.ChangeMode('Auto')
check_status(mission[-1]['latitude'],mission[-1]['longitude'])


host = '0.0.0.0'
port = 5051 
save_folder = "C:/Users/maxim/gaurav/suas24/cleo_test/missions/airdrop_coords" 

start_server(host, port, save_folder)
airdrop_wps_json = 'C:/Users/maxim/gaurav/suas24/cleo_test/missions/airdrop_coords/airdrops_suas.json'
airdrop_wps = load_airdrop_wps(airdrop_wps_json)
print("Found ODLC object - Going to drop dem bombs")
airdrops(airdrop_wps[0])
check_status(airdrop_wps[0]['latitude'],airdrop_wps[0]['longitude'])
Script.Sleep(2000)
print("Sending servo command")
MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO,9,400,0,0,0,0,0)
print("sent servo command")
Script.Sleep(4000)
Script.ChangeMode('RTL')
print("Coming Home ")