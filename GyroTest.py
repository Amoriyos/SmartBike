import sys
import time 
import numpy as np
import threading
from Phidget22.Devices.Spatial import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

try:
    ch = Spatial()
except RuntimeError as e:
    print("Runtime Exception %s" % e.details)
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    exit(1)

def SpatialAttached(self):
    try:
        attached = self
        print("\nAttach Event Detected (Information Below)")
        print("===========================================")
        print("Library Version: %s" % attached.getLibraryVersion())
        print("Serial Number: %d" % attached.getDeviceSerialNumber())
        print("Channel: %d" % attached.getChannel())
        print("Channel Class: %s" % attached.getChannelClass())
        print("Channel Name: %s" % attached.getChannelName())
        print("Device ID: %d" % attached.getDeviceID())
        print("Device Version: %d" % attached.getDeviceVersion())
        print("Device Name: %s" % attached.getDeviceName())
        print("Device Class: %d" % attached.getDeviceClass())
        print("Data Interval: %d" % attached.getDataInterval())
        print("\n")
	    #spatial = attached.getChannelClass()
        #self.zeroGyro()
        #time.sleep(5)

    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        exit(1)   
    
def SpatialDetached(self):
    detached = self
    try:
        print("\nDetach event on Port %d Channel %d" % (detached.getHubPort(), detached.getChannel()))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        exit(1)   

def ErrorEvent(self, eCode, description):
    print("Error %i : %s" % (eCode, description))

angularPos = [0.0, 0.0, 0.0]
gyro_k1 = [0.0, 0.0, 0.0]
gyro_k2 = [0.0, 0.0, 0.0]
gyro_k3 = [0.0, 0.0, 0.0]
h = 0.02
timer = 0

def SpatialDataHandler(self, acceleration, angularRate, fieldStrength, timestamp):
    global angularPos
    global gyro_k1
    global gyro_k2
    global gyro_k3
    global timer
    global h
    if (timer == 0):
        timer = timestamp - 40
    w = angularRate
    gyro_k1 = gyro_k2
    gyro_k2 = gyro_k3
    gyro_k3 = w
    h = (.75 * h) + (.25 * ((timestamp - timer) / 1000.0))
    timer = timestamp;

    #integrate the angular rates
    for i in range(3):
        angularPos[i] = angularPos[i] + (h / 6.0) * (gyro_k1[i] + 4 * gyro_k2[i] + gyro_k3[i])

    forceMagnitudeApprox = np.sqrt(acceleration[0]**2 + acceleration[1]**2 + acceleration[2]**2)
    if (forceMagnitudeApprox > 0.8 and forceMagnitudeApprox < 1.2):
        pitchAcc = np.arctan2(acceleration[0], acceleration[1]) * 180.0 / np.pi + 90
        angularPos[2] = angularPos[2] * 0.98 + pitchAcc * 0.02
        rollAcc = -np.arctan2(acceleration[0], acceleration[2]) * 180.0 / np.pi - 90.0
        angularPos[1] = angularPos[1] * 0.98 + rollAcc * 0.02

##    fieldMagnitudeApprox = np.sqrt(fieldStrength[0]**2 + fieldStrength[1]**2 + fieldStrength[2]**2)
##    if (fieldMagnitudeApprox < 2.0):
##        yawField = np.arctan2(fieldStrength[2]/ np.abs(np.cos(np.radians(angularPos[1]))), fieldStrength[1]/ np.abs(np.cos(np.radians(angularPos[2])))) * 180 / np.pi - 180
##        angularPos[0] = angularPos[0] * 0.99 + yawField * 0.01
        
##    print("Acceleration  : %7.3f  %8.3f  %8.3f" % (acceleration[2], acceleration[1], acceleration[0]))
##    print("Angular Rate  : %7.3f  %8.3f  %8.3f" % (angularRate[2], angularRate[1], angularRate[0]))
##    print("Angular Posit : %7.3f  %8.3f  %8.3f" % (angularPos[2], angularPos[1], angularPos[0]))
##    print("Field Strength: %7.3f  %8.3f  %8.3f" % (fieldStrength[2], fieldStrength[1], fieldStrength[0]))
##    print("Timestamp: %f\n" % timestamp)
##    print("h = %f" % h)


bc_previous_error = 0
bc_integral = 0
bc_derivative = 0

def balanceControl():

    global bc_previous_error
    global bc_integral
    global bc_derivative
    kp = 18.00582
    ki = 56.89620
    kd = -0.11878
    fc = 32.41575
    dt = 0.1

    error = 0.0 - angularPos[1]
    bc_integral += error * dt
    bc_derivative = (error - bc_previous_error) / dt
    steeringAngle = (kp * error) + (ki * bc_integral) + (kd * bc_derivative)
    print ("Control output: %f\n" % steeringAngle)
    
    if (steeringAngle < -45.0):
        steeringAngle = -45.0
    elif (steeringAngle > 45.0):
        steeringAngle = 45.0
    bc_previous_error = error
    
    threading.Timer(dt, balanceControl).start()
    


try:
    ch.setOnAttachHandler(SpatialAttached)
    ch.setOnDetachHandler(SpatialDetached)
    ch.setOnErrorHandler(ErrorEvent)
    ch.setOnSpatialDataHandler(SpatialDataHandler)

    # Please review the Phidget22 channel matching documentation for details on the device
    # and class architecture of Phidget22, and how channels are matched to device features.

    # Specifies the serial number of the device to attach to.
    # For VINT devices, this is the hub serial number.
    #
    # The default is any device.
    #
    # ch.setDeviceSerialNumber(<YOUR DEVICE SERIAL NUMBER>) 

    # For VINT devices, this specifies the port the VINT device must be plugged into.
    #
    # The default is any port.
    #
    # ch.setHubPort(0)

    # Specifies that the channel should only match a VINT hub port.
    # The only valid channel id is 0.
    #
    # The default is 0 (false), meaning VINT hub ports will never match
    #
    # ch.setIsHubPortDevice(1)

    # Specifies which channel to attach to.  It is important that the channel of
    # the device is the same class as the channel that is being opened.
    #
    # The default is any channel.
    #
    # ch.setChannel(0)

    # In order to attach to a network Phidget, the program must connect to a Phidget22 Network Server.
    # In a normal environment this can be done automatically by enabling server discovery, which
    # will cause the client to discovery and connect to available servers.
    #
    # To force the channel to only match a network Phidget, set remote to 1.
    #
    # Net.enableServerDiscovery(PhidgetServerType.PHIDGETSERVER_DEVICEREMOTE);
    # ch.setIsRemote(1)

    print("Waiting for the Phidget Spatial Object to be attached...")
    ch.openWaitForAttachment(5000)
    ch.zeroGyro()
    time.sleep(3)
    ch.setDataInterval(40)
    time.sleep(3)   # wait for the readings to stabilize
    balanceControl()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    exit(1)

print("Gathering data for 10 seconds...")
time.sleep(1000)

try:
    ch.close()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    exit(1) 
print("Closed Spatial device")
exit(0)
                     
