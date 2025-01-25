#! /usr/bin/env python3

import socket
import datetime
from time import  sleep
import argparse
import sys


parser = argparse.ArgumentParser(description="Simple UDP Packet broadcaster that sends the current time",
epilog="V1.0 (c) JCMBsoft 2016");
parser.add_argument("-I","--Destination_IP",default="255.255.255.255",help="Source of UDP packets, use 255.255.255.255 for broadcast")
parser.add_argument("-P","--Destination_Port",default="2103",help="Source port of UDP packets. Default 2103",type=int)
parser.add_argument("-T","--Tell", action='store_true',help="Tell the settings before starting")
parser.add_argument("-W","--Wait", default=5.0  ,help="Amount to delay before sending the next packet, in seconds, decimals delays supported. Default 5.0",type=float)
parser.add_argument("-V","--Verbose", action='count',help="Display information on incomming -v, and outgoing -vv packets")
parser.add_argument("-S","--Status", action='store_true',help="Display a . for each incomming packet. Otherwise print the data")

args = parser.parse_args()

UDP_TRAN_IP=args.Destination_IP
UDP_TRAN_PORT=args.Destination_Port

Packet_Every=args.Wait
Dots=args.Status
Verbose=args.Verbose

if args.Tell:
   sys.stderr.write("UDP target IP: "+UDP_TRAN_IP+"\n")
   sys.stderr.write("UDP target port: "+str(UDP_TRAN_PORT)+"\n")
   sys.stderr.write("Packet Every: "+str(Packet_Every)+"(s)\n")

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


if UDP_TRAN_IP=="255.255.255.255":
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
   if Verbose:
      sys.stderr.write("Outputting on broadcast address\n\n")

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setblocking(0)

Packets_Out=0
Packets_In=0

start_time=datetime.datetime.now()
while True:
   try:
      MESSAGE=str(datetime.datetime.now())+"\n"
      MESSAGE=MESSAGE.encode('utf-8')
      sock.sendto(MESSAGE, (UDP_TRAN_IP, UDP_TRAN_PORT))
      Packets_Out+=1
      if Verbose:
         sys.stderr.write("Sent message # " + str (Packets_Out) + " : "+MESSAGE)

      try:
         while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            Packets_In+=1
            if Dots:
               sys.stderr.write(".")
               if Packets_In % 100==0:
                   sys.stderr.write ("\n")
            else:
               print(("received message: %s" % data))


      except socket.error:
          pass
      sleep(Packet_Every)
   except KeyboardInterrupt:
      print("")
      print("Sent: {} packets in {}".format(Packets_Out,datetime.datetime.now()-start_time))
      print("")
      sys.exit(0)
   except:
      raise

