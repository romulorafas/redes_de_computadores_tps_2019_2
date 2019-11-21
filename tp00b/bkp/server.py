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
    listen_client(port)



def listen_client(port):

    # Recebe tamanho da string

    orig = (host,port)
    tcp.bind(orig)
    tcp.listen(1)
    # print ('created')
    con, cliente = tcp.accept()


    msg = con.recv(4)
    s = struct.Struct('4b')
    word_size = s.unpack(msg)[0]
    # print ('WORD SIZE: ', word_size)

    # Recebe string
    msg = con.recv(word_size)
    s = struct.Struct('4s')
    word = s.unpack(msg)[0]
    # print (word.decode('ascii'))

    # Recebe x
    msg = con.recv(4)
    s = struct.Struct('4b')
    number = s.unpack(msg)[0]
    # print ('VALOR DE X: ',number)


    word = word.decode('ascii')
    new_word = decript_cifra_de_cesar(word, number)
    s = struct.Struct('4s')
    msg = s.pack(new_word.encode('ascii'))
    print (new_word)
    con.send(msg)
    con.close()


# Descriptografa palavra
def decript_cifra_de_cesar(word,number):
    new_word = ''
    # print ('WORD: ', word)
    for caracter in word:
        i = word.find(caracter)
        index = i - number
        if index < 0:
            index = index + len(word)
        new_word = new_word + str(word[index])
    # print ('New word: ',new_word)
    return new_word

def start_server():

     orig = (host,port)
     tcp.bind(orig)
     tcp.listen(1)
     print ('created')
     while True:
         con, cliente = tcp.accept()
         t = threading.Thread(target = listen_client, args = [con,cliente])
         t.start()


# def start_server():
#
#     orig = (host,port)
#     tcp.bind(orig)
#     tcp.listen(1)
#     print ('created')
#     while True:
#         con, cliente = tcp.accept()
#         t = threading.Thread(target = listen_client)
#         t.start()

if __name__ == "__main__":
   main(sys.argv[1:])
