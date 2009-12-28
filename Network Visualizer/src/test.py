import Queue
import threading
import time
import mthread

neighQueue = Queue.Queue()
          
class multiScan(threading.Thread):
    def __init__(self, neighQueue, netMap):
        threading.Thread.__init__(self)
        self.neighQueue = neighQueue
        self.map = netMap

    def run(self):
            while (neighQueue.qsize() > 0):
                neighbor = neighQueue.get()
                print neighbor
                if (not netMap.has_key(neighbor)):
                    netMap[neighbor] = mthread.ScanNet(neighbor)
                    #print netMap[hosts]['OSPFNeighbors'].keys()
                    for sndNeigh in netMap[neighbor]['OSPFNeighbors'].keys():
                        if (not netMap.has_key(sndNeigh)):
                            self.neighQueue.put(sndNeigh)
                self.neighQueue.task_done()

start = time.time()

netMap = {}
dfsw1 = '10.25.2.14'
neighQueue = Queue.Queue()
netMap[dfsw1] = mthread.ScanNet(dfsw1)
for neighs in netMap[dfsw1]['OSPFNeighbors'].keys():
    neighQueue.put(neighs)
#for i in range(len(netMap[dfsw1]['OSPFNeighbors'].keys())):
for i in range(5):
    tread = multiScan(neighQueue, netMap)
    tread.start()
    neighQueue.join()
for i in netMap.keys():
    print netMap[i]['sysName']
print "Elapsed time is %s" % (time.time() - start)
