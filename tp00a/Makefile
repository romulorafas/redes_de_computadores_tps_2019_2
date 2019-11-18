all:
	gcc -Wall client.c -o client
	gcc -Wall server.c -o server
	gcc -Wall server-mt.c -lpthread -o server-mt

clean:
	rm -f client server server-mt
