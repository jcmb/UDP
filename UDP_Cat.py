#!/usr/bin/env python3

import socket
import sys
import pprint
import argparse
import datetime
import binascii

UDP_IP = "0.0.0.0"
UDP_PORT = 2101


parser = argparse.ArgumentParser(
    description="Simple UDP Packet receiver that outputs to StdOut.",
    epilog="V1.0 (c) JCMBsoft 2016",
)
parser.add_argument(
    "-i",
    "--Source_IP",
    default="",
    help="Source of UDP packets, leave blank for broadcast",
    type=str,
)
parser.add_argument(
    "-p",
    "--Source_Port",
    default=2101,
    help="Source port of UDP packets. Default 2101",
    type=int,
)
parser.add_argument("-c", "--Client", help="Client Connection", action="store_true")
parser.add_argument(
    "-T", "--Tell", action="store_true", help="Tell the settings before starting"
)
parser.add_argument(
    "-v",
    "--Verbose",
    action="count",
    help="Display information on incomming -v, and outgoing -vv packets",
)
parser.add_argument(
    "-H", "--Hex", action="store_true", help="Display packet information in hex"
)

args = parser.parse_args()

if args.Source_IP:
    UDP_RECV_IP = args.Source_IP
else:
     UDP_RECV_IP = None
#    UDP_RECV_IP = "192.168.128.3"
# UDP_RECV_IP=""

UDP_RECV_PORT = args.Source_Port
Verbose = args.Verbose
Hex = args.Hex
Client = args.Client


if args.Tell:
    if UDP_RECV_IP == "":
        sys.stderr.write("Source: Broadcast:{}\n".format(UDP_RECV_PORT))
    else:
        if Client:
            sys.stderr.write("Client: {}:{}\n".format(UDP_RECV_IP, UDP_RECV_PORT))
        else:
            sys.stderr.write("Source: {}:{}\n".format(UDP_RECV_IP, UDP_RECV_PORT))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
try:  # This fails on the Raspberry Pi for an unknown reason so we just ignore it
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except:
    pass

sock.bind(("", UDP_RECV_PORT))

Packets_In = 0
start_time = datetime.datetime.now()

if Client:
    # Message to send
    message = "Hello, UDP!"

    try:
        # Send the message
        sock.sendto(message.encode("utf-8"), (UDP_RECV_IP, UDP_RECV_PORT))
        print(f"Message sent to {UDP_RECV_IP}:{UDP_RECV_PORT}")
    except:
        print(f"Message NOT sent to {UDP_RECV_IP}:{UDP_RECV_PORT}")


data = None
while True:
    try:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes

        if Verbose:
            sys.stderr.write(
                "\nPacket: {} From Address: {}:{} at {}\n".format(
                    Packets_In, addr[0], addr[1], datetime.datetime.now()
                )
            )
            sys.stderr.flush()

        if UDP_RECV_IP:
            if (addr[0]) != UDP_RECV_IP:
                continue

        Packets_In += 1


        if Hex:
            sys.stdout.write("\n")
            sys.stdout.write(binascii.hexlify(data).decode("utf-8"))
            sys.stdout.write("\n")
        else:
            sys.stdout.write(data.decode("utf-8", errors="replace"))

        sys.stdout.flush()

    except KeyboardInterrupt:
        sys.stderr.write("\n")
        sys.stderr.write(
            "Received: {} packets in {}\n".format(
                Packets_In, datetime.datetime.now() - start_time
            )
        )
        sys.stderr.write("\n")
        sys.exit(0)
    except:
        raise
