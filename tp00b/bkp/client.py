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
    tcp.send (msg)

    # Envia string
    s = struct.Struct('4s')
    msg = s.pack(new_word.encode('ascii'))
    tcp.send (msg)
    #
    # Envia X
    s = struct.Struct('I')
    msg = s.pack(x)
    tcp.send (msg)
    #
    new_msg = tcp.recv(16)
    new_msg = new_msg.decode('ascii')
    print (new_msg)
    tcp.close()

# Criptografa palavra
def cript_cifra_de_cesar(word,number):
    new_word = ''
    for caracter in word:
        i = word.find(caracter)
        index = i + number
        if index >= len(word):
            index = index - len(word)
        new_word = new_word + word[index]
    # print ('New word: ',new_word)
    return new_word


if __name__ == "__main__":
   main(sys.argv[1:])
