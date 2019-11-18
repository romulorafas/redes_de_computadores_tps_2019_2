############################# Makefile ##########################
#Variável
CC = gcc
DEPS = cliente.h  
OBJ = main.o cliente.o
EXEC = clienteFTP
%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)
	
$(EXEC):$(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)
	
clean: 
	rm -rf *.o $(EXEC)