import socket
from socket import AF_INET, SOCK_DGRAM
import sys, getopt
import subprocess
import json
from pprint import pprint
from collections import namedtuple
import threading
from threading import Timer
import time

Routes = []
RouteRow = namedtuple('RouteRow', 'destination nextHop cost TTL')
count_route_rows = 0

def main(argv):
	opts = None
	args = None
	ADDR = None
	PERIOD = None
	STARTUP = None
	PORT = 55151

	# teste = RouteRow('A','C',2)
	# print (teste)
	routing_table = list()
	try:
		opts,args=getopt.getopt(argv,'a:u:s:',[ 'addr=', 'update-period=', 'startup-commands=' ])
	except getopt.GetoptError:
		print("router.py <ADDR> <PERIOD> [STARTUP]")

	# print (opts)
	for opt, arg in opts:
		if opt  in ('-a', '--addr'):
			ADDR = arg
		elif opt in ('-u', '--update-period'):
			PERIOD = arg
		elif opt in ('-s', '--startup-commands'):
			STARTUP = arg

	if STARTUP:
		read_file(STARTUP, routing_table)

	print(ADDR, PERIOD, STARTUP)
	comando = None

	start_listening(ADDR, 55151)

	t=threading.Thread(target=listen_to_cdm, args=())
	t.start()

	update_routes()

def listen_to_cdm():
	while comando is not 'quit':
		comando = input('')
		print (comando)
		comando = comando.replace('\n', '')
		comando = comando.split(" ")
		if comando[0] == 'add' and len(comando) == 3:
			add_ve(comando[1], comando[2], routing_table)
			print ('Enlace adicionado')
		elif comando[0] == 'del' and len(comando) == 2:
			del_ve(comando[1], routing_table)
			print ('Enlace removido')
		elif comando[0] == 'trace' and len(comando) == 2:
			send_trace(comando[1], ADDR)
			print ('Trace enviado')

def send_trace(ADDR, IP):
	json_msg = encode_message("trace", ADDR, IP, "teste_hops")
	send_message(IP, 55151, json_msg)
	print (IP)

# receives string 'add' or 'del'. Pelo que eu entendi a gente só vai usar isso pra inicializar os roteadores mesmo. Talvez nem precisasse estar no programa.
def loopback(operation):
	 subprocess.call(['./tests/lo-adresses.sh',operation])

def add_ve(ip, weight, routing_table):
	route_row = RouteRow (ip,ip,weight, 0)
	routing_table.append(route_row)
	return routing_table

def del_ve(ip, routing_table):
	return routing_table.pop(ip)

def merge_route(new_route):

def read_file(file_name, routing_table):
    with open(file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            command = line.replace('\n', '')
            commands = command.split(" ")
            print(commands)
            if commands[0] != 'add':
                print("Invalid command was read in startup file:", commands[0])
            if len(commands) != 3:
                print("Invalid format was read in startup file:", commands)
            else:
                add_ve(commands[1], commands[2], routing_table)

def encode_message(type, source, destination, last_info):
	if type is 'data':
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'payload': last_info})
	elif type is 'update': # tem que arrumar o distances. Eh outro json.
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'distances': last_info})
	elif type is 'trace':
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'hops': last_info})

def decode_message(message):
	data = json.loads(message)
	# Prints if it's data type message
	if data["type"] is 'data':
		pprint(data)
	return data


def send_message(HOST, PORT, message):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	dest = (HOST, int(PORT))
	udp.sendto(message, dest)
	udp.close()

def start_listening(IP, PORT):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	orig = (IP, int(PORT))
	udp.bind(orig)
	while True:
		message, client = udp.recvfrom(1024)
		print ("MENSAGEM RECEBIDA")
	udp.close()

def handler(udp):
	message, client = udp.recvfrom(1024)
	print ("MENSAGEM RECEBIDA")
	udp.close()

def update_routes():
    threading.Timer(PERIOD, update_routes).start()
    for route in routes:
        if time.time() > route.ttl + 4*PERIOD :
            routes.remove(route)

if __name__ == "__main__":
	main(sys.argv[1:])
