/*
 * main.c
 * cliente
 */
//host_do_servidor porto_servidor nome_arquivo tam_buffer
#include "cliente.h"

int main(int argc, char *argv[]) {

	if (argc < 4) {
		printf(
				"Entrar com nome do executavel host do servidor, porta do servidor, nome do arquivo e  tamanho do buffer\n");
		return 0;
	}
	/*Inicialização dos argumentos*/
	/*host = argv[1];
	 porta = atoi(argv[2]);
	 nome_arquivo =	argv[3];
	 tam_buffer = atoi(argv[4]);*/
	inicializa(argv[1], atoi(argv[2]), argv[3], atoi(argv[4]));

	return 0;
}
