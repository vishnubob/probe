import visa
import pyvisa.highlevel
from time import *
from struct import unpack
import numbers
import numpy as np

class TektronixScopeError(Exception):
    """Exception raised from the TektronixScope class

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, mesg):
        self.mesg = mesg
    def __repr__(self):
        return self.mesg
    def __str__(self):
        return self.mesg

class Scope(pyvisa.highlevel.Instrument):
    def write(self, msg):
        #print "->", msg
        super(Scope, self).write(msg)

    def ask(self, msg):
        resp = super(Scope, self).ask(msg)
        resp = resp.strip()
        #print "<-", resp
        return resp

    #Acquisition Command Group 
    def start_acq(self):
        """Start acquisition"""
        self.write('ACQ:STATE RUN')
    def stop_acq(self):
        """Stop acquisition"""
        self.write('ACQ:STATE STOP')

    #Miscellaneous Command Group
    def load_setup(self):
        resp = self.ask('SET?')
        items = resp.split(';')
        self.dico = {}
        for item in items:
            elems = item.split(' ')
            key = elems[0]
            val = str.join(' ', elems[1:])
            self.dico[key] = val
        return self.dico

    def get_setup_dict(self, force_load=False):
        """Return the dictionnary of the setup 
        
        By default, the method does not load the setup from the instrument
        unless it has not been loaded before or force_load is set to true.
        """
        if not hasattr(self, 'dico') or force_load:
            self.load_setup()
        return self.dico

    def get_setup(self, name, force_load=False):
        """Return the setup named 'name' 
        
        By default, the method does not load the setup from the instrument
        unless it has not been loaded before or force_load is set to true.
        """
        if not hasattr(self, 'dico') or force_load:
            self.load_setup()
        return self.dico[name]

    def number_of_channel(self):
        return 4
        """Return the number of available channel on the scope (4 or 2)"""
        if 'CH4' in self.get_setup_dict().keys():
            return 4
        else:
            return 2

    #Save and Recall Command Group

    #Search Command Group

    #Status and Error Command Group

    #Trigger Command Group

    #Vertical Command Group
    def channel_name(self, name):
        """Return and check the channel name
        
        Return the channel CHi from either a number i, or a string 'i', 'CHi'
        
        input : name is a number or a string
        Raise an error if the channel requested if not available 
        """
        n_max = self.number_of_channel()
        channel_list = ['CH%i'%(i+1) for i in range(n_max)]
        channel_listb = ['%i'%(i+1) for i in range(n_max)]
        if isinstance(name, numbers.Number):
            if name > n_max:
                raise ScopeError("Request channel %i while channel number should be between %i and %i"%(name, 1, n_max))
            return 'CH%i'%name
        elif name in channel_list:
            return name
        elif name in channel_listb:
            return 'CH'+name
        else:
            raise ScopeError("Request channel %s while channel should be in %s"%(str(name), ' '.join(channel_list)))

    def is_channel_selected(self, channel):
        return self.ask('SEL:%s?'%(self.channel_name(channel)))=='1'

    def get_channel_offset(self, channel):
        return float(self.ask('%s:OFFS?'%self.channel_name(channel)))

    def get_channel_position(self, channel):
        return float(self.ask('%s:POS?'%self.channel_name(channel)))

    def get_out_waveform_vertical_scale_factor(self):
        return float(self.ask('%s:SCA?'%self.channel_name(channel)))

    # Waveform Transfer Command Group
    def set_data_source(self, name):
        name = self.channel_name(name)
        self.write('DAT:SOUR '+str(name))

    def set_data_start(self, data_start):
        """Set the first data points of the waveform record
        If data_start is None: data_start=1
        """
        if data_start is None:
            data_start = 1
        data_start = int(data_start)
        self.write('DATA:START %i'%data_start)

    def get_data_start(self):
        return int(self.ask('DATA:START?'))

    def get_horizontal_record_length(self):
        return int(self.ask("horizontal:recordlength?"))

    def set_horizontal_record_length(self, val):
        self.write('HORizontal:RECOrdlength %s'%str(val))

    def set_data_stop(self, data_stop):
        """Set the last data points of the waveform record
        If data_stop is None: data_stop= horizontal record length
        """
        if data_stop is None:
            data_stop = self.get_horizontal_record_length()
        self.write('DATA:STOP %i'%data_stop)

    def get_data_stop(self):
        return int(self.ask('DATA:STOP?'))

    def get_out_waveform_horizontal_sampling_interval(self):
        return float(self.ask('WFMPRE:XIN?'))

    def get_out_waveform_horizontal_zero(self):
        return float(self.ask('WFMPRE:XZERO?'))

    def get_out_waveform_vertical_scale_factor(self):
        return float(self.ask('WFMPRE:YMUlt?'))

    def get_out_waveform_vertical_position(self):
        return float(self.ask('WFMPRE:YOFf?'))

    def read_data_one_channel(self, channel=None, data_start=None, 
                              data_stop=None, x_axis_out=False,
                              t0=None, DeltaT = None, booster=False):
        """Read waveform from the specified channel
        
        channel : name of the channel (i, 'i', 'chi'). If None, keep
            the previous channel
        data_start : position of the first point in the waveform
        data_stop : position of the last point in the waveform
        x_axis_out : if true, the function returns (X,Y)
                    if false, the function returns Y (default)
        t0 : initial position time in the waveform
        DeltaT : duration of the acquired waveform
            t0, DeltaT and data_start, data_stop are mutually exculsive 
        booster : if set to True, accelerate the acquisition by assuming
            that all the parameters are not change from the previous
            acquisition. If parameters were changed, then the output may
            be different than what is expected. The channel is the only
            parameter that is checked when booster is enable
        
        """
        # set booster to false if it the fist time the method is called
        # We could decide to automaticaly see if parameters of the method
        # are change to set booster to false. However, one cannot
        # detect if the setting of the scope are change
        # To be safe, booster is set to False by default.  
        if booster:  
            if not hasattr(self, 'first_read'): booster=False
            else: 
                if self.first_read: booster=False
        self.first_read=False
        if not booster:
            # Set data_start and data_stop according to parameters
            if t0 is not None or DeltaT is not None:
                if data_stop is None and data_start is None:
                    x_0 = self.get_out_waveform_horizontal_zero()
                    delta_x = self.get_out_waveform_horizontal_sampling_interval()
                    data_start = int((t0 - x_0)/delta_x)+1
                    data_stop = int((t0+DeltaT - x_0)/delta_x)
                else: # data_stop is not None or data_start is not None 
                    raise ScopeError("Error in read_data_one_channel,\
t0, DeltaT and data_start, data_stop args are mutually exculsive")
            if data_start is not None:
                self.set_data_start(data_start)
            if data_stop is not None:
                self.set_data_stop(data_stop) 
            self.data_start = self.get_data_start()
            self.data_stop = self.get_data_stop()
        # Set the channel
        if channel is not None:
            self.set_data_source(channel)
        if not booster:
            if not self.is_channel_selected(channel):
                raise ScopeError("Try to read channel %s which is not selected" % channel)
        if not booster:
            self.write("DATA:ENCDG RIB")
            self.write("WFMPRE:BYTE_NR 2")
            self.offset = self.get_out_waveform_vertical_position()
            self.scale = self.get_out_waveform_vertical_scale_factor()
            self.x_0 = self.get_out_waveform_horizontal_zero()
            self.delta_x = self.get_out_waveform_horizontal_sampling_interval()

        X_axis = self.x_0 + np.arange(self.data_start-1, self.data_stop)*self.delta_x

        curve = self.ask('CURVE?')
        length = curve[1]
        offset = 2 + int(length)
        res = np.frombuffer(curve[offset:], dtype = np.dtype('int16').newbyteorder('>'))
        # The output of CURVE? is scaled to the display of the scope
        # The following converts the data to the right scale
        Y = (res - self.offset)*self.scale
        if x_axis_out:
            return X_axis, Y
        else:
            return Y

    #Zoom Command Group
