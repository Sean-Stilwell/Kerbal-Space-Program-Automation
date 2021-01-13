import krpc
import time

connection = krpc.connect()
vessel = connection.space_center.active_vessel

ORBIT_DURATION = 100
DESIRED_ORBIT_HEADING =66

# Prepares a rocket to be launched by engaging autopilot to fly vertically
def prepareForLaunch():
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch = 90
    vessel.auto_pilot.target_heading = DESIRED_ORBIT_HEADING
    vessel.control.throttle = 1
    print("Vessel is prepared to launch, computer has control.")

# Controls the rocket through to 80000 metres
def firstStage():
    print("Lift off of Iris!")
    while (vessel.orbit.apoapsis_altitude < 80000):
        # Ensuring that the speed is not overly fast at a low altitude
        if (vessel.flight().mean_altitude < 10000 and vessel.flight().speed > 300):
            vessel.control.throttle = 0.75
            print("Iris is throttling down to avoid excessive spead")
        else:
            vessel.control.throttle = 1
        # Angling the spacecraft based on altitude
        if (vessel.flight().mean_altitude > 60000):
            vessel.auto_pilot.target_pitch = 0
        elif (vessel.flight().mean_altitude > 50000):
            vessel.auto_pilot.target_pitch = 5
        elif (vessel.flight().mean_altitude > 36000):
            vessel.auto_pilot.target_pitch = 10
        elif (vessel.flight().mean_altitude > 26000):
            vessel.auto_pilot.target_pitch = 30
        elif (vessel.flight().mean_altitude > 18000):
            vessel.auto_pilot.target_pitch = 50
        elif (vessel.flight().mean_altitude > 8000):
            vessel.auto_pilot.target_pitch = 70
        else:
            vessel.auto_pilot.target_pitch = 90
        time.sleep(0.5)
    vessel.control.throttle = 0
    time.sleep(2)

# Ensures nothing happens during the coast phase to apoapsis
def coast():
    print("Iris is now coasting to its highest point, where it will prepare for circularizing")
    while vessel.flight().mean_altitude < vessel.orbit.apoapsis_altitude * 0.93:
        vessel.auto_pilot.target_pitch = 0
        vessel.control.throttle = 0
        time.sleep(0.5)

# Initial circularization of the spacecraft
def circularize():
    print("Iris has commenced its circularization burn")
    aps = vessel.orbit.apoapsis_altitude
    while (vessel.orbit.periapsis_altitude < aps * 0.95):
        vessel.auto_pilot.target_pitch = 5
        vessel.control.throttle = 1
        time.sleep(0.5)

# In orbit
def orbit():
    print ("Iris has achieved a stable orbit. It will continue making small adjustments to ensure good altitude is maintained")
    seconds = 0
    vessel.auto_pilot.disengage()
    vessel.control.sas = True
    while abs(vessel.orbit.periapsis_altitude - vessel.orbit.apoapsis_altitude) > 2500 and vessel.resources.amount('LiquidFuel') > 225:
        # If there is significant variation between periapsis (per) and apoapsis (apo), and enough fuel, we'll improve circularization
        # If close to per, this code runs to lower the apo
        if vessel.orbit.time_to_periapsis < 30:
            try:
                vessel.control.sas_mode = vessel.control.sas_mode.retrograde
            except RuntimeError:
                print("Unable to engage SAS! Point prograde!")
                time.sleep(3)
            if abs(vessel.flight().pitch) < 1 and (vessel.orbit.time_to_periapsis < 10 or vessel.control.throttle == 0.5):
                vessel.control.throttle = 0.5
            else:
                vessel.control.throttle = 0
                time.sleep(5)

        # If close to aps, this code runs to raise the per.
        elif vessel.orbit.time_to_apoapsis < 30:
            try:
                vessel.control.sas_mode = vessel.control.sas_mode.prograde
            except RuntimeError:
                print("Unable to engage SAS! Point prograde!")
                time.sleep(3)
            if abs(vessel.flight().pitch) < 1 and (vessel.orbit.time_to_apoapsis < 10 or vessel.control.throttle == 0.5):
                vessel.control.throttle = 0.5
            else:
                vessel.control.throttle = 0
                time.sleep(5)
        # If neither of those conditions are true, mwe keep the rocket stationary
        else:
            vessel.control.throttle = 0
        seconds = seconds + 1
        time.sleep(0.25)
        if seconds % 100 == 0:
            print("T +" +str(seconds))

def deploy():
    print("The rocket will begin spinning rapidly to build momentum for the satellites.")
    vessel.control.throttle = 0
    time.sleep(1)
    vessel.control.activate_next_stage()
    time.sleep(1)
    vessel.control.toggle_action_group(1)
    time.sleep(2)
    vessel.control.sas = False
    vessel.control.pitch = 1
    time.sleep(1.2)
    print("Deploying the satellites.")
    vessel.control.activate_next_stage()
    vessel.control.pitch = 0
    time.sleep(5)
    print("Mission complete. Satellites can now be manually separated")
    

prepareForLaunch()
vessel.control.activate_next_stage()
firstStage()
vessel.control.activate_next_stage()
vessel.control.rcs = True
coast()
circularize()
orbit()
deploy()
