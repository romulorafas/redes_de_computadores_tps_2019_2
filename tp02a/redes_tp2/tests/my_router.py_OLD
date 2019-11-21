import socket
from socket import AF_INET, SOCK_DGRAM
import sys, getopt, os
import subprocess
import json
from pprint import pprint
from collections import namedtuple
import threading
from threading import Timer
import time
import random as ra

from sys import exit

routing_table = list()
RouteRow = namedtuple('RouteRow', 'destination nextHop cost ttl sentBy')
count_route_rows = 0
PORT = 55151
PERIOD = None
ROUTER_ADDR = None

def main(argv):
	opts = None
	args = None
	STARTUP = None
	ADDR = None
	PERIOD = None

	try:
		opts,args=getopt.getopt(argv,'a:u:s:',[ 'addr=', 'update-period=', 'startup-commands=' ])
	except getopt.GetoptError:
		print("router.py <ADDR> <PERIOD> [STARTUP]")

	# print(opts, args)
	if opts:
		for opt, arg in opts:
			if opt in ('-a', '--addr'):
				ADDR = arg
			elif opt in ('-u', '--update-period'):
				PERIOD = arg
			elif opt in ('-s', '--startup-commands'):
				STARTUP = arg
	elif len(args) >= 2:
		ADDR = args[0]
		PERIOD = args[1]
		if len(args) == 3:
			STARTUP = args[2]

	if ADDR is None or PERIOD is None:
		print("Error on startup. Use either: ")
		print("router.py <ADDR> <PERIOD> [STARTUP]")
		print("Or:")
		print("router.py --addr <ADDR> --update-period <PERIOD> --startup-commands [STARTUP]")
	else:
		ROUTER_ADDR = ADDR
		if STARTUP:
			read_file(STARTUP, ADDR)

		t1 = threading.Thread(target=start_listening, args=(ADDR, PORT))
		t1.setDaemon(True)
		t1.start()

		t2=threading.Thread(target=listen_to_cdm, args = (ADDR,))
		t2.setDaemon(True)
		t2.start()

		update_routes_periodically(PERIOD, ADDR)
		# remove_old_routes(PERIOD, ADDR)

def listen_to_cdm(ADDR):
	comando = None
	try:
		while True:
			comando = input('')
			comando = comando.replace('\n', '')
			comando = comando.split(" ")
			if comando[0] == 'add' and len(comando) == 3:
				add_ve(comando[1], comando[2], routing_table, ADDR)
				print ('Enlace adicionado')
				print (routing_table)
			elif comando[0] == 'del' and len(comando) == 2:
				del_ve(comando[1], routing_table)
				print ('Enlace removido')
				print (routing_table)
				t1 = threading.Thread(target=update, args=(ADDR))
				t1.setDaemon(True)
				t1.start()
			elif comando[0] == 'trace' and len(comando) == 2:
				print (get_next_hop(comando[1]))
				routers = list ()
				routers.append(ADDR)
				send_trace_or_data("trace", ADDR, comando[1], routers)
				print ('Trace enviado')
			elif comando[0] == 'quit':
				os._exit(1)
	except Exception as e:
		os._exit(1)

def send_trace_or_data(type, ADDR, destination, routers):
	json_msg = encode_message(type, ADDR, destination, routers)
	ip = get_next_hop(destination)
	if ip is not None:
		send_message(ip, PORT, json_msg)
	else:
		# retorna mensagem pro sender falando que n?o tem rota seria aqui?
		json_msg = encode_message('error', ADDR, ROUTER_ADDR, "There is no route available from " + ROUTER_ADDR + "to " + destination)

def add_ve(ip, weight, routing_table, addedBy):
	route_row = RouteRow (ip, ip, int(weight), time.time(), addedBy)
	routing_table.append(route_row)
	return routing_table

def del_ve(ip, routing_table):
    for route in routing_table:
        if ip == route.destination:
            routing_table.remove(route)
    return routing_table

def get_next_hop(destination):
	for i in range (0,len(routing_table)):
		if routing_table[i].destination == destination:
			return routing_table[i].nextHop
	return None

def get_cost(destination):
	for route in routing_table:
		if route.destination == destination:
			return route.cost

def get_neighbors(routing_table):
	neighbors = []
	for router in routing_table:
		if router not in neighbors:
			neighbors.append(router.nextHop)

	return neighbors

def print_table(routing_table):
	print ("{:<10} {:<10} {:<5} {:<15} {:<10}".format('destination','nextHop','cost', 'ttl', 'sentBy'))
	# print ('{:<10}'.format('destination'))
	for route in routing_table:
		d,n,c,t,s = route
		print ("{:<10} {:<10} {:<5} {:<15} {:<10}".format(d, n, c, t, s))

