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

launch.DESIRED_ORBIT_HEADING = 15 # High orbit to ensure maximum coverage
launch.prepareForLaunch() # Sets up for launch
launch.control.activate_next_stage() # Blast off
launch.firstStage() # Ascent to space
launch.control.activate_next_stage() # Starts second stage
launch.control.rcs = True
launch.coast() # Coasts to highest point
launch.circularize() # Makes the orbit approximately a circle
launch.orbit() # Adjusts the orbit of the ship to ensure it is a circle
print("The capsule is now in a stable orbit.")
deploy()
