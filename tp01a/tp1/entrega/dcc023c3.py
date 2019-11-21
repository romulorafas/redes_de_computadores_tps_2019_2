import socket
from socket import AF_INET, SOCK_DGRAM
import struct
import sys, getopt
import base64
from itertools import zip_longest
import binascii

# REFERENCES:
# https://www.rapidtables.com/convert/number/ascii-hex-bin-dec-converter.html
# https://www.mkyong.com/python/python-3-convert-string-to-bytes/
# https://stackoverflow.com/questions/3949726/calculate-ip-checksum-in-python

sync = 3703579586
flagACK = 128
flag = 0
class Frame:
	sync = None
	length = None
	chksum = None
	ID = None
	flags = None
	data = None

	def __init__(self, sync, length, chksum, ID, flags, data, dataOrig = None):
		self.sync = sync
		self.length = length
		self.chksum = chksum
		self.ID = ID
		self.flags = flags
		self.data = data
		self.dataOrig = dataOrig

	# Retorna o frame como string
	def to_str(self):
		msg = padhexa(hex(self.sync), 8)[2:]
		msg += padhexa(hex(self.sync), 8)[2:]
		msg += padhexa(hex(self.length), 4)[2:]
		msg += padhexa(hex(self.chksum), 4)[2:]
		msg += padhexa(hex(int(self.ID)), 2)[2:]
		msg += padhexa(hex(self.flags), 2)[2:]

		if self.dataOrig:
			msg += str(bytes(self.dataOrig))[2:-1]
		elif self.data != '':
			msg += str(bytes(self.data))[2:-1]

		return msg

	def calc_chksum(self):
		self.chksum = 0
		lista = splitTwoByTwo(self.to_str())
		data = map(lambda x: int(x,16), lista)
		data = struct.pack("%dB" % len(lista), *data)
		self.chksum = checksum(data)

		return self.chksum

def main(argv):
	opts = None
	args = None
	PORT = None
	IP = None
	OUTPUT = None
	INPUT = None
	try:
		opts, args = getopt.getopt(argv, "s:c:")
	except getopt.GetoptError:
		print("dcc023c2.py -s <PORT> <INPUT> <OUTPUT>")
		print("dcc023c2.py -c <IP>:<PORT> <INPUT> <OUTPUT>")
	for opt, arg in opts:
		if opt == '-s':
			PORT = arg
		elif opt == '-c':
			IP, PORT = arg.split(':')

		INPUT = args[0]
		OUTPUT = args[1]
		if IP:
			startClient(IP, PORT, INPUT, OUTPUT)
		else:
			startServer(PORT, INPUT, OUTPUT)

def decode16(c):
	return base64.b16decode(c)

def encode16(c):
	return base64.b16encode(c)

# decodifica dados recebidos no frame
def decodeMessage(msg):
	msg = bytes(msg)

	decoded = bytearray(b'')
	bs = splitTwoByTwo(str(msg.upper())[2:-1])
	for byte in bs:
		decoded.extend(decode16(byte))

	return decoded, msg

# codifica dados a serem enviados no frame
def encodeMessage(msg):
	encoded = bytearray(b'')
	for c in msg:
		encoded.extend(encode16(c))
	return bytes(encoded)


def carry_around_add(a, b):
    c = a + b
    return(c &0xffff)+(c >>16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg)-1, 2):
        w =(msg[i]<<8)+((msg[i+1]))
        s = carry_around_add(s, w)
    return~s &0xffff

def splitTwoByTwo(val):
	args = [iter(val)] * 2

	return [''.join(k) for k in zip_longest(*args)]

def padhexa(s,qtd):
    return '0x' + s[2:].zfill(qtd)

# le arquivo e o encapsula nos frames
def createFrames(input):
	frame_list = []
	new_frame = True
	ID = 1
	data = bytearray(b'')
	with open(input, "rb+") as f:
		while True:
			if new_frame:
				data = bytearray(b'')
				ID = not ID
				new_frame = False

			c = f.read(1)
			data.extend(encode16(c))
			if len(data) == 40000:
				frame = Frame(sync, int(len(data)/2), 0, ID, flag, data)
				frame.calc_chksum()
				frame_list.append(frame)
				new_frame = True
			if not c:
				break
	if not new_frame:
		frame = Frame(sync, int(len(data)/2), 0, ID, flag, data)
		frame.calc_chksum()
		frame_list.append(frame)



	return frame_list

def receive_frame(con):
	frame = Frame(0, 0, 0, 0, 0, '', None)
	teste1 = con.recv(8)
	print("RECEBE O FRAME")
	sync1 =  int(teste1.decode(), 16)
	#print("Sync1", sync1, teste1)
	teste2 = con.recv(8)
	sync2 =  int(teste2.decode(), 16)
	#print("sync2", sync2, teste2)
	if sync == sync1 and sync2 == sync2:
		print("CABECALHO VALIDO")
		length =  (int(con.recv(4).decode(), 16))
		#print("len", length)
		chksum =  int(con.recv(4).decode(), 16)
		#print("chk", chksum)
		ID =  int(con.recv(2).decode(), 16)
		#print("id", ID)
		flags =  int(con.recv(2).decode(), 16)
		#print("flags", flags)
		dados, dadoOrig = rec_data(con, length)
		#print("dados", dados, dadosOrig)
		frame = Frame(sync, length, chksum, ID, flags, dados, dadoOrig)
		#print(frame.to_str())
	return frame

