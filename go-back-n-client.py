import time
import signal
import socket
import inspect
import struct
import sys
import threading

TIMEOUT_TIMER = 3
DATA_PACKET_IDENTIFIER = 21845
ack_number = 0
last_seq_number = 0
data_to_send = []
send_buffer = {'x':'x'}
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
        global send_buffer
        global lock
        global ack_number
        global last_seq_number
        global total_packets
        global data_to_send
        global packet_ack

        current_number = 0
        server = (self.host, self. port)

        while packet_ack < total_packets:
            #go-back-n main logic
            while current_number - ack_number >= self.N:
                lock.acquire()
                if ack_number < total_packets and ack_number < current_number:
                    if send_buffer.get(ack_number):
                        try:
                            if (time.time()-((send_buffer[ack_number])[1])) >= TIMEOUT_TIMER:
                                for packet in range(ack_number, current_number):
                                    data = send_buffer [packet][0]
                                    send_buffer[packet] = (data, time.time())
                                    self.socket_client.sendto(data,server)
                                    print('Timeout, Sequence Number = '+str(packet))
                        except KeyError:
                            pass
                lock.release()

            lock.acquire()
            if total_packets <= self.N and ack_number < current_number:
                if send_buffer.get(ack_number):
                    try:
                        if (time.time()-((send_buffer[ack_number])[1])) >= TIMEOUT_TIMER:
                            for packet in range(ack_number, current_number):
                                data = send_buffer [packet][0]
                                send_buffer[packet] = (data, time.time())
                                self.socket_client.sendto(data,server)
                                print('Timeout, Sequence Number = '+str(packet))
                    except KeyError:
                        pass
            lock.release()


            lock.acquire()
            if ack_number < total_packets and ack_number < current_number:
                if send_buffer.get(ack_number):
                    try:
                        if (time.time()-((send_buffer[ack_number])[1])) >= TIMEOUT_TIMER:
                            for packet in range(ack_number, current_number):
                                data = send_buffer [packet][0]
                                send_buffer[packet] = (data, time.time())
                                self.socket_client.sendto(data,server)
                                print('Timeout, Sequence Number = '+str(packet))
                    except KeyError:
                        pass
            lock.release()

            lock.acquire()
            if current_number < total_packets:
                send_buffer[current_number] = (data_to_send[current_number],time.time())
                self.socket_client.sendto(data_to_send[current_number], server)
                current_number = current_number + 1
            lock.release()

class Acknowledgment(threading.Thread):
    def __init__(self, socket_client):
        threading.Thread.__init__(self)
        self.socket_client = socket_client
        self.start()

    def run(self):
        global send_buffer
        global lock
        global ack_number
        global last_seq_number
        global total_packets
        global data_to_send
        global packet_ack

        try:
            while packet_ack < total_packets:
                acknowledgement, address = self.socket_client.recvfrom(2048)
                packet_ack  = packet_ack + 1
                ack_number = ack_number+1
                sequence_number_received = struct.unpack('=I', acknowledgement[0:4])
                sequence_number_received = int(sequence_number_received[0])
                acknowledgement_check = struct.unpack('=H', acknowledgement[6:8])
                if acknowledgement_check[0] == DATA_PACKET_IDENTIFIER:
                    lock.acquire()
                    del send_buffer[sequence_number_received-1]
                    lock.release()

        except ConnectionResetError:
            print("Error")
            self.socket_client.close()

def carry_around_add(x, y):
    return ((x+y) & 0xffff) + ((x + y) >> 16)

def checksum_computation(message):
    add = 0
    for i in range(0, len(message) - len(message) % 2, 2):
        message = str(message)
        w = ord(message[i]) + (ord(message[i + 1]) << 8)
        add = carry_around_add(add, w)
    return ~add & 0xffff

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    file = sys.argv[3]
    N = int(sys.argv[4])
    MSS = int(sys.argv[5])
    start = time.time()
    global data_to_send
    global total_packets
    global ack_number
    new_N = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    
    new_MSS = [100,200,300,400,500,600,700,800,900,1000]
    for MSS_val in new_MSS:
    # for N_val in new_N:
        for i in range(5):
            print("----------------------------------------")    
            print("MSS = %s, Try = %s" %(MSS_val, i))                    
            print("----------------------------------------")
            ack_number = 0
            Client_IP = ''
            Client_Port = 4443
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_client.bind((Client_IP,Client_Port))
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
                data_sent = file_content.encode('ISO-8859-1','ignore')
                data_packet = struct.pack('=h',DATA_PACKET_IDENTIFIER)
                max_seq = struct.pack('=L',seq)
                packet = seq_number + checksum + data_packet + max_seq + data_sent
                data_to_send.append(packet)
                data = FILE.read(MSS)
                sequence_number += 1
            total_packets = len(data_to_send)
            ACKs = Acknowledgment(socket_client)


            # Task 1
            
            transmitted_data = Sender(host, port, file, N_val, MSS, socket_client)
            # transmitted_data = Sender(host, port, file, N, MSS, socket_client)
            transmitted_data.join()
            ACKs.join()
            end = time.time()
            server = (host,port)
            socket_client.close()
            print('Host:\t'+str(host))
            print('Port:\t'+str(port))
            print('Window Size:\t'+ str(N))
            print('Maximum Segment Size:\t'+str(MSS))
            print('End Time\t'+str(end))
            print('Total Time\t'+str(end-start))
            FILE.close() 

if __name__ == '__main__':
    main()