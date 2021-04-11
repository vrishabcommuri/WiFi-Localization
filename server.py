#!/usr/bin/env python3

import socket
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from scipy import signal
# import matplotlib.pyplot as plt


UDP_IP = "172.26.7.230"
UDP_PORT1 = 5005
UDP_PORT2 = 5006
SAMPLE_RATE = 2e6

BUF_SIZE = int(3e5)
buffers = {UDP_PORT1:np.zeros(BUF_SIZE),
           UDP_PORT2:np.zeros(BUF_SIZE)}


def recv_udp_stream(port):
    sock = socket.socket(socket.AF_INET,    # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, port))
    
    # counter to track how much of the buffer we have filled
    c = 0

    while True:
        data, addr = sock.recvfrom(1024)

        arr = np.frombuffer(data, dtype='<f4') 
        
        for i in range(len(arr)):
            port_buf = buffers[port]
            port_buf[c] = arr[i]
            c += 1
        
            if c >= BUF_SIZE:
                return

def compute_buffer_delay():
    buf0 = buffers[UDP_PORT1]
    buf1 = buffers[UDP_PORT2]

    xcorr = signal.correlate(buf0, buf1, 'valid')
    delay = len(xcorr)/2 - np.argmax(np.abs(xcorr))

    return delay

# def delay_to_angle(delay):



if __name__ == '__main__':
    ############################################################################
    # Compute delay for a given source
    ############################################################################

    while True:
        input("Press 'Enter' to evaluate delay")
        # spawn two threads -- one per antenna -- to collect data
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(recv_udp_stream, UDP_PORT1)
            executor.submit(recv_udp_stream, UDP_PORT2)

        delay = compute_buffer_delay()
        print(f"Repositioned source produced a delay of {delay} samples")

    


    

