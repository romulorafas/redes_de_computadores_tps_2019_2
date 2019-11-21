#!/usr/bin/env python3
import sys
import socket
import struct

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket.RCVTIMEO = 15000  # timeout: 15 sec

def main(argv):
    host = argv[0]
    port = int(argv[1])
    word = argv[2]
    x = int(argv[3])

    # print (host)
    # print (port)
    dest = (host, port)
    tcp.connect(dest)
    new_word = cript_cifra_de_cesar(word, x)

    # Envia tamanho da string
    s = struct.Struct('I')
    msg = s.pack(len(new_word))
    # print ('TAMANHO PALAVRA: ', str(len(new_word)))
    tcp.send (msg)


    s = struct.Struct(str(len(new_word)) +'s')
    msg = s.pack(new_word.encode('ascii'))
    tcp.send (msg)

    # Envia X
    s = struct.Struct('i')
    msg = s.pack(x)
    tcp.send (msg)

    # Receve string decriptografada
    new_msg = tcp.recv(len(new_word))
    new_msg = new_msg.decode('ascii')
    print (new_msg)
    sys.stdout.flush()
    tcp.close()

# Criptografa palavra
def cript_cifra_de_cesar(word,number):
    new_word = ''
    alfabeto = 'abcdefghijklmnopqrstuvwxyz'
    # print ('word: ',word)
    for caracter in word:
        # print ('caracter: ',caracter)
        i = alfabeto.find(caracter)
        # print ('i: ',i)
        index = i + number
        # print ('index: ',index)
        while(index >= len(alfabeto)):
            if index >= len(alfabeto):
                index = index - len(alfabeto)
        # print ('index: ',str(index))
        new_word = new_word + alfabeto[index]
        # print ('New word: ',new_word)
    return new_word


if __name__ == "__main__":
   main(sys.argv[1:])
