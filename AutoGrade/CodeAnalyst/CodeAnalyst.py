from Utils.Assignment import Assignment
from subprocess import Popen, TimeoutExpired, PIPE
from os import kill, system, getpid, getppid, popen, chdir, getcwd, path
from time import sleep
from psutil import Process
from Constants import MEM_VALUES, TOTAL_RUNS
class CodeAnalyst(object):



    def __init__(self, assignment, successIOs):
        self.__assignment = assignment
        self.__successIOs = successIOs
        self.__memVal = MEM_VALUES
        self.__cpuTimes = []
    

    def analyse(self) -> MEM_VALUES:
        indices = [i for i, x in enumerate(self.__successIOs) if x == 1]
        runs = 0
        psProcess = Process(getpid())
        currWorkingDir = getcwd()
        chdir(self.__assignment.getFolder())
        while(runs <= 20):
            for i in indices:
                process = Popen([self.__assignment.getLaunchCommand(), self.__assignment.getExecutableFileName()], stdout=PIPE, stdin=PIPE)
                
                try:
                    with open('/proc/{pid}/statm'.format(pid=process.pid)) as f:
                        self.updateMemValues(f.readlines()[0])

                    stdin, stdout = process.communicate(bytes('20'.encode('UTF-8')), timeout=30)
                except TimeoutExpired:
                    pass
                self.__cpuTimes.append(getattr(psProcess.cpu_times(), 'children_user') - sum(self.__cpuTimes))
                runs += 1
        
        chdir(currWorkingDir)
        return {
            'memValues': self.__memVal,
            'cpuTimes': self.__cpuTimes,
            'fileSize': path.getsize(self.__assignment.getFilePath())
        }

    def updateMemValues(self, strMem:str):
        listMem = strMem.replace('\n', '').split(' ')
        self.__memVal['size'].append(int(listMem[0]))
        self.__memVal['resident'].append(int(listMem[1]))
        self.__memVal['shared'].append(int(listMem[2]))
        self.__memVal['text'].append(int(listMem[3]))
        self.__memVal['lib'].append(int(listMem[4]))
        self.__memVal['data'].append(int(listMem[5]))
        self.__memVal['dt'].append(int(listMem[6]))

    def getMemValues(self):
        return self.__memVal
if __name__ == '__main__':
    # c = CodeAnayst(None, [0, 1, 0, 1, 0], None)
    # c.analyse()
    pass