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
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

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
		global ROUTER_ADDR
		ROUTER_ADDR = ADDR
		if STARTUP:
			read_file(STARTUP, ADDR)

		orig = (ADDR, int(PORT))
		udp.bind(orig)
		t1 = threading.Thread(target=start_listening, args=(ADDR, PORT))
		t1.setDaemon(True)
		t1.start()

		t2=threading.Thread(target=listen_to_cdm, args = (ADDR,))
		t2.setDaemon(True)
		t2.start()

		update_routes_periodically(PERIOD, ADDR, routing_table)
		remove_old_routes(PERIOD, ADDR, routing_table)

def listen_to_cdm(ADDR):
	comando = None
	# try:
	while True:
		comando = input('')
		comando = comando.replace('\n', '')
		comando = comando.split(" ")
		if comando[0] == 'add' and len(comando) == 3:
			add_ve(comando[1], comando[2], routing_table, ADDR)
		elif comando[0] == 'del' and len(comando) == 2:
			del_ve(comando[1], routing_table)
			t1 = threading.Thread(target=update, args=(ADDR, routing_table))
			t1.setDaemon(True)
			t1.start()
		elif comando[0] == 'trace' and len(comando) == 2:
			routers = list()
			routers.append(ADDR)
			send_trace_or_data("trace", ADDR, comando[1].replace("'", ""), routers)
		elif comando[0] == 'print': # COMANDO PARA DEBUG: PRINTA TABELA DE ROTEAMENTO
			print_table (routing_table)
		elif comando[0] == 'cls': # COMANDO PARA DEBUG: LIMPA O OUTPUT
			os.system('clear')
		elif comando[0] == 'quit':
			os._exit(1)
	# except Exception as e:
	# 	os._exit(1)

def send_trace_or_data(type, ADDR, destination, routers):
	json_msg = encode_message(type, ADDR, destination, routers)
	count_chances = 0
	if ADDR != destination:
		ip = get_next_hop(destination)
	else:
		ip = ADDR
	if ip is not None:
		send_message(ADDR, ip, PORT, json_msg)
	else:
		print ("Trying to find route to reach %s..." % (destination))
		messagem_sent = False
		while count_chances <= 2:
			time.sleep(5)
			ip = get_next_hop(destination)
			count_chances += 1
			if ip is not None:
				send_message(ADDR, ip, PORT, json_msg)
				messagem_sent = True
				break
		if not messagem_sent:
			print ("There is no route available from " + ADDR + " to " + destination)
			json_msg = encode_message('error', ADDR, destination, "There is no route available from " + ADDR + " to " + destination)
			send_trace_or_data('error', ROUTER_ADDR, ADDR, json_msg)

def add_ve(ip, weight, routing_table, addedBy):
	route_row = RouteRow (ip, ip, int(weight), time.time(), addedBy)
	routing_table.append(route_row)
	return routing_table

def del_ve(ip, routing_table):
	for route in routing_table:
		if ip == route.nextHop:
			routing_table.remove(route)
	return routing_table

def get_next_hop(destination):
	tied_routes = get_tied_routes(routing_table, destination)
	if tied_routes is None or tied_routes == []:
		for route in routing_table:
			if str(route.destination).replace("'", "") == destination:
				return route.nextHop
		return None
	else:
		route = load_balance(tied_routes)
		return route.nextHop

def get_cost(destination):
	for route in routing_table:
		if route.destination == destination:
			return route.cost
	return 0

def get_neighbors(routing_table):
	neighbors = list()
	for router in routing_table:
		if router not in neighbors:
			neighbors.append(router.nextHop.replace("'",""))

	neighbors = list(set(neighbors))
	return neighbors

# Retorna tabela com split horizon aplicado nesta
def get_splithorizon_routing_table(routing_table, router):
	new_routing_table  = list()
	for r in routing_table:
		if r.sentBy != router and r.destination != router:
			new_routing_table.append(r)

	return new_routing_table

