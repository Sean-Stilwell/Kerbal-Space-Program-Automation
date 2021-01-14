# This script is prepared for a 2-stage to orbit rocket to place it into an
# approximately ~100 km orbit above the surface. After a given amount of time,
# it then automatically re-enters and lands.

import krpc
import time

connection = krpc.connect()
vessel = connection.space_center.active_vessel

ORBIT_DURATION = 400 # Number of seconds the spacecraft will be in orbit
DESIRED_ORBIT_HEADING = 45 # Angle to be achieved in orbit (90/270 = equatorial, 0/180 = polar)

control = vessel.control
ap = vessel.auto_pilot
orbit = vessel.orbit
flight = vessel.flight()

# Prepares a rocket to be launched by engaging autopilot to fly vertically
def prepareForLaunch():
    ap.engage()
    ap.target_pitch = 90
    ap.target_heading = DESIRED_ORBIT_HEADING
    control.throttle = 1
    print("Vessel is prepared to launch, computer has control.")

# Controls the rocket through to 80000 metres
def firstStage():
    print("Lift off of Iris!")
    while (orbit.apoapsis_altitude < 80000):
        # Ensuring that the speed is not overly fast at a low altitude
        if (flight.mean_altitude < 10000 and flight.speed > 300):
            control.throttle = 0.75
            print("Iris is throttling down to avoid excessive spead")
        else:
            control.throttle = 1
        # Angling the spacecraft based on altitude
        if (flight.mean_altitude > 60000):
            ap.target_pitch = 0
            print("Iris is now flying exactly horizontal.")
        elif (flight.mean_altitude > 50000):
            ap.target_pitch = 5
        elif (flight.mean_altitude > 36000):
            ap.target_pitch = 10
        elif (flight.mean_altitude > 26000):
            ap.target_pitch = 30
        elif (flight.mean_altitude > 18000):
            ap.target_pitch = 50
        elif (flight.mean_altitude > 8000):
            ap.target_pitch = 70
        else:
            ap.target_pitch = 90
        time.sleep(0.5)
    control.throttle = 0
    time.sleep(2)

# Ensures nothing happens during the coast phase to apoapsis
def coast():
    print("Iris is now coasting to its highest point, where it will prepare for circularizing")
    while flight.mean_altitude < orbit.apoapsis_altitude * 0.93:
        ap.target_pitch = 0
        control.throttle = 0
        time.sleep(0.5)

# Initial circularization of the spacecraft
def circularize():
    print("Iris has commenced its circularization burn")
    aps = orbit.apoapsis_altitude
    while (orbit.periapsis_altitude < aps * 0.95):
        ap.target_pitch = 5
        control.throttle = 1
        time.sleep(0.5)

# In orbit
def orbit():
    print ("Iris has achieved a stable orbit. It will continue making small adjustments to ensure good altitude is maintained")
    seconds = 0
    ap.disengage()
    control.sas = True
    while seconds < ORBIT_DURATION * 4 and abs(orbit.periapsis_altitude - orbit.apoapsis_altitude) > 2500 and vessel.resources.amount('LiquidFuel') > 225:
        # If there is significant variation between periapsis (per) and apoapsis (apo), and enough fuel, we'll improve circularization
        # If close to per, this code runs to lower the apo
        if orbit.time_to_periapsis < 30:
            control.sas_mode = control.sas_mode.retrograde
            if abs(flight.pitch) < 1 and (orbit.time_to_periapsis < 10 or control.throttle == 0.5):
                control.throttle = 0.5
            else:
                control.throttle = 0
                time.sleep(5)

        # If close to aps, this code runs to raise the per.
        elif orbit.time_to_apoapsis < 30:
            control.sas_mode = control.sas_mode.prograde
            if abs(flight.pitch) < 1 and (orbit.time_to_apoapsis < 10 or control.throttle == 0.5):
                control.throttle = 0.5
            else:
                control.throttle = 0
                time.sleep(5)
        # If neither of those conditions are true, mwe keep the rocket stationary
        else:
            control.throttle = 0
        seconds = seconds + 1
        time.sleep(0.25)
        if seconds % 100 == 0:
            print("T +" +str(seconds))

# At end of flight, reduces orbit to sub 50,000 for re-entry
def reenter():
    print("The capsule is beginning its entry burn to re-enter the Earth's atmosphere")
    control.sas_mode = control.sas_mode.retrograde
    time.sleep(5)
    while (orbit.periapsis_altitude > 50000):
        # Ensures orientation is good before 
        control.throttle = 1
        time.sleep(0.5)
    control.throttle = 0
    time.sleep(2)

# During and after reentry, controls parachute and landing
def land():
    print("The capsule has burned sufficiently to re-enter the atmosphere and is now coasting")
    while (flight.mean_altitude > 11000):
        time.sleep(0.5)
    print("The capsule is deploying its drogue chutes to slow itself down to safe speeds")
    control.activate_next_stage() # Drogue chute deploy
    while (flight.mean_altitude > 5000):
        time.sleep(0.5)
    print("The capsule is now deploying its main chutes to prepare for landing")
    control.activate_next_stage() # Main chute deploy

prepareForLaunch() # Sets up for launch
control.activate_next_stage() # Blast off
firstStage() # Ascent to space
control.activate_next_stage() # Starts second stage
control.rcs = True
coast() # Coasts to highest point
circularize() # Makes the orbit approximately a circle
orbit() # Adjusts the orbit of the ship to ensure it is a circle
reenter()
vessel.control.activate_next_stage()
land()
