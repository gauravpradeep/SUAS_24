import clr
clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MAVLink")
# from System import Func
import MAVLink
from MAVLink import mavlink_set_position_target_local_ned_t

print('Start Script')
Script.ChangeMode("Guided")
command = mavlink_set_position_target_local_ned_t()

mavlink_set_position_target_local_ned_t.coordinate_frame.SetValue(command, 9)
mavlink_set_position_target_local_ned_t.type_mask.SetValue(command, 0b0000111111111000)
mavlink_set_position_target_local_ned_t.x.SetValue(command, -5) 
mavlink_set_position_target_local_ned_t.y.SetValue(command, 3)
mavlink_set_position_target_local_ned_t.z.SetValue(command, 4) 

target_system = 1
target_component = 1

MAV.sendPacket(command, target_system, target_component)
print('Script End')