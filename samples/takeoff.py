import sys
import math
import clr
import time
import System
from System import Byte

clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities") # includes the Utilities class
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink") # includes the Utilities class
import MAVLink

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

takeoff(50)