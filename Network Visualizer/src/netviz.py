'''
Created on 23.12.2009
Version 0.0.1 Pre-Alpha
@author: Pavel Klochan
'''
import ConfigParser
import sys

def main():
    config = ConfigParser.RawConfigParser()
    config.read('netviz.conf')
    rIp = config.get('Router', 'ip')
    print "test"
    print rIp

if __name__ == '__main__':
    main()