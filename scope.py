#!/usr/bin/arch -32 /usr/bin/python2.7
import tektronix
import matplotlib.pyplot as plt
import numpy as np

# List all the available Visa instrument
name = "USB0::0x0699::0x0368::C032162::INSTR"
scope = tektronix.Scope(name)
scope.write("RS232:BAUD 19200")

X = None
Y = None

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