def startClient(IP, PORT, INPUT, OUTPUT):
	print ("Client mode")
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # criando socket
	tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 15)
	tcp.settimeout(1) # timeout em segundos
	s = struct.Struct('>I')
	writeFile(OUTPUT)
	#criando os frames
	frames = createFrames(INPUT)
	dest = (str(IP), int(PORT))
	tcp.connect(dest) # Conectando

	print("	--- 	ENVIA FRAME INICIAL	---")
	count = 0
	oldID = 1
	sendFrame(tcp, frames[count])
	enviado = False
	start_conversation(OUTPUT, tcp, frames, count, oldID)
	socket.close()

def start_conversation(OUTPUT, tcp, frames, count, oldID):
	frames_arquivo = []
	tcp.settimeout(1) # timeout em segundos
	loop = True
	while loop:
			# envia seus proprios quadros
			if count < len(frames):
				print("	--- 	ENVIA FRAME	---")
				sendFrame(tcp, frames[count])

			try:
				frame = receive_frame(tcp)
				#print("FRAME RECEBIDO: ", frame.to_str())
				if frame.flags == flagACK:
					chksum = frame.chksum
					result_check = frame.calc_chksum()
					# se receber o ack corretamente, envia o proximo frame
					if result_check == chksum and frame.length == 0 and frame.flags == flagACK and frame.ID == frames[count].ID :
						print("RECEBEU ACK DO FRAME ", count)
						count+=1

				else:
					chksum = frame.chksum
					result_check = frame.calc_chksum()
					print ("Chksum antigo: ", chksum)
					print ("Chksum novo: ", result_check)
					if result_check == chksum and frame.ID != oldID:
						writeFile(OUTPUT, frame)
						oldID = frame.ID
						frames_arquivo.append(frame)
						frame_ack = Frame(sync, 0, 0, frame.ID, flagACK, '')
						frame_ack.calc_chksum()
						# Enviar ack
						print("	--- 	ENVIA ACK	---")
						sendFrame(tcp, frame_ack)
			except socket.timeout as e:
				print ("Timeout")

	tcp.close()

def rec_data(con, length):
	print("----------ENTROU REC DATA--------------")
	print("len", length)
	passo = 400
	dado =  bytearray(b'')
	resto = length * 2
	while resto != 0:
		if resto <= passo:
			dado.extend(con.recv(resto))
			resto = 0
			break
		else:
			dado.extend(con.recv(passo))
			resto -= passo
	if dado is None or dado == '':
		return decodeMessage('')
	else:
		return decodeMessage(dado)

def sendFrame(tcp, frame):
	# print("frame sendo enviado", frame.to_str())
	# print("sync 1", frame.sync, padhexa(hex(frame.sync), 8)[2:].encode())
	# print("sync 2", frame.sync, padhexa(hex(frame.sync), 8)[2:].encode())
	# print("len", frame.length, padhexa(hex(frame.length), 4)[2:].encode())
	# print("chk", padhexa(hex(frame.chksum), 4)[2:].encode())
	# print("id", padhexa(hex(int(frame.ID)), 2)[2:].encode())
	# print("flag", padhexa(hex(frame.flags), 2)[2:].encode())
	tcp.send(padhexa(hex(frame.sync), 8)[2:].encode())
	tcp.send(padhexa(hex(frame.sync), 8)[2:].encode())
	tcp.send(padhexa(hex(frame.length), 4)[2:].encode())
	tcp.send(padhexa(hex(frame.chksum), 4)[2:].encode())
	tcp.send(padhexa(hex(int(frame.ID)), 2)[2:].encode())
	tcp.send(padhexa(hex(frame.flags), 2)[2:].encode())
	if frame.data != '':
		str_data = str(bytes(frame.data)).lower()
		tcp.send(bytes(str_data.encode()[2:-1]))

	else:
		# print("data",''.encode())
		tcp.send(''.encode())

def startServer(PORT, INPUT, OUTPUT):
	print ("Server mode")
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 15)
	writeFile(OUTPUT)
	frames = createFrames(INPUT)
	orig = ('', int(PORT))
	oldID = 1
	tcp.bind(orig)
	tcp.listen(5)
	loop = True
	con, client = tcp.accept() # aceitando a conexao
	while loop:
		try:
			frame = receive_frame(con)
			chksum = frame.chksum
			result_check = frame.calc_chksum()
			if result_check == chksum and frame.ID != oldID:
				writeFile(OUTPUT, frame)
				oldID = frame.ID
				frame_ack = Frame(sync, 0, 0, frame.ID, flagACK, '')
				frame_ack.calc_chksum()
				# Enviar ack
				print("	--- 	ENVIA PRIMEIRO ACK	---")
				sendFrame(con, frame_ack)
			print("	--- 	INICIA CONVERSA	---")
			start_conversation(OUTPUT, con, frames, 0, oldID)
			loop = False
		except Exception as e:
			print("Unhandled exception", e)
			loop = False
	tcp.close()

def writeFile(output, frame = None):
	if frame:
		print ("Gravando no arquivo")
		file = open(output,"ab+")
		# print(bytes(frame.data))
		file.write(bytes(frame.data))
	else:
		print ("Limpeza inicial do arquivo")
		file = open(output,"wb+")
	file.close()

if __name__ == "__main__":
	main(sys.argv[1:])
