/*
 * main.c
 * server
 */

#include "server.h"
//porto_servidor tam_buffer
int main(int argc, char *argv[]) {

	if (argc < 2) {
		printf("Entrar com nome do executavel, porta e  tamanho do buffer\n");
		return 0;
	}
	inicializa(atoi(argv[1]), atoi(argv[2]));

	return 0;
}
