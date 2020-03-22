#Parametros do Cliente : Porta Local, Endereco de Ip do servidor, porta do servidor
import select
import socket
import struct
import sys
from sys import stdin

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def main(argv):
	HOST = None
	PORT = None
	LOCAL_PORT = None
	# Deve receber os 3 parametros para iniciar conexao
	if len(argv) >= 3:
		LOCAL_PORT = argv[0]
		HOST = argv[1] # Endereco IP do Servidor
		PORT = argv[2] # Porta em que o Servidor esta

		server.bind(('',int(LOCAL_PORT)))
		input = [server,stdin]
		running = 1
		# send_message(HOST, PORT, TEXT)
		while running:
			inputready,outputready,exceptready = select.select(input,[],[],)

			for s in inputready:
				if s == server:
					data = s.recv(500).decode('ascii')
					print(data)
				elif s == stdin:
					# handle standard input
					TEXT = stdin.readline()
					TEXT = TEXT.replace('\n', '')
					send_message(HOST, PORT, TEXT)
				else:
					# handle all other sockets
					print("outros sockets")
					data = s.recv(500).decode('ascii')
					print(data)
					if data:
						s.send(data)
					else:
						s.close()
						input.remove(s)
		server.close()

def send_message(HOST, PORT, message):

	dest = (HOST, int(PORT))
	server.sendto(message.encode('ascii'), dest)

if __name__ == "__main__":
	main(sys.argv[1:])
