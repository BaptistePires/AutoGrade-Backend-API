from subprocess import Popen, TimeoutExpired, PIPE
from os import getpid, getppid, path
from psutil import Process
import resource


class CodeAnalyst(object):

    def __init__(self, assignment, successIOs):
        self.__assignment = assignment
        self.__successIOs = successIOs
        self.__cpuTimes = []
        self.__maxRSS = 0

    def analyse(self) -> dict:
        """
            This is the main method of this class, if the resources used by assigment/submission
            need to be retrieved you must use this method.
        :return: Returns a Dict containing : list of cpuTimes, the file size and the maximum resident size.
        """
        # Retrieve the indexes of the inputs / outputs the program succeeded.
        indexes = [i for i, x in enumerate(self.__successIOs) if x == 1]
        runs = 0
        executable = self.getAssignment().getCompiledName()
        psProcess = Process(getpid())
        while (runs <= 20):
            import sys

            for i in indexes:
                process = Popen([self.__assignment.getLaunchCommand(),
                                 executable], stdout=PIPE, stdin=PIPE, stderr=PIPE)
                print('process : ', process.pid)
                rusageChild = resource.getrusage(resource.RUSAGE_CHILDREN)
                try:
                    _, __ = process.communicate(
                        bytes(self.__assignment.getIOs()[i][0].encode('UTF-8')), timeout=30)
                    if rusageChild.ru_maxrss > self.__maxRSS:
                        self.__maxRSS = rusageChild.ru_maxrss
                except TimeoutExpired:
                    assert ('[except - CodeAnalysis.anaylse() - This point should never be reached as IOs has already'
                            'been checked up.s')
                    pass
                self.__cpuTimes.append(
                    getattr(psProcess.cpu_times(), 'children_user') - sum(self.__cpuTimes))
                runs += 1

                if path.exists('./stat'):

                    with open('./stat', 'r') as f:
                        values = f.read().split(' ')
                        utime, stime, vsize = values[13], values[14], values[22]
                        print('getpid() : ', getpid(), 'stat pid: ', values[0], 'getppdi()',getppid())
                        print('utime :', utime, 'stime :', stime, 'vsize :' ,vsize)


        return {
            'cpuTimes': self.__cpuTimes,
            'fileSize': path.getsize(self.__assignment.getOriginalFilename()),
            'maxRSS': self.__maxRSS
        }

    def getAssignment(self):
        return self.__assignment
