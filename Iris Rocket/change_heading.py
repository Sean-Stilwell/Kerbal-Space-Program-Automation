import krpc
import time

# INCOMPLETE

# Given the ship's current heading and the desired one, returns
# True if a left turn would be ideal and False if a right turn
# would be ideal.
def leftOrRight(current, desired):
    if abs(desired - current) > 90:
        return False
    else:
        return True
    

connection = krpc.connect()
vessel = connection.space_center.active_vessel
control = vessel.control
ap = vessel.auto_pilot
flight = vessel.flight()
