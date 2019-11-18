#include "cliente.h"

void die(char *s)
{
	perror(s);
	exit(1);
}


void inicializa(char *host, int porta, char nome_arquivo[MAX], int tam_buffer) {


	int sockfd;
	
	sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (sockfd == -1) {
		die("socket");
	}


	memset((char *)&si_other, 0, sizeof(si_other));
	si_other.sin_family = AF_INET;
	si_other.sin_port = htons(porta);	



	if (inet_aton(host, &si_other.sin_addr) == 0)
	{
		fprintf(stderr, "inet_aton() failed\n");
		exit(1);
	}


	tranferencia(sockfd, host, porta, nome_arquivo, tam_buffer);
	close(sockfd);


}

void tranferencia(int sockfd, char *host, int porta, char nome_arquivo[MAX],int tam_buffer) {

	FILE *fp;
	char buf[tam_buffer];
	char message[tam_buffer];

		fp = fopen(nome_arquivo, "w+");
	if (fp == NULL){
		printf("Não conseguiu abrir o arquivo %s .\n", nome_arquivo);
	}


		// Envia o nome do arquivo que deverá ser enviado pelo servidor
	if (tp_sendto(sockfd, nome_arquivo, tam_buffer, (struct sockaddr *)&si_other) == -1)
	{
		die("sendto()");
	}

	while (1)
	{
		// Resetar o buffer
		memset(buf, '\0', tam_buffer);

		// Receber os dados do arquivo
		if (tp_recvfrom(sockfd, buf, tam_buffer, (struct sockaddr *)&si_other) == -1)
		{
			die("recvfrom()");
		}

		char* ack = "ACK";

		// Envia o ack para o servidor
		if (tp_sendto(sockfd, ack, tam_buffer, (struct sockaddr *)&si_other) == -1)
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
		fwrite(buf, 1, tam_buffer, fp);
	}

	close(fp);


}
