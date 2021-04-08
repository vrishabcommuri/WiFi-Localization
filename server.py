#!/usr/bin/env python3

import socket
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from scipy import signal
import matplotlib.pyplot as plt

UDP_IP = "172.26.7.230"
UDP_PORT1 = 5005
UDP_PORT2 = 5006

BUF_SIZE = int(10e6)
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
        
            if c == BUF_SIZE:
                return

if __name__ == '__main__':

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(recv_udp_stream, UDP_PORT1)
        executor.submit(recv_udp_stream, UDP_PORT2)

    print(len(buffers[UDP_PORT1]), len(buffers[UDP_PORT2]))

    # normalize signals
    data0 = buffers[UDP_PORT1]
    data1 = buffers[UDP_PORT2]

    data0 = (data0 - np.mean(data0))/np.std(data0)
    data1 = (data1 - np.mean(data1))/np.std(data1)

    xcorr = signal.correlate(data0, data1)

    delay = len(xcorr)/2 - np.argmax(xcorr)
    print(f"delay between elements is {delay} samples")