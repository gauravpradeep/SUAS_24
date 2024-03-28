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

'''
Params:
FT_TO_MT : Conversion factor for feet to metres since all altitudes in mission planner are in metres but we will mention altitudes in feet
ALT : Initial takeoff altitude in feet
'''

with open('C:/Users/maxim/gaurav/suas24/cleo_test/scripts/gcs_config.json', 'r') as config_file:
    config = json.load(config_file)

FT_TO_MT = 3.28084
HOST = '0.0.0.0'
RADIUS_OF_EARTH = 6371000.0
TAKEOFF_ALT = config["TAKEOFF_ALT"]
PORT = config["AIRDROPS_PORT"]
AIRDROPS_JSON_FOLDER = config["AIRDROPS_JSON_FOLDER"]
PROXIMITY_THRESHOLD = config["PROXIMITY_THRESHOLD"]


idmavcmd = MAVLink.MAV_CMD.WAYPOINT
id = int(idmavcmd)
home = Locationwp().Set(cs.lat, cs.lng, 0, id)

def haversine_dist(lat1, lon1, lat2, lon2):
    
    '''
    Calcultes and returns the haversine distance, in metres, between two pairs of global coordinates, used to account for curvature of the earth
    (lat1, lon1), (lat2, lon2) : Pair of coordinates between which distance is being calculated 
    '''
    

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = RADIUS_OF_EARTH * c

    return distance

def arm_and_takeoff(alt):

    '''
    
    Arms the drone and takes off to 'alt' feet

    '''

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
    '''
    Loads the main lap waypoints
    Params :
    file_path : path to json from which lap waypoints are loaded
    '''

    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]

def load_coverage_wps(file_path):
    '''
    Loads the calculated intermediate waypoints for coverage
    Params :
    file_path : path to json from where intermediate coverage waypoints are loaded
    '''
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]

def load_airdrop_wps(file_path):

    '''
    Loads set of airdrop coordinates as received from the ODLC computer via ethernet
    Params : 
    file_path : path to json to load airdrop coordinates
    '''

    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]

def check_status(final_lat,final_lon,no_of_waypoints):

    '''
    Checks whether the drone is within the distance threshold to the given lat,lon
    Params:
    final_lat, final_long : coordinates of last point of a mission at any time 
    '''
    global proximity_threshold

    while True:
        if haversine_dist(cs.lat,cs.lng,final_lat,final_lon) <= PROXIMITY_THRESHOLD and cs.wpno == no_of_waypoints:
            break
        else:
            print("Current waypoint : ",cs.wpno)
            Script.Sleep(1000)

def start_mission(mission):
    '''
    Checks whether the drone is in a mission
    '''
    # upload_mission(mission)
    Script.Sleep(500)
    print("Starting Mission")
    Script.ChangeMode('Auto')
    check_status(mission[-1]['latitude'],mission[-1]['longitude'],len(mission))

def upload_mission(waypoints):

    '''
    
    Uploads the set of waypoints as a mission on to the drone and keeps control in the function until these set of waypoints are completed
    
    '''

    print("Uploading initial waypoints + coverage waypoints")
    global id, home

    MAV.setWPTotal(len(waypoints) + 1)
    MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

    for i, wp in enumerate(waypoints):
        
        waypoint = Locationwp().Set(wp['latitude'], wp['longitude'], wp['altitude']/FT_TO_MT, id)
        MAV.setWP(waypoint, i + 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

    MAV.setWPACK()
    print("No of waypoints : ",MAV.getWPCount())
    Script.Sleep(1000)

def perdorm_airdrop(airdrop_wp,pin_number,pwm_value):

    '''
    Takes one airdrop coordinate and performs drop of payload attaced to specified servo pin
    '''
    Script.ChangeMode("Guided")
    item = MissionPlanner.Utilities.Locationwp() # creating waypoint
    Locationwp.lat.SetValue(item,airdrop_wp['latitude']) # sets latitude
    Locationwp.lng.SetValue(item,airdrop_wp['longitude']) # sets longitude
    Locationwp.alt.SetValue(item,30/FT_TO_MT) # sets altitude
    MAV.setGuidedModeWP(item)
    print("Found ODLC object - Going to drop dem bombs")
    check_status(airdrop_wp['latitude'],airdrop_wp['longitude'])
    Script.Sleep(2000)
    print("Sending servo command")
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO,pin_number,pwm_value,0,0,0,0,0)
    print("Sent Servo Command")
    Script.Sleep(3000)

def start_server(host, port, save_path):

    '''
    Starts listening on specified port via ethernet connection to receive airdrop coords from ODLC computer, saves it in json format and closes socket connection
    '''

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
                        part = part.replace("END_OF_DATA".encode('utf-8'), b'')
                        data += part
                        break
                    data += part

                json_data = json.loads(data.decode('utf-8'))
                print("Received data:")
                print(json.dumps(json_data, indent=4))

                file_path = os.path.join(save_path, f"airdrops_suas.json")
                with open(file_path, 'w') as file:
                    json.dump(json_data, file, indent=4)
                print(f"Data saved to {file_path}")
                conn.close()
                break
            break
        s.close()
        print("airdrop json created")

def come_home():
    Script.ChangeMode('RTL')
    print("Coming Home ")
    
def main():
    
    mission = load_waypoints(config["LAP_WAYPOINTS_JSON"])
    coverage_waypoints = load_coverage_wps(config["COVERAGE_WAYPOINTS_JSON"])
    mission.extend(coverage_waypoints)
    arm_and_takeoff(TAKEOFF_ALT)
    upload_mission(mission)
    start_mission(mission)
    # start_server(HOST, PORT, AIRDROPS_JSON_FOLDER)
    # airdrop_wps_json = os.path.join(AIRDROPS_JSON_FOLDER,config["AIRDROPS_JSON_FILENAME"])
    # airdrop_wps = load_airdrop_wps(airdrop_wps_json)
    # perdorm_airdrop(airdrop_wps[0],9,400)
     
    come_home()

main()
