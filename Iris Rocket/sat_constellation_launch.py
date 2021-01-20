# This script launches between 7 and 12 communications satellites as part of
# a constellation for communication. Uses the launch.py scripts along with its own
# deployment operation once orbit is obtained

import launch
import time

# Deploys the satellites so that they naturally separate
def deploy():
    print("The rocket will begin spinning rapidly to build momentum for the satellites.")
    launch.vessel.control.throttle = 0
    time.sleep(1)
    # Detaches from the Iris second stage
    launch.vessel.control.activate_next_stage()
    time.sleep(1)
    # Deploy solar pannels (where applicable
    launch.vessel.control.toggle_action_group(1)
    time.sleep(2)
    # Rapid spinning creates momentum so that satellites can naturally separate
    launch.vessel.control.sas = False
    launch.vessel.control.pitch = 1
    time.sleep(1.2)
    # The satellites are then released from each other
    print("Deploying the satellites.")
    launch.vessel.control.activate_next_stage()
    launch.vessel.control.pitch = 0
    time.sleep(5)
    print("Mission complete.")

launch.DESIRED_ORBIT_HEADING = 25 # High orbit to ensure maximum coverage
launch.prepare_for_launch() # Sets up for launch
launch.control.activate_next_stage() # Blast off
try:
    launch.first_stage() # Ascent to space
except Exception as e:
    print(e)
    print("Vehicle will attempt to resume control.")
    time.sleep(3)
    try:
        launch.first_stage()
    except Exception as f:
        print("Vehicle unable to regain control. Proceed manually if possible.")
else:
    launch.control.activate_next_stage() # Starts second stage
    launch.control.rcs = True
    launch.coast() # Coasts to highest point
    try:
        launch.circularize() # Makes the orbit approximately a circle
    except:
        print("Vehicle unable to circularize. Proceed manually and type GO to deploy.")
        s = ""
        while (s != "GO"):
            s = input("\nTo re-enter and land now, type END. \nTo remain in orbit under manual control or to run another script, type CONTINUE\n> ")
        deploy()
    else:
        launch.orbit() # Adjusts the orbit of the ship to ensure it is a circle
        print("The capsule is now in a stable orbit.")
        time.sleep(3)
        deploy()
