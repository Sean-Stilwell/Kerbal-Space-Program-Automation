# This script is prepared for the Iris 2-stage to orbit rocket to place cargo into an
# approximately ~100 km orbit above the surface. This will leave the rocket
# in orbit until the user takes manual action or another script is used.

# Additionally, this script is used by most other scripts to facilitate launches

import krpc
import time

# Code that runs automatically upon running script
connection = krpc.connect() # Establishes a connection to the game
vessel = connection.space_center.active_vessel # Variable for the vessel that's currently in use
control = vessel.control # Variable for the vessel's controls
ap = vessel.auto_pilot # Variable for programming the vessel's autopilot
flight = vessel.flight() # Variable for flight dynamics of the vessel

DESIRED_ORBIT_HEADING = 45 # Angle to be achieved in orbit (90/270 = equatorial, 0/180 = polar)
DESIRED_ORBIT_ALTITUDE = 80000 # Desired altitude of the orbit (Default 80000)

# Prepares a rocket for liftoff
def prepare_for_launch():
    ap.engage() # Activates the autopilot for use in flight
    ap.target_pitch = 90 # Tells the autopilot to aim vertically
    ap.target_heading = DESIRED_ORBIT_HEADING # Tells the autopilot what the preferred heading is
    control.throttle = 1 # Throttles the rocket up
    print("Vessel is prepared to launch!")

# Countdown (for fun) from n to 0.
def countdown(n):
    if (n < 0): # Handles an invalid input
        n = 10
    while (n > 0): # Counts down from n to 0
        print("T -" + str(n))
        n = n - 1
        time.sleep(1)

# Controls the rocket through to its desired orbit height
def first_stage():
    print ("Lift Off!")
    
    while (vessel.orbit.apoapsis_altitude < DESIRED_ORBIT_ALTITUDE):
        # The angling of the spacecraft is approximated by these formulas (not perfect)
        # This allows for a rough gravity turn to occur
        alt = flight.mean_altitude
        if alt < 18000: # This formula slightly pitches below 18000
            ap.target_pitch = 88.604 - (0.0014 * alt)
        elif alt < 36000: # This formula causes more rapid pitching below 36000
            ap.target_pitch = 102.61 - (0.0027 * alt)
        elif alt < 60000: # This formula gradually continues pitching until 0
            ap.target_pitch = 25.092 - (0.0004 * alt)
        check_for_issues()
        time.sleep(0.5) # Reevaluates every half second

    # We continue burning until the tank is mostly empty. This allows for a hypothetical first stage landing.
    while vessel.resources_in_decouple_stage(vessel.control.current_stage - 1).amount("LiquidFuel") > 200:
        ap.target_pitch = 0
        time.sleep(0.5)
        
    control.throttle = 0 # Throttles down for separation
    time.sleep(2) # Gives time to ensure vessel throttles down

# Ensures nothing happens during the coast phase to apoapsis
def coast():
    print("Iris is now coasting to its highest point, where it will prepare for circularizing")
    while flight.mean_altitude < vessel.orbit.apoapsis_altitude * 0.93:
        ap.target_pitch = 0
        control.throttle = 0
        time.sleep(0.5)
        check_for_issues()

# Initial circularization of the spacecraft
def circularize():
    print("Iris has commenced its circularization burn")
    aps = vessel.orbit.apoapsis_altitude
    while (vessel.orbit.periapsis_altitude < aps * 0.97):
        ap.target_pitch = 0
        control.throttle = 1
        time.sleep(0.5)
        check_for_issues()

# In orbit
def orbit():
    print ("Iris has achieved a stable orbit. It will continue making small adjustments to ensure good altitude is maintained")
    seconds = 0
    ap.disengage()
    control.sas = True
    while abs(vessel.orbit.periapsis_altitude - vessel.orbit.apoapsis_altitude) > 2500 and vessel.resources.amount('LiquidFuel') > 225:
        # If there is significant variation between periapsis (per) and apoapsis (apo), and enough fuel, we'll improve circularization
        # If close to per, this code runs to lower the apo
        if vessel.orbit.time_to_periapsis < 30:
            control.sas_mode = control.sas_mode.retrograde
            if abs(flight.pitch) < 1 and (vessel.orbit.time_to_periapsis < 10 or control.throttle == 0.5):
                control.throttle = 0.5
            else:
                control.throttle = 0
                time.sleep(5)

        # If close to aps, this code runs to raise the per.
        elif vessel.orbit.time_to_apoapsis < 30:
            control.sas_mode = control.sas_mode.prograde
            if abs(flight.pitch) < 1 and (vessel.orbit.time_to_apoapsis < 10 or control.throttle == 0.5):
                control.throttle = 0.5
            else:
                control.throttle = 0
                time.sleep(5)
        # If neither of those conditions are true, mwe keep the rocket stationary
        else:
            control.throttle = 0
        time.sleep(0.25)
    if vessel.resources.amount('LiquidFuel') <= 225:
        print("Fuel is low, orbit maintenance will no longer occur.")
    control.throttle = 0

# Checks for various possible in-flight failures.
def check_for_issues():
    # If fuel runs out, it generally cannot reach the proper orbit.
    if vessel.resources_in_decouple_stage(vessel.control.current_stage - 1).amount("LiquidFuel") <= 1:
        raise Exception("Fuel was insufficient to reach successful orbit!")
    # If the vessel is not pointing towards its autopilot heading, it is out of control
    if (flight.heading < ap.target_heading - 15 or flight.heading > ap.target_heading + 15) and flight.pitch < 75:
        raise Exception("Vessel's heading varies significantly from target!")

# Sets the desired heading of the orbit
def set_orbit_heading(heading):
    DESIRED_ORBIT_HEADING = heading

# Sets the desired altitude of the orbit
def set_orbit_altitude(altitude):
    DESIRED_ORBIT_ALTITUDE = altitude
