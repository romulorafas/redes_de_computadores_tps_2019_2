#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include "tp_socket.h"

void die(char *s)
{
	perror(s);
	exit(1);
}

int main(int argc, char *argv[])
{

	if (argc <= 3)
	{
		printf("Faltando argumentos!");
		exit(1);
	}

	// Parse dos argumentos da linha de comando
	char* SERVER = argv[1];
	int PORT     = atoi(argv[2]);
	char* NAME   = argv[3];
	int BUFLEN   = atoi(argv[4]);

	struct sockaddr_in si_other;
	int s, i, slen = sizeof(si_other);
	char buf[BUFLEN];
	char message[BUFLEN];

	if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1)
	{
		die("socket");
	}

	memset((char *)&si_other, 0, sizeof(si_other));
	si_other.sin_family = AF_INET;
	si_other.sin_port = htons(PORT);

	if (inet_aton(SERVER, &si_other.sin_addr) == 0)
	{
		fprintf(stderr, "inet_aton() failed\n");
		exit(1);
	}

	FILE *fp;

	fp = fopen("output.txt", "w+");

	if (fp == NULL)
	{
		printf("file does not exist\n");
		exit(1);
	}

	// Envia o nome do arquivo que deverá ser enviado pelo servidor
	if (tp_sendto(s, NAME, BUFLEN, (struct sockaddr *)&si_other) == -1)
	{
		die("sendto()");
	}

	while (1)
	{
		// Resetar o buffer
		memset(buf, '\0', BUFLEN);

		// Receber os dados do arquivo
		if (tp_recvfrom(s, buf, BUFLEN, (struct sockaddr *)&si_other) == -1)
		{
			die("recvfrom()");
		}

		char* ack = "ACK";

		// Envia o ack para o servidor
		if (tp_sendto(s, ack, BUFLEN, (struct sockaddr *)&si_other) == -1)
		{
			die("sendto()");
		}

		puts(buf);

		// Detecção do fim da transmissão
		if(buf[0] == '['
		&& buf[1] == 'E'
		&& buf[2] == 'N'
		&& buf[3] == 'D'
		&& buf[4] == ']') {
			break;
		}

		// Escrita no arquivo de destino
		fwrite(buf, 1, BUFLEN, fp);
	}

	close(s);
	close(fp);
	return 0;
}