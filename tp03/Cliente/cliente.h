#ifndef CLIENTE_H
#define CLIENTE_H

#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include "tp_socket.h"
#define MAX 80
struct sockaddr_in si_other;
#define Tentativas_s 3
#define SegundosEspera 3

/*-----------------------------------------------------------------------------
 * Prototipo: inicializa(int porta, int tam_buffer)
 * Função: inicializa o cliente
 * Entrada: host - endereco do servidor
 * 			porta - porta de comunicacao
 * 			nome_arquivo - nome do arquivo para transferencia
 * 			tam_buffer - tamanho do buffer
 * Saida: void
 *----------------------------------------------------------------------------*/
void inicializa(char *host, int porta, char nome_arquivo[MAX], int tam_buffer);

/*-----------------------------------------------------------------------------
 * Prototipo: tranferencia(int sockfd)
 * Função: tranferencia do arquivo
 * Entrada: sockfd - informacao do cliente
 * 			host - endereco do servidor
 * 			porta - porta de comunicacao
 * 			nome_arquivo - nome do arquivo para transferencia
 * 			tam_buffer - tamanho do buffer
 * Saida: void
 *----------------------------------------------------------------------------*/
void tranferencia(int sockfd, char *host, int porta, char nome_arquivo[MAX],
		int tam_buffer);

/*-----------------------------------------------------------------------------
 * Prototipo: die(char *s)
 * Função: encerra o programa
 * Entrada: s - nome do erro
 * Saida: void
 *----------------------------------------------------------------------------*/
void die(char *s);

#endif // CLIENTE_H