# Retorna tabela de roteamento como um dicionario
def get_routingtable_to_dict(ADDR, routing_table):
	routing_dict = dict()
	routing_dict[ADDR] = 0
	for route in routing_table:
		routing_dict[route.destination] = route.cost

	return routing_dict

# Verifica se roteador existe na tabela de roteamento como vizinho
def is_neighbor(routing_table, router):
	neighbors = get_neighbors(routing_table)
	for neighbor in neighbors:
		if neighbor.replace("'","") == router:
			return True

	return False

# Identifica e retorna as rotas de mesmo peso para um mesmo destino
def get_tied_routes(routing_table, destination):
	destination_routes = list(route for route in routing_table if (route.destination == destination))
	tied_routes = list(route for route in destination_routes if(route.cost == aux_route.cost and route.nextHop != aux_route.nextHop for aux_route in destination_routes))

	if tied_routes is not None:
		return tied_routes
	else:
		return None

# Funcao para facilitar DEBUG. Imprime a tabela de roteamento em forma de tabela
def print_table(routing_table):
	print ("{:<10} {:<10} {:<5} {:<15} {:<10}".format('destination','nextHop','cost', 'ttl', 'sentBy'))
	for route in routing_table:
		d,n,c,t,s = route
		print ("{:<10} {:<10} {:<5} {:<15} {:<10}".format(d, n, c, t, s))

# Verifica se uma rota ja existe na tabela de roteamento
def has_route(routing_table, new_route, neighbor, cost_hop):
	for route in routing_table:
		if ((route.destination == new_route.destination) and (route.nextHop == neighbor)
			and (route.cost == (new_route.cost + cost_hop))): # and (route.sentBy == neighbor)):
			routing_table.remove(route)
			new_route = (RouteRow(route.destination, route.nextHop , route.cost,
					 time.time(), route.sentBy))
			routing_table.append(new_route)
			return True

	return False

# Realiza o merge entre as rotas do roteador e as do vizinho
# Possiveis situacoes:
# - Rota nao existe na tabela de roteamento
# 	Nesse caso, rota é adicionada na tabela
# - Ja existe uma rota para o destino, porem de custo MAIOR
# 	Nesse caso, a rota de melhor custo deve permanecer
# - Ja existe uma rota para o destino, porem de custo MENOR
# 	Nesse caso, a new_route eh descartada
# - Ja existe uma rota para o destino, de custo IGUAL
# 	Nesse caso, ambas as rotas devem ser mantidas na tabela
def merge_route(new_route, routing_table, cost_hop, ADDR, neighbor):
	index = -1
	old_route = None
	final_cost = 0
	for route in routing_table:
		final_cost = cost_hop
		if route.destination == new_route.destination:
			if final_cost is None:
				print ("new_route.cost:", new_route.cost)
				print ("final_cost:", final_cost)
				print_table(routing_table)
			elif ((new_route.nextHop != route.nextHop)
				and ((new_route.cost + final_cost) < route.cost)): #melhor rota encontrada
				index = routing_table.index(route)
				old_route = route
				# remove rota a ser atualizada
				routing_table.remove(route)
				break
			elif ((new_route.nextHop != route.nextHop)
				and ((new_route.cost + final_cost) == route.cost)): #rota alternativa encontrada
				index = -1
			elif ((new_route.nextHop == route.nextHop)
				and ((new_route.cost + final_cost) == route.cost)): #rota alternativa encontrada
				index = -1
			else: # rota sera descartada
				index = 0

	if index == -1: # nova rota
		new_cost = new_route.cost + final_cost
		new_route = (RouteRow(new_route.destination, neighbor, new_cost,
					time.time(), neighbor))
		routing_table.append(new_route)
	elif index > 0: # rota sera atualizada
		new_cost = new_route.cost + final_cost
		new_route = (RouteRow(new_route.destination, neighbor, new_cost,
					 time.time(), neighbor))
		routing_table.append(new_route)


