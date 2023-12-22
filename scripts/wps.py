import sys
import math
import clr
import time
import System
import json  # Import json module
from System import Byte

clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities") 
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink") 
import MAVLink

# Function to load waypoints from a JSON file
def load_waypoints_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["waypoints"]
M_TO_FT=3.28084
# Path to the JSON file containing waypoints
json_file_path = 'C:/Users/maxim/gaurav/scripts/aco_centroids.json'

# Load waypoints from the JSON file
waypoints = load_waypoints_from_json(json_file_path)

idmavcmd = MAVLink.MAV_CMD.WAYPOINT
id = int(idmavcmd)

# Assuming home coordinates are set manually or retrieved from another source
home = Locationwp().Set(cs.lat, cs.lng, 0, id)

print "set wp total"
MAV.setWPTotal(len(waypoints) + 1)

print "upload home - reset on arm"
MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

# Upload waypoints from JSON file
for i, wp in enumerate(waypoints):
    waypoint = Locationwp().Set(wp['latitude'], wp['longitude'], wp['altitude']/M_TO_FT, id)
    print "upload wp ",i+1
    MAV.setWP(waypoint, i + 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

print "final ack"
MAV.setWPACK()

print "done"
