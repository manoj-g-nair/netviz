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
            import sys
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
            import sys
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
        return 1
    else:
        if re.search('Cisco', sysDescr[0]):
            hwVendor = 'Cisco'
        elif re.search('HP', sysDescr[0]):
            hwVendor = 'HP'
        elif re.search('Juniper', sysDescr[0]):
            hwVendor = 'Juniper'
        RoutResult['sysDescr'] = sysDescr[0]
        RoutResult['Vendor'] = hwVendor
    vendorConf = ConfigParser.RawConfigParser()
    vendorConf.read(str(confRoot) + '/vbsnmp/'.__add__(hwVendor) + str('.snmp'))
    # So, we've identified our router's vendor
    snmpConn.oid = vendorConf.get('OSPF', 'routerID')
    RoutResult['OSPFRID'] = snmpConn.queryGet()[0]
    snmpConn.oid = vendorConf.get('OSPF', 'Neihbors')
    ospfNeighbors = []
    for neigh in snmpConn.queryWalk():
        if neigh != '0.0.0.0':
            ospfNeighbors.append(neigh)
    RoutResult['OSPFNeighbors'] = ospfNeighbors
    snmpConn.oid = '.1.3.6.1.2.1.4.20.1.3' #we need to match all IP's and masks
    for i in snmpConn.queryWalk():
        print "Netmask", i
    return RoutResult
    

#Main program starting
def main():
    confMain = ConfigParser.RawConfigParser()
    confMain.read('netviz.conf')
    temp = ScanNet(confMain.get('Router', 'ip'))
    print temp.get('OSPFNeighbors')
                                       
# Default value start main program
if __name__ == "__main__":
    main()