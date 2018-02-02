#import serial
import time

for i in range(0, 2000):
    f = open("bikedata.json", "w")
    f.write("{ \"speed\" : %d}" % i)
    f.close()
    time.sleep(1)

