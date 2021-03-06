import time
import signal
import socket
import inspect
import struct
import sys
import threading
from common import carry_around_add, checksum_computation

TIMEOUT_TIMER = 1
DATA_PACKET_IDENTIFIER = 21845
ACK_PACKET_IDENTIFIER = 43690
ack_number = 0
last_seq_number = 0
data_to_send = []
sending_array = {'x':'x'}
packets_sent = 0
total_packets = 1
packet_ack = 0
lock = threading.Lock()

class Sender(threading.Thread):
    def __init__(self, host, port, file, N, MSS, socket_client):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.file = file
        self.N    = N
        self.MSS  = MSS
        self.socket_client = socket_client
        self.start()

    def run(self):
        global sending_array
        global lock
        global ack_number
        global last_seq_number
        global total_packets
        global data_to_send
        global packet_ack

        current_number = 0
        server = (self.host, self. port)

        while packet_ack < total_packets:
            # If ther were failures in a window
            while current_number - ack_number >= self.N:
                lock.acquire()
                if ack_number < total_packets and ack_number < current_number:
                    if sending_array.get(ack_number):
                        try:
                            if (time.time()-((sending_array[ack_number])[1])) >= TIMEOUT_TIMER:
                                for packet in range(ack_number, current_number):
                                    data = sending_array [packet][0]
                                    sending_array[packet] = (data, time.time())
                                    self.socket_client.sendto(data,server)
                                    print('Timeout, Sequence Number = '+str(packet))
                        except KeyError:
                            pass
                lock.release()

            # Failures in last window which may be lesser than the window size
            lock.acquire()
            if total_packets <= self.N and ack_number < current_number:
                if sending_array.get(ack_number):
                    try:
                        if (time.time()-((sending_array[ack_number])[1])) >= TIMEOUT_TIMER:
                            for packet in range(ack_number, current_number):
                                data = sending_array [packet][0]
                                sending_array[packet] = (data, time.time())
                                self.socket_client.sendto(data,server)
                                print('Timeout, Sequence Number = '+str(packet))
                    except KeyError:
                        pass
            lock.release()

            # If there is still something lagging behind
            lock.acquire()
            if ack_number < total_packets and ack_number < current_number:
                if sending_array.get(ack_number):
                    try:
                        if (time.time()-((sending_array[ack_number])[1])) >= TIMEOUT_TIMER:
                            for packet in range(ack_number, current_number):
                                data = sending_array [packet][0]
                                sending_array[packet] = (data, time.time())
                                self.socket_client.sendto(data,server)
                                print('Timeout, Sequence Number = '+str(packet))
                    except KeyError:
                        pass
            lock.release()

            # Main sending 
            lock.acquire()
            if current_number < total_packets:
                sending_array[current_number] = (data_to_send[current_number],time.time())
                self.socket_client.sendto(data_to_send[current_number], server)
                current_number = current_number + 1
            lock.release()

class Acknowledgment(threading.Thread):
    def __init__(self, socket_client):
        threading.Thread.__init__(self)
        self.socket_client = socket_client
        self.start()

    def run(self):
        global sending_array
        global lock
        global ack_number
        global last_seq_number
        global total_packets
        global data_to_send
        global packet_ack

        try:
            while packet_ack < total_packets:
                acknowledgement, address = self.socket_client.recvfrom(2048)
                ack_number = ack_number+1
                packet_ack  = packet_ack + 1
                seq_number = struct.unpack('=I', acknowledgement[0:4])
                seq_number = int(seq_number[0])
                acknowledgement_check = struct.unpack('=H', acknowledgement[6:8])
                # If successful acknowledgement, delete packet. 
                if acknowledgement_check[0] == ACK_PACKET_IDENTIFIER:
                    lock.acquire()
                    del sending_array[seq_number-1]
                    lock.release()

        except:
            self.socket_client.close()

def prepare(file, MSS):
    FILE = open(file,'rb')
    FILE_COPY = open(file, 'rb')
    data = FILE.read(MSS)
    data_copy = FILE_COPY.read(MSS)
    seq = 1
    while data_copy:
        seq+=1
        data_copy = FILE_COPY.read(MSS)
    sequence_number = 1
    while data:
        file_content = str(data,'UTF-8',errors='replace')
        checksum = checksum_computation(file_content)
        checksum = struct.pack('=H', checksum)
        seq_number = struct.pack('=L',sequence_number)
        data_sent = file_content.encode('UTF-8','ignore')
        data_packet = struct.pack('=h',DATA_PACKET_IDENTIFIER)
        max_seq = struct.pack('=L',seq)
        packet = seq_number + checksum + data_packet + max_seq + data_sent
        # data_to_send.append(packet)
        data = FILE.read(MSS)
        sequence_number += 1
    return 

def output_data(host, port, N, MSS, endTime, startTime):
    print('Total Time Taken (Delay):'+str(endTime-startTime))
    return

def rdt_send():
    host = sys.argv[1]
    port = int(sys.argv[2])
    file = sys.argv[3]
    N = int(sys.argv[4])
    MSS = int(sys.argv[5])
    startTime = time.time()
    global data_to_send
    global total_packets
    global ack_number

    client_port = 4443
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_client.bind(('', client_port))
    FILE = open(file,'rb')
    FILE_COPY = open(file, 'rb')
    data = FILE.read(MSS)
    data_copy = FILE_COPY.read(MSS)
    seq = 1
    while data_copy:
        seq+=1
        data_copy = FILE_COPY.read(MSS)
    prepare(file,MSS)
    sequence_number = 1
    while data:
        file_content = str(data,'UTF-8',errors='replace')
        checksum = checksum_computation(file_content)
        checksum = struct.pack('=H', checksum)
        seq_number = struct.pack('=L',sequence_number)
        data_sent = file_content.encode('UTF-8','ignore')
        data_packet = struct.pack('=h',DATA_PACKET_IDENTIFIER)
        max_seq = struct.pack('=L',seq)
        packet = seq_number + checksum + data_packet + max_seq + data_sent
        data_to_send.append(packet)
        data = FILE.read(MSS)
        sequence_number += 1

    file_content = "0101end0101"
    checksum = checksum_computation(file_content)
    checksum = struct.pack('=H', checksum)
    seq_number = struct.pack('=L',sequence_number)
    data_sent = file_content.encode('UTF-8','ignore')
    data_packet = struct.pack('=h',DATA_PACKET_IDENTIFIER)
    max_seq = struct.pack('=L',seq)
    packet = seq_number + checksum + data_packet + max_seq + data_sent
    data_to_send.append(packet)

    total_packets = len(data_to_send)
    ACKs = Acknowledgment(socket_client)

    transmitted_data = Sender(host, port, file, N, MSS, socket_client)
    transmitted_data.join()
    ACKs.join()
    endTime = time.time()
    server = (host,port)
    socket_client.close()
    output_data(host, port, N, MSS, endTime, startTime)


if __name__ == '__main__':
    rdt_send()