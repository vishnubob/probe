#!/usr/bin/arch -32 /usr/bin/python2.7
import tektronix
import unittest

# List all the available Visa instrument
name = "USB0::0x0699::0x0368::C032162::INSTR"
GlobalScope = tektronix.Scope(name)
GlobalScope.write("RS232:BAUD 19200")

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.scope = GlobalScope

    def test_variable_set(self):
        state = self.scope.acq.state = 1
        self.assertTrue(state == self.scope.acq.state)
        state = self.scope.acq.state = 0
        self.assertTrue(state == self.scope.acq.state)
        state = self.scope.acq.state = 1
        self.assertTrue(state == self.scope.acq.state)

    def test_curve(self):
        ENC = ["RIB", "RPB", "SRI", "SRP"]
        WID = [1, 2]
        for wid in WID:
            for enc in ENC:
                self.scope.dat.wid = wid
                self.scope.dat.enc = enc
                self.assertTrue(self.scope.curve)
        self.scope.dat.enc = "ASCI"
        self.assertTrue(self.scope.curve)

    def test_report(self):
        report = self.scope.report()
        self.assertTrue(report)
        f = open("report.txt", 'w')
        f.write(report)

if __name__ == '__main__':
    unittest.main()
