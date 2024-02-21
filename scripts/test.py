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

M_TO_FT=3.28084

def takeoff(alt):
    Script.ChangeMode('Stabilize')
    Script.Sleep(1000)
    MAV.doARM(True)

    while not cs.armed:
        MAV.doARM(True)
        Script.Sleep(1000)

    Script.ChangeMode('Guided')
    MAV.doCommand(MAVLink.MAV_CMD.TAKEOFF,0,0,0,0,0,0,alt)
    while cs.alt < alt:
        Script.Sleep(1000)

altitude=50
takeoff(altitude)

def load_waypoints_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]

json_file_path = 'C:/Users/maxim/gaurav/scripts/gps_centroids.json'

waypoints = load_waypoints_from_json(json_file_path)

idmavcmd = MAVLink.MAV_CMD.WAYPOINT
id = int(idmavcmd)

home = Locationwp().Set(cs.lat, cs.lng, 0, id)

MAV.setWPTotal(len(waypoints) + 1)

MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

# Upload waypoints from JSON file
for i, wp in enumerate(waypoints):
    waypoint = Locationwp().Set(wp['latitude'], wp['longitude'], wp['altitude']/M_TO_FT, id)
    # print("upload wp ",i+1)
    MAV.setWP(waypoint, i + 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

# print("final ack")
MAV.setWPACK()

Script.Sleep(2000)
Script.ChangeMode('Auto')
