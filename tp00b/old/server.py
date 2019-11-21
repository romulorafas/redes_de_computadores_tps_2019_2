#!/usr/bin/env python3
import sys
import socket
import struct
import threading

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket.RCVTIMEO = 15000  # timeout: 15 sec
host = ''


def main(argv):
    port = int(argv[0])
    start_server(port)


def listen_client(con,cliente,port):

    msg = con.recv(4)
    s = struct.Struct('4b')
    word_size = s.unpack(msg)[0]
    # print ('TAMANHO PALAVRA: ', str(word_size))

    # Recebe string
    string_word = ''
    while len(string_word) < word_size:
        msg = con.recv(4)
        s = struct.Struct('4s')
        word = s.unpack(msg)[0]
        word = word.decode('ascii')
        string_word = string_word + word

    # Recebe x
    msg = con.recv(4)
    s = struct.Struct('4b')
    number = s.unpack(msg)[0]

    # print ('PALAVRA: ',string_word)
    new_word = decript_cifra_de_cesar(string_word, number)
    s = struct.Struct(str(word_size) +'s')
    msg = s.pack(new_word.encode('ascii'))
    print (new_word)
    sys.stdout.flush()
    con.send(msg)
    con.close()


# Descriptografa palavra
def decript_cifra_de_cesar(word,number):

    new_word = ''
    alfabeto = 'abcdefghijklmnopqrstuvwxyz'

    for caracter in word:
        i = alfabeto.find(caracter)
        index = i - number
        while(index < 0):
            if index < 0:
                index = index + len(alfabeto)
        new_word = new_word + alfabeto[index]

    return new_word

def start_server(port):

     orig = (host,port)
     tcp.bind(orig)
     tcp.listen(1)
     while True:
         con, cliente = tcp.accept()
         t = threading.Thread(target = listen_client, args = [con,cliente,port])
         t.start()

if __name__ == "__main__":
   main(sys.argv[1:])
