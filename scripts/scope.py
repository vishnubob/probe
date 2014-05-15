#!/usr/bin/arch -32 /usr/bin/python2.7
import tektronix
import matplotlib.pyplot as plt
import numpy as np
import time

# List all the available Visa instrument
name = "USB0::0x0699::0x0368::C032162::INSTR"
scope = tektronix.Scope(name)
scope.write("RS232:BAUD 19200")

X = None
Y = None

scope.set_horizontal_record_length(1000)
print scope.get_horizontal_record_length()
scope.start_acq()
time.sleep(2)
scope.stop_acq()
print scope.get_horizontal_record_length()


for x in range(2):
    (_X, _Y) = scope.read_data_one_channel('CH1', t0=0, DeltaT=10, x_axis_out=True)
    if (X == None):
        X = _X
        Y = _Y
    else:
        np.concatenate((X, _X), axis=0)
        np.concatenate((Y, _Y), axis=0)

plt.plot(X,Y)
plt.savefig("plot.png")
