#!/usr/bin/env python3

import socket
import sys
import pprint
import argparse
import datetime
import binascii

UDP_IP = "0.0.0.0"
UDP_PORT = 2101


parser = argparse.ArgumentParser(description="Simple UDP Packet receiver that outputs packet length to stdout.",
epilog="V2.0 (c) JCMBsoft 2021");
#parser.add_argument("-i","--Source_IP",default="",help="Source of UDP packets, leave blank for broadcast",type=str)
parser.add_argument("-p","--Source_Port",default=2101,help="Source port of UDP packets. Default 2101",type=int)
parser.add_argument("-T","--Tell", action='store_true',help="Tell the settings before starting")
parser.add_argument("-v","--Verbose", action='count',help="Display information on incomming -v, and outgoing -vv packets")
parser.add_argument("-W","--When", action='store_true',help="Display the time that the packet was received")
parser.add_argument("-E","--Epoch", type=float,default=0.0, help="Display the total size of data that was received in that amount of time. In seconds. Note that generally this should be around 1/2 the output rate")

args = parser.parse_args()

#UDP_RECV_IP=args.Source_IP
UDP_RECV_IP=""
UDP_RECV_PORT=args.Source_Port
Verbose=args.Verbose
Epoch_Interval=args.Epoch
Display_Time=args.When


if args.Tell:
   if UDP_RECV_IP=="" :
      sys.stderr.write("Source: Broadcast:{}\n".format(UDP_RECV_PORT))
   else:
      sys.stderr.write("Source: {}:{}\n".format(UDP_RECV_IP,UDP_RECV_PORT))
   sys.stderr.write("Verbose: {}\n".format(Verbose))
   sys.stderr.write("When: {}\n".format(Display_Time))
   sys.stderr.write("Epoch: {}\n".format(Epoch_Interval))
   sys.stderr.write("\n")


sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
try:   #This fails on the Raspberry Pi for an unknown reason so we just ignore it
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except:
   pass

sock.bind((UDP_RECV_IP, UDP_RECV_PORT))

Packets_In=0
start_time=datetime.datetime.now()

data=None
Epoch_Start_Time=None
Epoch_Count=0
Epoch_Total=0
Epoch_Delta=datetime.timedelta(milliseconds=Epoch_Interval*1000)
Packet_Length=0
rcv_time=None


while True:
   try:
      data, addr = sock.recvfrom(8196) # buffer size is 8196 bytes
      previous_rcv_time=rcv_time

      rcv_time=datetime.datetime.now()
      Packets_In+=1
      Packet_Length=len(data)


      if Epoch_Start_Time==None:
         Epoch_Start_Time=rcv_time
         Epoch_Count=1
         Epoch_Total=Packet_Length
      else:
#         sys.stdout.write("   DEBUG: {} {} {} {} {}\n".format(Epoch_Start_Time, rcv_time, Epoch_Start_Time + Epoch_Delta, rcv_time -Epoch_Start_Time, rcv_time >= (Epoch_Start_Time + Epoch_Delta)))
         if Epoch_Interval != 0.0 and (rcv_time >= (Epoch_Start_Time + Epoch_Delta)):
            if Display_Time:
               sys.stdout.write("Epoch: {} {} Data: {} Packets: {}\n".format(Epoch_Start_Time, previous_rcv_time, Epoch_Total, Epoch_Count))
            else:
               sys.stdout.write("{},{} \n".format(Epoch_Total, Epoch_Count))
            Epoch_Start_Time=rcv_time
            Epoch_Count=1
            Epoch_Total=Packet_Length
         else:
            Epoch_Count+=1
            Epoch_Total+=Packet_Length

      if Verbose:
         sys.stderr.write("Packet: {} From Address: {}:{} at {}\n".format(Packets_In,addr[0],addr[1],rcv_time))
         sys.stderr.flush()

      if Display_Time:
         if Epoch_Interval == 0.0 :
            sys.stdout.write("Time: {} Length: {}\n".format(rcv_time, len(data)))
      else:
         if Epoch_Interval == 0.0 :
            sys.stdout.write(str(len(data))+"\n")

      sys.stdout.flush()

   except KeyboardInterrupt:
      sys.stderr.write( "\n")
      sys.stderr.write("Received: {} packets in {}\n".format(Packets_In,datetime.datetime.now()-start_time))
      sys.stderr.write("\n")
      sys.exit(0)
   except:
      raise
