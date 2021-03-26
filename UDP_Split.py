#! /usr/bin/env python

import socket
import datetime
from collections import deque
from pprint import pprint
import argparse
import sys
from random import randint

UDP_RECV_IP = "" # Broadcast Address
UDP_TRAN_IP = "255.255.255.255" # Broadcast Address
UDP_RECV_PORT = 2101
UDP_TRAN_PORT = 2103

Timeout=0.1


parser = argparse.ArgumentParser(description="Split UDP packets",
epilog="""
Note that the system never changes the order of packets. So if the Number*Delay > than the time between packets you will not get what you expect.

V1.0 (c) JCMBsoft 2018
""");
parser.add_argument("-i","--Source_IP",default="",help="Source of UDP packets, leave blank for broadcast")
parser.add_argument("-p","--Source_Port",default=2101,help="Source port of UDP packets. Default 2101",type=int)
parser.add_argument("-I","--Destination_IP",default="255.255.255.255",help="Source of UDP packets, use 255.255.255.255 for broadcast")
parser.add_argument("-P","--Destination_Port",default="2103",help="Source port of UDP packets. Default 2103",type=int)
parser.add_argument("-T","--Tell", action='store_true',help="Tell the settings before starting")
parser.add_argument("-v","--Verbose", action='count',help="Display information on incomming -v, and outgoing -vv packets")
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


def send_items (out_sock,IP,PORT,Packets_Out, GPS_Packet, GLONASS_Packet, CMRPlus_Packet, RTXOffset_Packet,packet_size=0,drop_rate=0):
  current_time=datetime.datetime.now()

#   if Packets_Out % 8 == 0 or  Packets_Out % 8 == 4 :
#      Data+=GPS_Packet

#   if Packets_Out % 20 == 4 or  Packets_Out % 20 == 4 or Packets_Out % 20 == 4 or Packets_Out % 20 == 4 :
  Data=GLONASS_Packet
  Data+=GPS_Packet
  Data+=CMRPlus_Packet
  sys.stderr.write("Sending message total bytes ("+ str(len(Data))+ ") at "+ str(current_time) + "\n")
#  Data+=RTXOffset_Packet
  if  packet_size == 0 :
    if randint(1,100) < drop_rate:
        sys.stderr.write("Dropping message  #"+str(Packets_Out)+ " : bytes ("+ str(len(Data))+ ") at "+ str(current_time) + "\n")
    else:
        sys.stderr.write("Sending message  #"+str(Packets_Out)+ " : bytes ("+ str(len(Data))+ ") at "+ str(current_time) + "\n")
        out_sock.sendto(Data, (IP, PORT))
    Packets_Out+=1
  else:
    while len(Data) != 0:
        send_packet=Data[:packet_size]
        Data=Data[packet_size:]
        if randint(1,100) < drop_rate:
            sys.stderr.write("Dropping message  #"+str(Packets_Out)+ " : bytes ("+ str(len(send_packet))+ ") at "+ str(current_time) + "\n")
        else:
            sys.stderr.write("Sending message  #"+str(Packets_Out)+ " : bytes ("+ str(len(send_packet))+ ") at "+ str(current_time) + "\n")
            out_sock.sendto(send_packet, (IP, PORT))
        Packets_Out+=1
  return(Packets_Out)


def setup_input_socket(IP,PORT,Timeout):
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
   sock.bind(('0.0.0.0', 1444))
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   return sock

def process(in_sock,out_sock,IP,PORT,Dots):

#   Data_Queue=deque()
   Packets_In=0
   Packets_Out=0
   GPS_Packet=None
   GLONASS_Packet=None
   CMRPlus_Packet=None
   RTXOffset_Packet=None

   while True:
       try:
          data, addr = in_sock.recvfrom(1024) # buffer size is 1024 bytes
          received_time=datetime.datetime.now()
          Packets_In+=1
          message_type=ord(data[2])
          message_version=ord(data[4])
          message_version >>=5
          subtype=ord(data[5])
          subtype >>=5

          if message_type==0x93:
            if subtype==0:
               GPS_Packet=data
            elif subtype==3:
               GPS_Packet=None
               GLONASS_Packet=None
               CMRPlus_Packet=None
               RTXOffset_Packet=None
               GLONASS_Packet=data
          elif message_type==0x94:
               CMRPlus_Packet=data
          elif message_type==0x98:
               RTXOffset_Packet=data

          if Verbose>=1:
             sys.stderr.write("Received message # "+str(Packets_In)+" : bytes (" + str(len (data)) + ") from " + addr[0] + " at " +str(received_time) +"\n")
             sys.stderr.write("Message: {} Version: {} Subtype: {}".format(hex(message_type),message_version,subtype))
             sys.stderr.write("\n")

          else:
             if Dots:
                sys.stderr.write(".")
                if Packets_In % 100==0:
                  sys.stderr.write ("\n")


          if GPS_Packet and GLONASS_Packet and CMRPlus_Packet and RTXOffset_Packet:
#            print "Got all packets"
            Packets_Out=send_items(out_sock,IP,PORT,Packets_Out,GPS_Packet, GLONASS_Packet, CMRPlus_Packet, RTXOffset_Packet,packet_size=220,drop_rate=10)
            GPS_Packet=None
            GLONASS_Packet=None
            CMRPlus_Packet=None
            RTXOffset_Packet=None


#          TimeOuts=0
#          Current_Packet=0
#          Data_Queue.append([received_time+datetime.timedelta(seconds=Base_Delay+Current_Packet*Packet_Delay),addr,data,received_time,Packets_In])
#          print len(Data_Queue)
   #       pprint (Data_Queue)


       except KeyboardInterrupt:
          return (Packets_In,Packets_Out)
          raise
       except socket.timeout:
#          Packets_Out=send_items(Data_Queue,out_sock,IP,PORT,Packets_Out)
   #       print "Time Out: " + str(TimeOuts)

          pass

       except:
          raise


out_sock=setup_output_socket(UDP_TRAN_IP=="255.255.255.255")
in_sock=setup_input_socket(UDP_RECV_IP,UDP_RECV_PORT,0.1)
start_time=datetime.datetime.now()
Packets_In=0
Packets_Out=0

try:
   (Packets_In,Packets_Out)=process(in_sock,out_sock,UDP_TRAN_IP,UDP_TRAN_PORT,Dots)
except KeyboardInterrupt:
   print "Packets Received: {} Sent: {}".format(Packets_In,Packets_Out)

print ""
print "Received: {} Sent: {} in {}".format(Packets_In,Packets_Out,datetime.datetime.now()-start_time)
