#! /usr/bin/env python3

import socket
import datetime
from collections import deque
from pprint import pprint
import argparse
import sys
from struct import *
import binascii

parser = argparse.ArgumentParser(description="Relay UDP Packets", epilog=" (c) JCMBsoft 2020");
parser.add_argument("-i","--Source_IP",default="0.0.0.0",help="IP Address of interface to listen for UDP packets on. 0.0.0.0 is all")
parser.add_argument("-p","--Source_Port",default=2101,help="Source port of UDP packets. Default 2101",type=int)
parser.add_argument("-I","--Destination_IP",default="",help="Destination of MUX UDP packets", required=True)
parser.add_argument("-P","--Destination_Port",default="2102",help="Source port of UDP packets. Default 2102",type=int)
parser.add_argument("-T","--Tell", action='store_true',help="Tell the settings before starting")
parser.add_argument("-V","--Verbose", action='count',help="Display information on incoming -v, and outgoing -vv packets")
parser.add_argument("-S","--Status", action='store_true',help="Display a . for each incoming packet")

args = parser.parse_args()

UDP_RECV_IP=args.Source_IP
UDP_RECV_PORT=args.Source_Port
UDP_TRAN_IP=args.Destination_IP
UDP_TRAN_PORT=args.Destination_Port

Dots=args.Status

Verbose=args.Verbose
if not Verbose:
   Verbose=0

if args.Tell:
   print ("\n")
   if UDP_RECV_IP=="" :
      print ("Source: Broadcast:{}\n".format(UDP_RECV_PORT))
   else:
      print ("Source: {}:{}\n".format(UDP_RECV_IP,UDP_RECV_PORT))
   print ("Destination: {}:{}\n".format(UDP_TRAN_IP,UDP_TRAN_PORT))
   print ("")


def setup_input_socket(IP,PORT):
   Timeout=0.001
   in_sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
#   IP="0.0.0.0"
   if Verbose:
      print ("Input: IP:Port {}:{}\n".format(IP,PORT))
   in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
   in_sock.bind((IP, PORT))

   #in_sock.setblocking(0)
   #in_sock.settimeout(Timeout) # This means that we will wait at most 0.01 second for a UDP packet
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
   SEQ_Number=0


   while True:
       try:
          data, addr = in_sock.recvfrom(4000) # buffer size is 4000 bytes
#          print ("Len: {}".format(len(data)))
          received_time=datetime.datetime.now()
          Packets_In+=1
          if SEQ_Number!=255:
             SEQ_Number+=1
          else:
             SEQ_Number=0
#          print (SEQ_Number)
#          print ("")

          if Verbose>=1:
             sys.stderr.write("Received message # "+str(Packets_In)+" : bytes (" + str(len (data)) + ") from " + addr[0] + " at " +str(received_time) +"\n")
          else:
             if Dots:
                sys.stderr.write(".")
                if Packets_In % 100==0:
                  sys.stderr.write ("\n")

          data_length=len(data)
          if Verbose:
             print ("UDP Packet: {}".format(data_length))
          if data_length > 1300:
#             Packet_Trailer=pack('!B',0xAE,SEQ_Number,2,1,1000)
             Packet_1_Header=pack('!BBBBH',0xAE,SEQ_Number,2,1,0)
             Packet_2_Header=pack('!BBBBH',0xAE,SEQ_Number,2,2,1000)
             Packet_1=Packet_1_Header+data[:1000]
             Packet_2=Packet_2_Header+data[1000:]
             out_sock.sendto(Packet_1, (UDP_TRAN_IP, UDP_TRAN_PORT))
             out_sock.sendto(Packet_2, (UDP_TRAN_IP, UDP_TRAN_PORT))
             if Verbose:
                print ("ID: {} SEQ_Number: {} Num_Packets: {} This_Packet: {} Length:{}".format(0xAE,SEQ_Number,2,1,1000))
                print ("ID: {} SEQ_Number: {} Num_Packets: {} This_Packet: {} Length:{}".format(0xAE,SEQ_Number,2,2,data_length-1000))

             Packets_Out+=2
#             print ("Send double\n")
          else:
             Packet_1_Header=pack('!BBBBH',0xAE,SEQ_Number,1,1,0)
             if Verbose:
                print ("ID: {} SEQ_Number: {} Num_Packets: {} This_Packet: {} Length:{}".format(0xAE,SEQ_Number,1,1,data_length))


             Packet_1=Packet_1_Header+data
             out_sock.sendto(Packet_1, (UDP_TRAN_IP, UDP_TRAN_PORT))
             Packets_Out+=1
#             print ("Send Single Start\n")
#             print (binascii.hexlify(Packet_1_Header))
#             print ("\n")
#             print (binascii.hexlify(data))
#             print ("\n")
#             print (binascii.hexlify(Packet_1))
#             print ("Send Single End\n")

       except KeyboardInterrupt:
          return (Packets_In,Packets_Out)
#          raise
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
   print ("Packets Received: {} Sent: {}\n").format(Packets_In,Packets_Out)

print ("\n")
print ("Received: {} Sent: {} in {}\n".format(Packets_In,Packets_Out,datetime.datetime.now()-start_time))
