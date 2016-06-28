#!/usr/bin/env python

import socket
import sys
import pprint
import argparse
import datetime
from time import sleep

UDP_IP = "0.0.0.0"
UDP_PORT = 2101


parser = argparse.ArgumentParser(description="Count Number of UDP Packets that are received",
epilog="V1.0 (c) JCMBsoft 2016");
#parser.add_argument("-i","--Source_IP",default="",help="Source of UDP packets, leave blank for broadcast")
parser.add_argument("-p","--Source_Port",default=2101,help="Source port of UDP packets. Default 2101",type=int)
parser.add_argument("-t","--time", default=20,help="Number of seconds to count packets for")

parser.add_argument('--nagios', action='store_true',
                help='Return information in a way suitable for Nagios monitoring')
parser.add_argument('-w', '--warning', metavar='COUNT', type=int, default=18,
                help='return warning if received packets is less than COUNT. Nagios Mode only')
parser.add_argument('-c', '--critical', metavar='COUNT', type=int, default=16,
                help='return critical if received packets is less than COUNT, Nagios Mode only')

parser.add_argument('-W', '--high_warning', metavar='COUNT', type=int, default=22,
                help='return warning if received packets is more than COUNT. Nagios Mode only')
parser.add_argument('-C', '--high_critical', metavar='COUNT', type=int, default=24,
                help='return critical if received packets is more than COUNT, Nagios Mode only')


parser.add_argument("-T","--Tell", action='store_true',help="Tell the settings before starting")
parser.add_argument("-v","--Verbose", action='count',help="Display information on incomming -v, and outgoing -vv packets")

args = parser.parse_args()

#UDP_RECV_IP=args.Source_IP
UDP_RECV_IP=""
UDP_RECV_PORT=args.Source_Port
Verbose=args.Verbose
Test_Time=args.time


if args.Tell:
   if UDP_RECV_IP=="" :
      sys.stderr.write("Source: Broadcast:{}\n".format(UDP_RECV_PORT))
   else:
      sys.stderr.write("Source: {}:{}\n".format(UDP_RECV_IP,UDP_RECV_PORT))
   sys.stderr.write("Test Time:{}\n".format(str(Test_Time)))

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
                     
try:   #This fails on the Raspberry Pi for an unknown reason so we just ignore it
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except:
   pass
   
sock.bind((UDP_RECV_IP, UDP_RECV_PORT))
sock.setblocking(0)

Packets_In=0
start_time=datetime.datetime.now()
end_time=start_time+datetime.timedelta(0,Test_Time)
current_time=start_time
while current_time<=end_time:
   current_time=datetime.datetime.now()

   try:
      try:
         data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
      except :
         sleep(0.001) # We check for packets around 100 times a second. Without this we peg the CPU which is rude
         continue
      Packets_In+=1
      if Verbose:
         sys.stderr.write("Packet: {} From Address: {}:{} at {}\n".format(Packets_In,addr[0],addr[1],datetime.datetime.now()))

#      sys.stdout.write(data)
#      sys.stdout.flush()
   except KeyboardInterrupt:
      sys.stderr.write( "\n")
      sys.stderr.write("Received: {} packets in {}\n".format(Packets_In,datetime.datetime.now()-start_time))
      sys.stderr.write("\n")
      sys.exit(1)
   except:
      raise

if not args.nagios:
   sys.stderr.write( "\n")
   sys.stderr.write("Received: {} packets in {}\n".format(Packets_In,datetime.datetime.now()-start_time))
   sys.stderr.write("\n")
   sys.exit(0)

# Here we are reporting out for Nagios only
if Packets_In<=args.critical:
   print "CRITICAL - Not enough packets {}, threshold {}".format(Packets_In,str(args.critical))
   sys.exit(2)

if Packets_In<=args.warning:
   print "WARNING - Not enough packets {}, threshold {}".format(Packets_In,str(args.warning))
   sys.exit(1)

if args.high_critical and Packets_In>=args.high_critical:
   print "CRITICAL - Too many packets {}, threshold {}".format(Packets_In,str(args.high_critical))
   sys.exit(2)

if args.high_warning and Packets_In>=args.high_warning:
   print "warning - Too many packets {}, threshold {}".format(Packets_In,str(args.high_warning))
   sys.exit(1)

print "OK - {}, in {} seconds".format(Packets_In,str(Test_Time))
