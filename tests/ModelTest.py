import os
import signal
import sys
import time
from abc import ABCMeta, abstractmethod
from subprocess import Popen, PIPE
from threading import Thread
import json
import psutil



class ModelTest(object):

    @abstractmethod
    def prepare(self, h, soma, mechanism):
        pass

    @abstractmethod
    def on_run_complete(self):
        pass

    @abstractmethod
    def getResults(self):
        raise NotImplementedError()

    def __init__(self):
        self.error = False
        self.saveStartDir()

    def saveStartDir(self):
        self.startPath = os.getcwd()

    def restoreStartDir(self):
        os.chdir(self.startPath)

    def modelDir(self):
        return os.path.dirname(self.path)

    def modelFileName(self):
        return os.path.basename(self.path)

    def resultsDir(self):
        return os.path.dirname(self.resultsFile)

    def comparisonPath(self):
        return self.resultsDir() + "/comparison.png"

    def loadResults(self):
        with open(self.resultsFile) as r:
            result = json.load(r)

        return result

    def getResultsOwnThread(self):
        self.printAndRun('python -c "from ' + self.__class__.__module__ + ' import ' + self.__class__.__name__ + ' as test; test().getResults();"')

    def printAndRun(self, command):
        sys.stdout.write('Running:   "' + command + '" ... ')

        startDir = os.getcwd()

        try:
            from Queue import Queue, Empty
        except ImportError:
            from queue import Queue, Empty  # python 3.x

        ON_POSIX = 'posix' in sys.builtin_module_names

        def enqueue_output(out, err, queue):
            for line in iter(out.readline, b''):
                queue.put(line)

            out.close()

            for line in iter(err.readline, b''):
                queue.put(line)

            err.close()




        q = Queue()
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, bufsize=1, close_fds=ON_POSIX)
        t = Thread(target=enqueue_output, args=(p.stdout, p.stderr, q))
        t.daemon = True  # thread dies with the program

        lines = ""



        # read line without blocking
        # check if process is alive and if so, wait up to 5 mins for output
        # handle non-outputting short processes eg. rm ...
        # and long running, non-outputting processes like neuron run
        # and long running, hung processes that show an error


        # Start the process
        pid = p.pid
        t.start()
        keepChecking = True

        # Check for errors in output
        while keepChecking:

            # Get all lines thus far from process
            try:
                line = ""

                while True:
                    line = line + q.get_nowait()

            # No more lines
            except Empty:
                pass

            # If no lines received, wait
            if line == "":
                time.sleep(0.01)

            # Process the output line
            else:
                lines = lines + line

                errorsFound = self.errorsFound(line)

                if errorsFound:
                    logFile = startDir + "/error.log"

                    with(open(logFile, "w")) as f:
                        f.write(command)
                        f.write(lines)

                    self.kill_proc_tree(pid)

                    print('ERROR')

                    print(lines)

                assert not errorsFound  # See error.log file in script start folder

            # If the thread is dead and there are no more output lines, stop checking
            if not t.isAlive() and q.empty():
                keepChecking = False

        print('OK')

    def errorsFound(self, line):

        # Clear false alarms
        cleanOutput = line \
            .replace("NRN Error", "") \
            .replace("NMODL Error", "") \
            .lower()

        errorsFound = 'error' in cleanOutput or \
                      'is not valid against the schema' in cleanOutput or \
                      'problem in model' in cleanOutput or \
                      'traceback' in cleanOutput or \
                      'out of range, returning exp' in cleanOutput

        return errorsFound

    def kill_proc_tree(self, pid, sig=signal.SIGTERM, include_parent=True,
                       timeout=None, on_terminate=None):
        """Kill a process tree (including grandchildren) with signal
        "sig" and return a (gone, still_alive) tuple.
        "on_terminate", if specified, is a callabck function which is
        called as soon as a child terminates.
        """
        if pid == os.getpid():
            raise RuntimeError("I refuse to kill myself")
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)
        for p in children:
            p.send_signal(sig)
        gone, alive = psutil.wait_procs(children, timeout=timeout,
                                        callback=on_terminate)
        return (gone, alive)


