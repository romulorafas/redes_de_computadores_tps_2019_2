############################# Makefile ##########################
#Variável
CC = gcc
DEPS = server.h tp_socket.h  
OBJ = main.o server.o tp_socket.o
EXEC = serverFTP
%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)
	
$(EXEC):$(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)
	
clean: 
	rm -rf *.o $(EXEC)