import atexit
import signal
import sys, os
class Daemon:
    def __init__(self, pidfile, path): 
        self.pidfile = pidfile
        self.path = path
        self.statuses = {
            '0': 'Daemon is running.',
            '1': 'Daemon is not running.',
            '2': 'Pidfile not found, stopping daemon.',
            '3': 'Process not found, removing pidfile.'
        }

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\
            n'.format(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\
            n'.format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        
        pid = str(os.getpid())

        with open(self.pidfile,'w+') as f:
            f.write(pid + '\n') 


    def delpid(self):
        os.remove(self.pidfile)


    def start(self):
        if os.path.isfile(self.pidfile):
            print('pidfile ' + self.pidfile + ' already exists. Daemon already running?')
            sys.exit(1)
        else:
            self.daemonize()
            self.run()

    def stop(self):
        if not os.path.isfile(self.pidfile):
            print('pidfile ' + self.pidfile + ' does not exist. Daemon not running?')
        else:
            pid = 0
            with open(self.pidfile, 'r') as f:
                pid = int(f.read()[ : -1])
            self.delpid()
            os.kill(pid, signal.SIGTERM)
    
    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def run(self):
        """You should override this method when you subclass
        Daemon.
        It will be called after the process has been daemonized
        start() or restart()."""