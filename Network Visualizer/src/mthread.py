#!/usr/bin/env python
################################################################################
# One patch is needed:
# in /usr/share/pyshared/netsnmp/client.py need to remove "for" cycle
# in snmpwalk section comment
#    for var in var_list:
#       print "  ",var.tag, var.iid, "=", var.val, '(',var.type,')'
################################################################################
# Revision: 0.0.1 Pre-Alpha
# Written by Pavel Klochan


import netsnmp
import re
import ConfigParser
import sys
import time
# netsnmp - for class snmpSession
# re - for def ScanNet, for identifying device vendor
# ConfigParser - for def ScanNet (for oids) and for main to get configuration


class snmpSession(object):
    def __init__(self,
                oid="sysDescr",
                Version=2,
                DestHost="localhost",
                Community="public",
                Verbose = False,
                RetryNoSuch = 1):
        self.oid = oid
        self.Version = Version
        self.DestHost = DestHost
        self.Community = Community
        self.Verbose = Verbose
        self.RetryNoSuch = RetryNoSuch

    def queryGet(self):
        try:
            result = netsnmp.snmpget(self.oid,
                                    Version = self.Version,
                                    DestHost = self.DestHost,
                                    Community = self.Community)
        except:
            print sys.exc_info()
            result = None
        finally:
            return result
    def queryWalk(self):
        try:
            result = netsnmp.snmpwalk(self.oid,
                                    Version = self.Version,
                                    DestHost = self.DestHost,
                                    Community = self.Community)
        except:
            print sys.exc_info()
            result = None
        finally:
            return result

################################################################################

def ScanNet(object):
    RoutResult = {}
    confRoot = '/home/klochan/workspace/Network Visualizer/src'
    snmpConn = snmpSession()
    snmpConn.DestHost = object
    sysDescr = snmpConn.queryWalk()
    #Try for variable availability
    try:
        sysDescr[0]
    except IndexError:        
        print "Router is not responding. Please, try another router..."
        return 12
    else:
        if re.search('Cisco', sysDescr[0]):
            hwVendor = 'Cisco'
        elif re.search('HP', sysDescr[0]):
            hwVendor = 'HP'
        elif re.search('Juniper', sysDescr[0]):
            hwVendor = 'Juniper'
        RoutResult['sysDescr'] = sysDescr[0]
        RoutResult['Vendor'] = hwVendor
    snmpConn.oid = 'sysName'
    RoutResult['sysName'] = snmpConn.queryWalk()[0]
    vendorConf = ConfigParser.RawConfigParser()
    vendorConf.read(str(confRoot) + '/vbsnmp/'.__add__(hwVendor) + str('.snmp'))
    # So, we've identified our router's vendor
    snmpConn.oid = vendorConf.get('OSPF', 'routerID')
    RoutResult['OSPFRID'] = snmpConn.queryGet()[0]
    #snmpConn.oid = vendorConf.get('OSPF', 'Neihbors')
    snmpConn.oid = '.1.3.6.1.2.1.14.10.1.1' # router ip
    ospfNeighbors = {}
    for neigh in snmpConn.queryWalk():
        ospfRIP = neigh
        snmpConn.oid = '.1.3.6.1.2.1.14.10.1.3' + "." + ospfRIP + ".0" # router ip
        if (snmpConn.queryGet()[0] != '0.0.0.0'):
            #snmpConn.queryGet()
            ospfNeighbors[snmpConn.queryGet()[0]] = ospfRIP
            #ospfNeighbors.append(neigh)
    RoutResult['OSPFNeighbors'] = ospfNeighbors
    
    #Get IP-Addres, Mask, OSPF-Area-ID
    snmpConn.oid = '.1.3.6.1.2.1.4.20.1.1'
    ipInt = {}
    for intNet in snmpConn.queryWalk():
        snmpConn.oid = '.1.3.6.1.2.1.4.20.1.3' + "." + intNet #cisco netmask
        ipMask = snmpConn.queryGet()[0]
        snmpConn.oid = '.1.3.6.1.2.1.14.7.1.3' + "." + intNet + ".0" #cisco ospf areaid
        ipOSPFAID = snmpConn.queryGet()
        if (intNet != '0.0.0.0'):
            if (ipOSPFAID[0] != None):
                ipInt[intNet] = [ipMask, snmpConn.queryGet()[0]]
    RoutResult['Interfaces'] = ipInt
    
    #Get Routes, Netmask, NextHop and Type
    snmpConn.oid = '.1.3.6.1.2.1.4.21.1.1' #get networks
    ipRout = {}
    for RoutNet in snmpConn.queryWalk():
        snmpConn.oid = '.1.3.6.1.2.1.4.21.1.11' + '.' + RoutNet # get route mask
        RoutNetMask = snmpConn.queryGet()[0]
        snmpConn.oid = '.1.3.6.1.2.1.4.21.1.7' + '.' + RoutNet # get nexthop
        RoutNextHop = snmpConn.queryGet()[0]
        snmpConn.oid = '.1.3.6.1.2.1.4.21.1.9' + '.' + RoutNet # get type of rout
        RouteType = snmpConn.queryGet()[0]
        ipRout[RoutNet] = [RoutNetMask, RoutNextHop, RouteType]
    RoutResult['Routes'] = ipRout
    #Return our hash
    return RoutResult

#Recursion is only for testing algoritm
#We need to implement multithreading with queues
#Number of threads needs to be calculated from number of CPU
#We have first router in queue, return neighbors, put them in queue and so on
# threads get neighbors from queue and get all information
#!!!!!! we need to analyze, if router was already in queue 
# http://www.artfulcode.net/articles/multi-threading-python/
def recurScan(dict, id):
    if dict.has_key(id):
        pass
    else:
        dict[id] = ScanNet(id)
        for neigh in dict[id]['OSPFNeighbors'].keys():
            recurScan(dict, neigh)
    return dict


#Main program starting
def main():
    startTime = time.time()
    dfsw1 = '10.25.2.14'
    temp = {}
    temp = recurScan(temp, dfsw1)
    for i in temp.keys():
        print temp[i]['sysName'],
    print "\n", len(temp.keys())
    print "Elapsed Time: %s" % (time.time() - startTime)
        
                                           
# Default value start main program
if __name__ == "__main__":
    main()