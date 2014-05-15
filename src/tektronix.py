import visa
import logging
import struct
import getpass
import pickle
import time
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CacheManager(object):
    def __init__(self, cache_dir=None):
        if cache_dir == None:
            username = getpass.getuser()
            homedir = os.path.expanduser('~' + username)
            cache_dir = os.path.join(homedir, ".tektronix")
        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir)
        self._cache_dir = cache_dir

    @staticmethod
    def load(name, cache_dir=None):
        cm = CacheManager(cache_dir)
        try:
            pickle_fn = os.path.join(cm._cache_dir, name)
            fh = open(pickle_fn)
            logger.debug("CacheManager loading")
            return pickle.load(fh)
        except:
            return None
        
    @staticmethod
    def save(name, obj, cache_dir=None):
        logger.debug("CacheManager saving")
        cm = CacheManager(cache_dir)
        pickle_fn = os.path.join(cm._cache_dir, name)
        fh = open(pickle_fn, 'w')
        pickle.dump(obj, fh)

def numify(val):
    try:
        if '.' in val:
            return float(val)
        else:
            return int(val)
    except ValueError:
        return val

class Namespace(dict):
    def __init__(self, name, parent): 
        self._parent = parent
        self._scope = self._parent._scope
        self._name = name
        self._cache = {}
        super(Namespace, self).__init__()
    
    def __getattr__(self, key):
        key = key.upper()
        # If we are None, we've been cached
        if key in self and self[key] == None:
            self[key] = self.lookup(key)
        return self[key.upper()]

    def dirty(self, visit=None):
        if visit == None:
            visit = []
        if self in visit:
            return
        self._cache = {}
        visit.append(self)
        for nodename in self:
            node = self[nodename]
            if hasattr(node, "dirty"):
                node.dirty(visit)
        self._parent.dirty(visit)

    def lookup(self, key):
        name = str.join(':', self.get_name() + [key.upper()])
        cmd = "%s?" % name
        return numify(self._scope.ask(cmd))

    def verify(self, key, val):
        scope_val = self.lookup(key)
        if val != scope_val:
            raise ValueError, 'key "%s": current value "%s" (type %s) does not match returned value "%s" (type %s)' % (key, val, type(val), scope_val, type(scope_val))
        logmsg = 'verified key "%s" == "%s"' % (key, val)
        logger.debug(logmsg)
        return True

    def __setattr__(self, key, val):
        if key[0] == '_':
            super(Namespace, self).__setattr__(key, val)
        else:
            if type(val) in (int, float, str, unicode):
                name = self.get_name() + [str(key)]
                name = str.join(':', name)
                cmd = "%s %s" % (name, val)
                self._scope.write(cmd)
            if self.verify(key, val):
                self[key.upper()] = val
                self.dirty()

    def get_name(self, qualified=True):
        if not qualified:
            return self._name
        if self._parent == self:
            return []
        return self._parent.get_name() + [self._name]

    def report(self):
        content = ''
        for key in self:
            if isinstance(self[key], self.__class__):
                content += self[key].report()
                continue
            name = self.get_name()
            name.append(key)
            name = str.join(':', name)
            content += "%s %s\n" % (name, self[key])
        return content

class Scope(Namespace):
    def __init__(self, instrument_name, connect=True):
        self._scope = None
        super(Scope, self).__init__("__scope__", self)
        self._scope = self
        self._instrument_name = instrument_name
        if connect:
            self.connect()

    def connect(self, instrument_name=None, retry=5):
        # XXX: check scope for connection?
        ts = time.time()
        if instrument_name:
            self._instrument_name = instrument_name
        logmsg = 'Connecting to "%s"' % self._instrument_name
        logger.info(logmsg)
        rm = visa.ResourceManager()
        while retry:
            retry -= 1
            try:
                self._instrument = rm.get_instrument(self._instrument_name)
                self.load_environment()
                break
            except Exception as err:
                if retry:
                    logmsg = 'Error: %s, retrying' % str(err)
                    logger.error(logmsg)
                else:
                    raise
        delta = time.time() - ts
        logmsg = "It took %.2f seconds to connect" % delta
        logger.debug(logmsg)

    def load_environment(self):
        logmsg = 'Loading scope environment'
        logger.info(logmsg)
        resp = CacheManager.load(self._instrument_name)
        cached = False
        if not resp:
            resp = self.ask('set?')
            CacheManager.save(self._instrument_name, resp)
            cached = True
        tokens = resp.split(';')
        for token in tokens:
            if ':' in token:
                parts = filter(bool, token.split(':'))
                token = parts[-1]
                path = parts[:-1]
                head = self
                for key in path:
                    if key not in head:
                        head[key] = Namespace(key, head)
                    head = head[key]
            token = token.split(' ')
            key = token[0]
            val = str.join(' ', token[1:])
            if not cached:
                head[key] = numify(val)
            else:
                head[key] = None

    def write(self, msg):
        return self._instrument.write(msg.upper())
        logmsg = 'sent "%s"' % msg
        logger.debug(logmsg)

    def ask(self, msg):
        resp = self._instrument.ask(msg)
        resp = resp.strip()
        logmsg = 'recv "%s"' % resp
        logger.debug(logmsg)
        return resp

    def read(self):
        resp = self._instrument.read()
        resp = resp.strip()
        logmsg = 'read "%s"' % resp
        logger.debug(logmsg)
        return resp

    def read_raw(self):
        resp = self._instrument.read_raw()
        logmsg = 'read_raw "%s"' % resp
        logger.debug(logmsg)
        return resp

    def get_encoding(self):
        if "__encoding__" in self._cache:
            return self._cache["__encoding__"]
        flag = ''
        fmtch = ''
        if self.dat.enc == "ASCI":
            # ascii
            fmtch = 's'
        else:
            # binary
            width_code = {1: 'b', 2: 'h', 4:'i'}
            # data width
            fmtch = width_code[self.dat.wid]
            # encoding
            if 'RI' in self.dat.enc:
                # signed
                fmtch = fmtch.lower()
            else:
                # unsigned
                fmtch = fmtch.upper()
            if self.dat.enc[0] == 'S':
                # LSB
                flag += '<'
            else:
                # MSB
                flag += '>'
        logmsg = 'get_encoding(): (%s, %s)' % (fmtch, flag)
        logger.debug(logmsg)
        self._cache["__encoding__"] = (fmtch, flag)
        return self._cache["__encoding__"]

    @property
    def curve(self):
        (fmtch, flag) = self.get_encoding()
        self.write("curve?")
        curve = self.read_raw().strip()
        if fmtch == 's':
            return map(int, curve.split(','))
        hdr_length = int(curve[1])
        offset = 2 + hdr_length
        length = int(curve[2:offset]) / self.dat.wid
        curve = curve[offset:]
        fmt = flag + (fmtch * length)
        return struct.unpack(fmt, curve)

    def record(self, nframes=1):
        return [self.curve for frame in xrange(nframes)]
