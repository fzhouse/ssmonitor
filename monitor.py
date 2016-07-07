#!/usr/bin/python

import sys
import time
import socket
import pcap
import dpkt
import multiprocessing

def capPkt(filters, ports):
    pc = pcap.pcap()
    pc.setfilter(filters)
    for ts, pkt in pc:
        eth = dpkt.ethernet.Ethernet(pkt)
        ports["cap"] = eth.data.data.sport
        return

def sendPkt(target_host, target_port, ports):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((target_host, int(target_port)))
    if result == 0:
        print "port is open"
        sock.send("1")
    else:
        print "port is closed"
    sock.close()

    time.sleep(0.1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex((proxy_host, int(proxy_port)))
    _, ports["term"] = sock.getsockname()
    sock.close()

if __name__ == '__main__':
    target_host = sys.argv[1]
    target_port = sys.argv[2]
    proxy_host  = sys.argv[3]
    proxy_port  = sys.argv[4]

    manager = multiprocessing.Manager()
    ports = manager.dict()

    f = 'tcp and dst host %s and dst port %s' % (proxy_host, proxy_port)
    p = multiprocessing.Process(target=capPkt, args=(f, ports))
    p.start()

    time.sleep(1)
    p2 = multiprocessing.Process(target=sendPkt, args=(target_host, target_port, ports))
    p2.start()

    p2.join()
    p.join()

    if ports["term"] == ports["cap"]:
        print "Fail"
        sys.exit(1)

    print "Success"
    sys.exit(0)