def read_file(file_name, ADDR):
    with open(file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            command = line.replace('\n', '')
            commands = command.split(" ")
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
		return json.dumps({'type': type, 'source': source, 'destination': destination, 'payload': last_info})


def decode_message(IP, message):
	# Verifica versao do python para tratamento da mensagem
	python_version  = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
	if python_version == '3.5':
		message = message.decode('utf-8')
	data = json.loads(message)
	# Printa se é o destino da mensagem de dado ou se é uma mensagem de erro
	if (data["type"] == 'data' or data["type"] == 'error') and data["destination"] == IP:
		payload = json.loads(data["payload"])
		print ("message from %s:" % (data["source"]) )
		print(payload)
	return data


def send_message(ADDR, HOST, PORT, message):
	dest = (str(HOST), int(PORT))
	udp.sendto(message.encode('utf-8'), dest)

def start_listening(IP, PORT):
	while True:
		message, client = udp.recvfrom(1024)
		# verifica se roteador que envia a mensagem ainda é vizinho
		json_msg = decode_message(IP, message)
		if is_neighbor(routing_table, str(client[0]).replace("'","")) is True:
			if json_msg["type"] == 'update':
				new_routing_table = json_msg["distances"]
				for new_route in new_routing_table:
					if new_route not in IP: #split horizon
						new_route = RouteRow(new_route, json_msg["source"], new_routing_table[new_route], time.time(), json_msg["source"])
						# Verifica se rota ja existe na tabela, fazendo merge apenas de rotas novas/atualizadas
						if (has_route(routing_table, new_route, json_msg["source"], get_cost(json_msg["source"])) is False):
							merge_route(new_route, routing_table, get_cost(json_msg["source"]), IP, json_msg["source"])

			elif json_msg["type"] == 'trace':
				routers = json_msg["hops"]
				routers.append(IP)
				if json_msg["destination"] == IP: # trace chegou ao destino!
					payload = json.dumps(json_msg)
					send_trace_or_data("data", json_msg["destination"] , json_msg["source"], payload)
				else: # trace segue seu caminho
					send_trace_or_data("trace", json_msg["source"], json_msg["destination"], routers)
			elif json_msg["type"] == 'data':
				if json_msg["destination"] != IP: # data segue seu caminho
					send_trace_or_data("data", json_msg["source"] , json_msg["destination"], json_msg["payload"])
	udp.close()

def remove_old_routes(PERIOD, ADDR, routing_table):
	threading.Timer(int(PERIOD), remove_old_routes, args = (PERIOD, ADDR, routing_table)).start()
	is_there_change = False
	for route in routing_table:
		if time.time() > (route.ttl + 4*float(PERIOD)) and route.sentBy != ADDR:
			routing_table.remove(route)
			is_there_change = True
	if is_there_change:
		t1 = threading.Thread(target=update, args=(ADDR, routing_table))
		t1.setDaemon(True)
		t1.start()

def update_routes_periodically(PERIOD, ADDR, routing_table):
	update(ADDR, routing_table)
	threading.Timer(int(PERIOD), update_routes_periodically, args = (PERIOD, ADDR, routing_table)).start()

def update(ADDR, routing_table):
	routers = get_neighbors(routing_table)
	for router in routers:
		new_routing_table = get_splithorizon_routing_table(routing_table, router)
		json_msg = encode_message("update", ADDR, router, get_routingtable_to_dict(ADDR, new_routing_table))
		router = router.replace("'","")
		send_message(ADDR, router, PORT, json_msg)

# receives list with tied routes like ['1.1.1.1', '1.1.1.2', '1.1.1.3'] and returns the chosen one
def load_balance(tied_routes):
    a = 1
    b = len(tied_routes)+1
    chosen = ra.uniform(a,b)
    chosen = int(chosen)
    return tied_routes[chosen-1]

if __name__ == "__main__":
	main(sys.argv[1:])
