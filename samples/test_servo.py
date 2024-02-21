import sys
import math
import clr
import time
import System
clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities") # includes the Utilities class
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink") # includes the Utilities class
import MAVLink
# for i in range (10):
MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO,9,400,0,0,0,0,0)
