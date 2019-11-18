#include "server.h"

void inicializa(int porta, int tam_buffer) {

	int sockfd, connfd, len;
	struct sockaddr_in servaddr, cli;

	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd == -1) {
		printf("Criacao do socket falhou...\n");
		exit(0);
	}

	bzero(&servaddr, sizeof(servaddr));

	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port = htons(porta);

	if ((bind(sockfd, (SA*) &servaddr, sizeof(servaddr))) != 0) {
		printf("Ligacao do socket falhou...\n");
		exit(0);
	}

	if ((listen(sockfd, 5)) != 0) {
		printf("Listen falhou...\n");
		exit(0);
	}

	len = sizeof(cli);

	connfd = accept(sockfd, (SA*) &cli, &len);
	if (connfd < 0) {
		printf("Servidor falhou...\n");
		exit(0);
	} else
		printf("Cliente aceito pelo servidor...\n");

	// Funcao para procurar arquivo e faz a tranferencia para o cliente
	transferencia(connfd, tam_buffer);
	close(sockfd);
}

void transferencia(int sockfd, int tam_buffer) {

	char nome_arquivo[MAX];
	char sdbuf[tam_buffer];
	int fs_block_sz;
	FILE *fs;
	struct timeval begintime, endtime;

	bzero(nome_arquivo, MAX);
	read(sockfd, nome_arquivo, sizeof(nome_arquivo));

	printf("Enviando arquivo %s para o cliente...\n", nome_arquivo);
	gettimeofday(&begintime, NULL);

	fs = fopen(nome_arquivo, "r");
	if (fs == NULL) {
		printf("ERRO: Arquivo %s não encontrado no servidor\n", nome_arquivo);
		close(sockfd);
		exit(1);
	}

	// Cálculo do tamanho do arquivo
	fseek(fs, 0, SEEK_END);
	size_t file_size = ftell(fs);
	fseek(fs, 0, SEEK_SET);

	bzero(sdbuf, tam_buffer);

	while ((fs_block_sz = fread(sdbuf, sizeof(char), tam_buffer, fs)) > 0) {
		if (send(sockfd, sdbuf, fs_block_sz, 0) < 0) {
			printf("ERRO: Falha ao enviar o arquivo %s.\n",
					nome_arquivo);
			close(sockfd);
			exit(1);
		}
		bzero(sdbuf, tam_buffer);
	}

	printf("Arquivo enviado para o cliente!\n");

	gettimeofday(&endtime, NULL);
	double seg = (endtime.tv_sec - begintime.tv_sec) * 1000.0;	// sec para ms
	seg += (endtime.tv_usec - begintime.tv_usec) / 1000.0; // us para ms
	seg /= 1000;
	double throughput = ((file_size * 8)/1024) / seg; // kilobits por segundo
	printf("Buffer = \%5u byte(s), \%10.2f kbps (\%u bytes em \%lf s)\n",tam_buffer, file_size, throughput, seg);

	fclose(fs);
	bzero(nome_arquivo, MAX);

}
