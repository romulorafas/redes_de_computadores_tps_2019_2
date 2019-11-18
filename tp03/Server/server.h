#ifndef SERVER_H
#define SERVER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "tp_socket.h"
#define MaxTentativas_msg 30
#define MAX 80
#define TAM_MAX_JANELA 5
struct sockaddr_in si_me;
struct sockaddr_in si_other;

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
void transferencia(int sockfd, int tam_buffer, char nome_arquivo[MAX]);

#endif // SERVER_H
