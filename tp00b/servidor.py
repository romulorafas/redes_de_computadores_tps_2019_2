#!/usr/bin/env python3
import sys
import socket
import struct
import threading

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# socket.RCVTIMEO = 15000  # timeout: 15 segundos
tcp.settimeout(15) # timeout: 15 segundos
host = ''


def main(argv):
    port = int(argv[0])
    start_server(port)

def listen_client(con,cliente,port):

    # Recebe tamanho da string
    msg = con.recv(4)
    s = struct.Struct('>i')
    word_size = s.unpack(msg)[0]

    # Recebe string
    s = struct.Struct(str(word_size) + 's')
    msg = con.recv(word_size)
    string_word = s.unpack(msg)[0]
    string_word = string_word.decode('ascii')

    # Recebe x
    msg = con.recv(4)
    s = struct.Struct('>i')
    number = s.unpack(msg)[0]

    new_word = descript_cifra_de_cesar(string_word, number)
    s = struct.Struct(str(word_size) +'s')
    msg = s.pack(new_word.encode('ascii'))
    print (new_word)
    sys.stdout.flush()

    # Envia string descriptografada
    con.send(msg)
    con.close()


# Descriptografa string
def descript_cifra_de_cesar(word,number):

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
