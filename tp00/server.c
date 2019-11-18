#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include "tp_socket.h"
#include <sys/errno.h>
#include <sys/time.h>
#include <signal.h>

void die(char *s)
{
	perror(s);
	exit(1);
}

int main(int argc, char *argv[])
{
	if (argc <= 1)
	{
		printf("Faltando argumentos!");
		exit(1);
	}

	// Estruturas para medições do tempo de execução
	struct timeval begintime, endtime;
	gettimeofday(&begintime, NULL);

	int PORT   = atoi(argv[1]);
	int BUFLEN = atoi(argv[2]);

	struct sockaddr_in si_me, si_other;

	int s, i, slen = sizeof(si_other), recv_len;
	char buf[BUFLEN];
	char ack[BUFLEN];
	char file_buf[BUFLEN];

	s = tp_socket(PORT);

	// Recepção do nome do arquivo que será enviado
	if (tp_recvfrom(s, buf, 1024, (struct sockaddr *)&si_other) == -1) {
		die("recvfrom()");
	}

	/**
	 * Configuração do timeout do socket 
	 */ 
	struct timeval tv;
	tv.tv_sec = 3;
	if (setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0)
	{
		perror("Error");
	}

	FILE *fp;

	fp = fopen(buf, "r");

	if (fp == NULL)
	{
		printf("file does not exist\n");
		exit(1);
	}

	// Cálculo do tamanho do arquivo
	fseek(fp, 0, SEEK_END);
	size_t file_size = ftell(fp);
	fseek(fp, 0, SEEK_SET);

	printf("Tamanho do arquivo: %d\n", file_size);

	int requests = 0;
	char end[10];

	// A cada bloco lido, de tamanho do BUFFER estipulado nos argumentos
	while(fread(file_buf, BUFLEN, 1, fp) == 1) {
		requests++;

		// Envio dos dados.
		reenviar: if(tp_sendto(s, file_buf, BUFLEN, (struct sockaddr *)&si_other) == -1)
		{
			printf("error in sending the file\n");
			exit(1);
		}

		int result = tp_recvfrom(s, ack, BUFLEN, (struct sockaddr *)&si_other);

		// Caso o timeout seja ativado antes do recebimento de um ACK
		// realizar um novo envio
		if(result == -1)
			goto reenviar;

		// Conferência do ack
		if(ack[0] == 'A' && ack[1] == 'C' && ack[2] == 'K') {
			printf("\n%s\n", ack);
		}

		bzero(file_buf, sizeof(file_buf));
		bzero(ack, sizeof(ack));
	}

	// Flag do fim da transmissão
	if(tp_sendto(s, "[END]", BUFLEN, (struct sockaddr *)&si_other) == -1)
	{
		printf("error in sending the file\n");
		exit(1);
	}

	printf("Requisições: %d\n", requests);

	close(s);

	gettimeofday(&endtime, NULL);

	double seg = (endtime.tv_sec - begintime.tv_sec) * 1000.0;	// sec para ms
	seg += (endtime.tv_usec - begintime.tv_usec) / 1000.0; // us para ms
	seg /= 1000;

	double throughput = ((file_size * 8)/1024) / seg; // kilobits por segundo

	printf("Buffer = \%5u byte(s), \%10.2f kbps (\%u bytes em \%lf s)\n",BUFLEN, file_size, throughput, seg);
	return 0;
}