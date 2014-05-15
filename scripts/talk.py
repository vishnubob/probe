#!/usr/bin/arch -32 /usr/bin/python2.7
import tektronix
import matplotlib.pyplot as plt
import numpy as np
import time
import code
import os
import readline
import atexit
import pyvisa
import pprint

# List all the available Visa instrument
class ScopeConsole(code.InteractiveConsole):
    def __init__(self, name, locals=None, filename="<console>", histfile=os.path.expanduser("~/.console-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)
        self.name = name
        self.attach_scope(name)

    def attach_scope(self, name):
        self.scope = tektronix.Scope(name)
        self.scope.write("RS232:BAUD 19200")

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)

    def push(self, code):
        try:
            if code.strip() == "setup":
                pprint.pprint(self.scope.setup)
            else:
                if " " in code:
                    self.scope.write(code)
                else:
                    resp = self.scope.ask(code)
                    print resp
        except pyvisa.errors.VisaIOError, err:
            print err
        
name = "USB0::0x0699::0x0368::C032162::INSTR"
sc = ScopeConsole(name)
sc.interact()


