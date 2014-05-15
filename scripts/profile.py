#!/usr/bin/arch -32 /usr/bin/python2.7
import tektronix
import unittest
import logging
import time
import math

# List all the available Visa instrument
name = "USB0::0x0699::0x0368::C032162::INSTR"
scope = tektronix.Scope(name)
scope.write("RS232:BAUD 19200")

logger = logging.getLogger("tektronix.tektronix")
logger.setLevel(logging.CRITICAL)

def avg_stdev(data):
    length = float(len(data))
    avg = sum(data) / length
    stdev = math.sqrt(sum([(x - avg) ** 2 for x in data]) / length)
    return (avg, stdev)

def profile_curve(expcnt=2, frames=10):
    res =  []
    start = time.time()
    while expcnt:
        expcnt -= 1
        ts = time.time()
        curves = scope.record(frames)
        res.append(time.time() - ts)
    end = time.time()
    jitter = (end - start) - sum(res)
    return (res, jitter)

def profile_all_curves():
    ENC = ["RIB", "RPB", "SRI", "SRP"]
    WID = [1, 2]
    for wid in WID:
        for enc in ENC:
            scope.dat.wid = wid
            scope.dat.enc = enc
            curve = scope.curve
            (profile, jitter) = profile_curve()
            print wid, enc, jitter, avg_stdev(profile)
    scope.dat.enc = "ASCI"
    (profile, jitter) = profile_curve()
    print wid, enc, jitter, avg_stdev(profile)

if __name__ == '__main__':
    profile_all_curves()
