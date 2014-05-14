import visa
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
        super(Namespace, self).__init__()
    
    def __getattr__(self, key):
        return self[key.upper()]

    def lookup(self, key):
        name = str.join(':', self.get_name() + [key.upper()])
        cmd = "%s?" % name
        return numify(self._scope.ask(cmd))

    def verify(self, key, val):
        scope_val = self.lookup(key)
        if val != scope_val or type(val) != type(scope_val):
            raise ValueError, 'key "%s": current value "%s" (type %s) does not match returned value "%s" (type %s)' % (name, val, type(val), scope_val, type(scope_val))
        logmsg = 'Verified key "%s" == "%s"' % (key, val)
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
    
    def connect(self, instrument_name=None):
        # XXX: check scope for connection?
        if instrument_name:
            self._instrument_name = instrument_name
        logmsg = 'Connecting to "%s"' % self._instrument_name
        logger.info(logmsg)
        rm = visa.ResourceManager()
        self._instrument = rm.get_instrument(self._instrument_name)
        self.load_environment()

    def load_environment(self):
        logmsg = 'Loading scope environment'
        logger.info(logmsg)
        resp = self.ask('SET?')
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
            head[key] = numify(val)

    def write(self, msg):
        return self._instrument.write(msg)
        logmsg = 'sent "%s"' % msg
        logger.debug(logmsg)

    def ask(self, msg):
        resp = self._instrument.ask(msg)
        resp = resp.strip()
        logmsg = 'received "%s"' % resp
        logger.debug(logmsg)
        return resp

