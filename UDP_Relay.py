#! /usr/bin/env python

import socket
import datetime
from collections import deque
from pprint import pprint
import argparse
import sys

UDP_RECV_IP = "" # Broadcast Address
UDP_TRAN_IP = "255.255.255.255" # Broadcast Address
UDP_RECV_PORT = 2101
UDP_TRAN_PORT = 2103

Base_Delay= 5.0
Packet_Delay=0.1
Number_Packets=9


parser = argparse.ArgumentParser(description="Delay and/or duplicate UDP packets",
epilog="""
Note that the system never changes the order of packets. So if the Number*Delay > than the time between packets you will not get what you expect.

V1.0 (c) JCMBsoft 2016
""");
parser.add_argument("-i","--Source_IP",default="",help="Source of UDP packets, leave blank for broadcast")
parser.add_argument("-p","--Source_Port",default=2101,help="Source port of UDP packets. Default 2101",type=int)
parser.add_argument("-I","--Destination_IP",default="255.255.255.255",help="Source of UDP packets, use 255.255.255.255 for broadcast")
parser.add_argument("-P","--Destination_Port",default="2103",help="Source port of UDP packets. Default 2103",type=int)
parser.add_argument("-T","--Tell", action='store_true',help="Tell the settings before starting")
parser.add_argument("-V","--Verbose", action='count',help="Display information on incomming -v, and outgoing -vv packets")
parser.add_argument("-S","--Status", action='store_true',help="Display a . for each incomming packet")

args = parser.parse_args()

UDP_RECV_IP=args.Source_IP
UDP_RECV_PORT=args.Source_Port
UDP_TRAN_IP=args.Destination_IP
UDP_TRAN_PORT=args.Destination_Port

Dots=args.Status

Verbose=args.Verbose

if args.Tell:
   print ""
   if UDP_RECV_IP=="" :
      print "Source: Broadcast:{}".format(UDP_RECV_PORT)
   else:
      print "Source: {}:{}".format(UDP_RECV_IP,UDP_RECV_PORT)
   print "Destination: {}:{}".format(UDP_TRAN_IP,UDP_TRAN_PORT)
   print ""


def setup_input_socket(IP,PORT):
   Timeout=0.001
   in_sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
   in_sock.bind((IP, PORT))
   in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
   #in_sock.setblocking(0)
   in_sock.settimeout(Timeout) # This means that we will wait at most 0.01 second for a UDP packet
   # You might think that we would get to 100Hz but in practice it is more like 80 on the MacBook Pro
   return in_sock


def setup_output_socket(Broadcast):
   sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
   if Broadcast :
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      if Verbose:
         sys.stderr.write("Outputting on broadcast address\n")
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   return sock

def process(in_sock,out_sock,IP,PORT,Dots):

   Packets_In=0
   Packets_Out=0

   while True:
       try:
          data, addr = in_sock.recvfrom(4000) # buffer size is 4000 bytes
          received_time=datetime.datetime.now()
          Packets_In+=1
          if Verbose>=1:
             sys.stderr.write("Received message # "+str(Packets_In)+" : bytes (" + str(len (data)) + ") from " + addr[0] + " at " +str(received_time) +"\n")
          else:
             if Dots:
                sys.stderr.write(".")
                if Packets_In % 100==0:
                  sys.stderr.write ("\n")
          out_sock.sendto(data, (UDP_TRAN_IP, UDP_TRAN_PORT))
          Packets_Out+=1


       except KeyboardInterrupt:
          return (Packets_In,Packets_Out)
          raise
       except socket.timeout:
          pass

       except:
          raise


out_sock=setup_output_socket(UDP_TRAN_IP=="255.255.255.255")
in_sock=setup_input_socket(UDP_RECV_IP,UDP_RECV_PORT)
start_time=datetime.datetime.now()
Packets_In=0
Packets_Out=0

try:
   (Packets_In,Packets_Out)=process(in_sock,out_sock,UDP_TRAN_IP,UDP_TRAN_PORT,Dots)
except KeyboardInterrupt:
   print "Packets Received: {} Sent: {}".format(Packets_In,Packets_Out)

print ""
print "Received: {} Sent: {} in {}".format(Packets_In,Packets_Out,datetime.datetime.now()-start_time)
