#!/usr/bin/env python

import socket
import sys
import pprint
import argparse
import datetime

UDP_IP = "0.0.0.0"
UDP_PORT = 2101


parser = argparse.ArgumentParser(description="Simple UDP Packet broadcaster that sends the current time",
epilog="V1.0 (c) JCMBsoft 2016");
parser.add_argument("-i","--Source_IP",default="",help="Source of UDP packets, leave blank for broadcast")
parser.add_argument("-p","--Source_Port",default=2101,help="Source port of UDP packets. Default 2101",type=int)
parser.add_argument("-T","--Tell", action='store_true',help="Tell the settings before starting")
parser.add_argument("-V","--Verbose", action='count',help="Display information on incomming -v, and outgoing -vv packets")

args = parser.parse_args()

UDP_RECV_IP=args.Source_IP
UDP_RECV_PORT=args.Source_Port
Verbose=args.Verbose


if args.Tell:
   if UDP_RECV_IP=="" :
      sys.stderr.write("Source: Broadcast:{}\n".format(UDP_RECV_PORT))
   else:
      sys.stderr.write("Source: {}:{}\n".format(UDP_RECV_IP,UDP_RECV_PORT))

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
sock.bind((UDP_RECV_IP, UDP_RECV_PORT))

Packets_In=0
start_time=datetime.datetime.now()

while True:
   try:
      data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
      Packets_In+=1
      if Verbose:
         sys.stderr.write("Packet: {} From Address: {}:{}\n".format(Packets_In,addr[0],addr[1]))

      sys.stdout.write(data)
      sys.stdout.flush()
   except KeyboardInterrupt:
      sys.stderr.write( "\n")
      sys.stderr.write("Received: {} packets in {}\n".format(Packets_In,datetime.datetime.now()-start_time))
      sys.stderr.write("\n")
      sys.exit(0)
   except:
      raise