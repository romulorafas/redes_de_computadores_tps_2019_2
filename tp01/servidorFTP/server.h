#ifndef SERVER_H
#define SERVER_H

#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#define MAX 80
#define SA struct sockaddr

/*-----------------------------------------------------------------------------
 * Prototipo: inicializa(int porta, int tam_buffer)
 * Função: inicializa o servidor
 * Entrada: porta - porta de comunicacao
 * 			tam_buffer - tamanho do buffe
 * Saida: void
 *----------------------------------------------------------------------------*/
void inicializa(int porta, int tam_buffer);

/*-----------------------------------------------------------------------------
 * Prototipo: tranferencia(int sockfd)
 * Função: tranferencia do arquivo
 * Entrada: sockfd - informacao do cliente
 * 			tam_buffer - tamanho do buffe
 * Saida: void
 *----------------------------------------------------------------------------*/
void transferencia(int sockfd, int tam_buffer);

#endif // SERVER_H