def merge_route(new_route, routing_table, cost_hop, ADDR, neighbor):
	index = -1
	old_route = None
	for route in routing_table:
		# print ("Route:", route)
		# print ("New route:", new_route)
		if route.destination == new_route.destination:
			# print ("new_route.cost + cost_hop:", new_route.cost + cost_hop)
			# print ("route.cost", route.cost)
			if (new_route.cost + cost_hop) < route.cost: #melhor rota encontrada
			    #or (new_route.nextHop == route.nextHop)):
				index = routing_table.index(route)
				old_route = route
				routing_table.remove(route)
				break
			else: # nada de novo
				index = 0

	if index == -1: # nova rota
		new_cost = new_route.cost + cost_hop
		new_route = (RouteRow(new_route.destination, neighbor, new_cost,
					new_route.ttl, neighbor))
		routing_table.append(new_route)
		# print ("Nova rota adicionada")
	elif index > 0:
		new_cost = new_route.cost + cost_hop
		new_route = (RouteRow(new_route.destination, neighbor, new_cost,
					 new_route.ttl, neighbor))
		routing_table.append(new_route)
		# print ("rota atualizada")


def read_file(file_name, ADDR):
    with open(file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            command = line.replace('\n', '')
            commands = command.split(" ")
            # print(commands)
            if commands[0] != 'add':
                print("Invalid command was read in startup file:", commands[0])
            if len(commands) != 3:
                print("Invalid format was read in startup file:", commands)
            else:
                add_ve(commands[1], commands[2], routing_table, ADDR)

def encode_message(type, source, destination, last_info):
	if type is 'data':
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'payload': last_info})
	elif type is 'update':
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'distances': last_info})
	elif type is 'trace':
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'hops': last_info})
	else: # error
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'message': last_info})


def decode_message(IP, message):
	data = json.loads(message)
	# Prints if it's the destination of the data type message or if it's an error message
	if (data["type"] == 'data' or data["type"] == 'error') and data["destination"] == IP:
		payload = json.loads(data["payload"])
		print ("message from %s:" % (data["source"]) )
		print(payload)
	return data


def send_message(HOST, PORT, message):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	dest = (HOST, int(PORT))
	udp.sendto(message.encode('utf-8'), dest)
	# print ("Mensagem enviada")
	udp.close()

def start_listening(IP, PORT):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	orig = (IP, int(PORT))
	udp.bind(orig)
	while True:
		message, client = udp.recvfrom(1024)
		json_msg = decode_message(IP, message)
		if json_msg["type"] == 'update':
			# print ("Update do vizinho %s recebido" % (json_msg["source"]) )
			# new_routing_table = json.loads(json_msg["distances"])
			new_routing_table = json_msg["distances"]
			# print ("ROTA ANTES DO UPDATE")
			# print_table (routing_table)
			for new_route in new_routing_table:
				# print ("rota:", new_route)
				if new_route[0] not in IP and new_route[4] not in IP: #split horizon
					# print ("rota aceita no split horizon")
					new_route = RouteRow(new_route[0], new_route[1], new_route[2], new_route[3], new_route[4])
					merge_route(new_route, routing_table, get_cost(json_msg["source"]), IP, json_msg["source"])
					# print ("Route processed")
				# else:
				# 	print ("rota NAO aceita no split horizon")
			# print ("TABELA DEPOIS DO UPDATE:")
			# print_table (routing_table)
			# print ("------------------------------------------------------------")
		elif json_msg["type"] == 'trace':
			routers = json_msg["hops"]
			routers.append(IP)
			print ("Caminho trace ate agora:", routers)
			if json_msg["destination"] == IP: # trace chegou ao destino!
				payload = json.dumps (json_msg)
				send_trace_or_data("data", json_msg["destination"] , json_msg["source"], payload)
			else: # trace segue seu caminho
				send_trace_or_data("trace", json_msg["source"], json_msg["destination"], routers)
		elif json_msg["type"] == 'data':
			if json_msg["destination"] != IP: # data segue seu caminho
				print ("Data passou por aqui!")
				send_trace_or_data("data", json_msg["source"] , json_msg["destination"], json_msg["payload"])
	udp.close()

def remove_old_routes(PERIOD, ADDR):
	is_there_change = False
	threading.Timer(PERIOD, remove_old_routes, args = [ADDR]).start()
	for route in routing_table:
		if time.time() > (route.ttl + 4*float(PERIOD)):
			print ("Entrou no if")
			routing_table.remove(route)
			is_there_change = True
	if is_there_change:
		t1 = threading.Thread(target=update, args=(ADDR))
		t1.setDaemon(True)
		t1.start()

def update_routes_periodically(PERIOD, ADDR):
	# print ("PERIOD:", PERIOD)
	update(ADDR)
	threading.Timer(int(PERIOD), update_routes_periodically, args = [PERIOD,ADDR]).start()

def update(ADDR):
	# print ("---------Sending updates------------")
	routers = get_neighbors(routing_table)
	for router in routers:
		json_msg = encode_message("update", ADDR, router, routing_table)
		router = router.replace("'","")
		send_message(router, PORT, json_msg)
	# print ("Updates enviados")

# receives list with tied routes like ['1.1.1.1', '1.1.1.2', '1.1.1.3'] and returns the chosen one
def load_balance(tied_routes):
    a = 1
    b = len(tied_routes)+1
    chosen = ra.uniform(a,b)
    chosen = int(chosen)
    return tied_routes[chosen-1]

if __name__ == "__main__":
	main(sys.argv[1:])
