import launch
import time

# At end of flight, reduces orbit to sub 50,000 for re-entry
def reenter():
    print("The capsule is beginning its entry burn to re-enter the Earth's atmosphere")
    launch.control.sas_mode = launch.control.sas_mode.retrograde
    time.sleep(5)
    while (launch.vessel.orbit.periapsis_altitude > 50000):
        # Ensures orientation is good before 
        launch.control.throttle = 0.5
        time.sleep(0.5)
    launch.control.throttle = 0
    time.sleep(1)

# During and after reentry, controls parachute and landing
def land():
    print("The capsule has burned sufficiently to re-enter the atmosphere and is now coasting")
    while (launch.flight.mean_altitude > 11000):
        launch.control.sas_mode = launch.control.sas_mode.retrograde
        time.sleep(0.5)
    print("The capsule is deploying its drogue chutes to slow itself down to safe speeds")
    launch.control.activate_next_stage() # Drogue chute deploy
    while (launch.flight.mean_altitude > 5000):
        time.sleep(0.5)
    print("The capsule is now deploying its main chutes to prepare for landing")
    launch.control.activate_next_stage() # Main chute deploy
    # Touch down occurs shortly after this

# Helper function to receive the desired heading
def inputNumber(message):
  while True:
    try:
       userInput = int(input(message))       
    except ValueError:
       print("Not an integer! Try again.")
       continue
    else:
       return userInput 
       break 

launch.DESIRED_ORBIT_HEADING = inputNumber("What heading for launch? 0 = N, 90 = E, 180 = S, 270 = W relative to KSC\n > "
launch.prepareForLaunch() # Sets up for launch
launch.control.activate_next_stage() # Blast off
launch.firstStage() # Ascent to space
launch.control.activate_next_stage() # Starts second stage
launch.control.rcs = True
launch.coast() # Coasts to highest point
launch.circularize() # Makes the orbit approximately a circle
launch.orbit() # Adjusts the orbit of the ship to ensure it is a circle

print("The capsule is now in a stable orbit.")
s = ""
while (s != "END" and s != "CONTINUE"):
    s = input("To re-enter and land now, type END. \nTo remain in orbit under manual control or to run another script, type CONTINUE\n> ")

if (s == "END"):
    reenter()
    launch.control.activate_next_stage()
    land()
