#include "server.h"


void die(char *s)
{
	perror(s);
	exit(1);
}


void inicializa(int porta, int tam_buffer) {


	int sockfd;
	char buf[tam_buffer];


	sockfd = tp_socket(porta);

	// Recepção do nome do arquivo que será enviado
	if (tp_recvfrom(sockfd, buf, 1024, (struct sockaddr *)&si_other) == -1) {
		die("recvfrom()");
	}



	transferencia(sockfd, tam_buffer, buf);
	close(sockfd);
}

void transferencia(int sockfd, int tam_buffer, char nome_arquivo[MAX]) {

	FILE *fp;
	char ack[tam_buffer];
	char file_buf[tam_buffer];

	struct timeval begintime, endtime,tv;

			/**
	 * Configuração do timeout do socket 
	 */ 
	tv.tv_sec = 3;
	if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0)
	{
		perror("Error");
	}

	fp = fopen(nome_arquivo, "r");

	if (fp == NULL)
	{
		printf("ERRO: Arquivo %s não encontrado no servidor\n", nome_arquivo);
		close(sockfd);
		exit(1);

	}

	// Cálculo do tamanho do arquivo
	fseek(fp, 0, SEEK_END);
	size_t file_size = ftell(fp);
	fseek(fp, 0, SEEK_SET);

	printf("Tamanho do arquivo: %d\n", file_size);

	int requests = 0;

	// A cada bloco lido, de tamanho do BUFFER estipulado nos argumentos
	while(fread(file_buf, tam_buffer, 1, fp) == 1) {
		requests++;

		// Envio dos dados.
		reenviar:
		if(tp_sendto(sockfd, file_buf, tam_buffer, (struct sockaddr *)&si_other) == -1)
		{
			printf("ERRO: Falha ao enviar o arquivo %s.\n",	nome_arquivo);
		close(sockfd);
			exit(1);
		}

		int result = tp_recvfrom(sockfd, ack, tam_buffer, (struct sockaddr *)&si_other);

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
	if(tp_sendto(sockfd, "[END]", tam_buffer, (struct sockaddr *)&si_other) == -1)
	{
		printf("ERRO: Falha ao enviar o arquivo %s.\n",
					nome_arquivo);
			close(sockfd);

		exit(1);
	}

	printf("Requisições: %d\n", requests);


	gettimeofday(&endtime, NULL);

	double seg = (endtime.tv_sec - begintime.tv_sec) * 1000.0;	// sec para ms
	seg += (endtime.tv_usec - begintime.tv_usec) / 1000.0; // us para ms
	seg /= 1000;

	double throughput = ((file_size * 8)/1024) / seg; // kilobits por segundo

	printf("Buffer = \%5u byte(s), \%10.2f kbps (\%u bytes em \%lf s)\n",tam_buffer, file_size, throughput, seg);







}
