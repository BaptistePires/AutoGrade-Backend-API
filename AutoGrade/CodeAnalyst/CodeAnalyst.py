from Utils.Assignment import Assignment
from subprocess import Popen, TimeoutExpired, PIPE
from os import kill, system, getpid, getppid, popen, chdir, getcwd, path
from time import sleep
from psutil import Process
from Constants import MEM_VALUES, TOTAL_RUNS
import resource


class CodeAnalyst(object):

    def __init__(self, assignment, successIOs):
        self.__assignment = assignment
        self.__successIOs = successIOs
        self.__cpuTimes = []
        self.__maxRSS = 0

    def analyse(self) -> MEM_VALUES:
        indices = [i for i, x in enumerate(self.__successIOs) if x == 1]
        runs = 0
        psProcess = Process(getpid())
        currWorkingDir = getcwd()
        chdir(self.__assignment.getFolder())

        while(runs <= 20):
            for i in indices:
                process = Popen([self.__assignment.getLaunchCommand(),
                self.__assignment.getExecutableFileName()], stdout=PIPE, stdin=PIPE, stderr=PIPE)
                rusageChild = resource.getrusage(resource.RUSAGE_CHILDREN)
                rusageSelf = resource.getrusage(resource.RUSAGE_SELF)

                try:
                    stdin, stdout = process.communicate(
                        bytes('20'.encode('UTF-8')), timeout=30)
                    if rusageSelf.ru_maxrss - rusageChild.ru_maxrss > self.__maxRSS:
                        self.__maxRSS = rusageSelf.ru_maxrss - rusageChild.ru_maxrss
                except TimeoutExpired:
                    pass
                self.__cpuTimes.append(
                    getattr(psProcess.cpu_times(), 'children_user') - sum(self.__cpuTimes))
                runs += 1

        chdir(currWorkingDir)
        return {
            'cpuTimes': self.__cpuTimes,
            'fileSize': path.getsize(self.__assignment.getFilePath()),
            'maxRSS': self.__maxRSS
        }

    def getMemValues(self):
        return self.__memVal


if __name__ == '__main__':
    # c = CodeAnayst(None, [0, 1, 0, 1, 0], None)
    # c.analyse()
    pass
