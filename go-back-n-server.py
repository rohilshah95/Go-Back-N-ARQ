import socket
import sys
import threading
import pickle
import struct
import random

data_packet_acknowledgment = 43690
null_string = 0

def receive_and_process_input(file_name, data, expected_sequence, data_packet_acknowledgment, soc_receiver, checksum, address):
    with open(file_name, 'ab') as file:
        file.write(str.encode(data))
        seq_number = struct.pack('=I', expected_sequence)
        null = struct.pack('=H', null_string)
        acknowledgment_sent = struct.pack('=H',data_packet_acknowledgment)
        acknowledgment = seq_number + null + acknowledgment_sent
        soc_receiver.sendto(acknowledgment, address)

def message_from_sender(message):
    seq_num = message[0:4]
    seq_num = struct.unpack('=L', seq_num)
    checksum = message[4:6]
    checksum = struct.unpack('=H', checksum)
    data_packet_identifier = message[6:8]
    data_packet_identifier = struct.unpack('=h', data_packet_identifier)
    max_seq = message[8:12]
    max_seq = struct.unpack('=L', max_seq)
    data = (message[12:])
    actual_message = data.decode('UTF-8','ignore')
    return seq_num, checksum, data_packet_identifier, max_seq, actual_message

def server_receiver():
    port = int(sys.argv[1])
    file_name = sys.argv[2]
    probability = float(sys.argv[3])
    client_port = 4443

    print("Server's port - " + str(port))
    print("filename - " + file_name)
    print("probability - " + str(probability))

    expected_sequence = 1
    soc_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_address = socket.gethostname()
    print(host_address)
    addr = (host_address, client_port)
    soc_receiver.bind((host_address, port))

    while True:
        message, address = soc_receiver.recvfrom(2048)
        seq_num, checksum, data_identifier, max_seq, data = message_from_sender(message)
        if(random.random()<probability):
            print('Packet loss, sequence number = '+ str(seq_num[0]))
        else:
            # print("Expecting:%s, got  %s" %(expected_sequence, seq_num[0]))
            # if expected_sequence > seq_num[0]:
            #     expected_sequence = seq_num[0]
            # if expected_sequence < seq_num[0]:
            #     expected_sequence = seq_num[0]
            if expected_sequence == seq_num[0]:
                if checksum[0] == checksum_computation(data):
                    receive_and_process_input(file_name, data, expected_sequence, data_packet_acknowledgment, soc_receiver, checksum, address)
                    expected_sequence += 1   
        # if seq_num[0] == max_seq[0]-1:
        #     print("Server Reset")
        #     expected_sequence=1

def carry_around_add(x, y):
    return ((x + y) & 0xffff) + ((x + y) >> 16)

def checksum_computation(message):
    add = 0
    for i in range(0, len(message) - len(message) % 2, 2):
        message = str(message)
        w = ord(message[i]) + (ord(message[i + 1]) << 8)
        add = carry_around_add(add, w)
    return ~add & 0xffff

if __name__ == '__main__':
    server_receiver()