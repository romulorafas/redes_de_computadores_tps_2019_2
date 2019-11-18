#include "cliente.h"

void inicializa(char *host, int porta, char nome_arquivo[MAX], int tam_buffer) {
	int sockfd;
	struct sockaddr_in servaddr;

	// socket create and varification
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd == -1) {
		printf("Erro na cricao do socket...\n");
		exit(0);
	}

	bzero(&servaddr, sizeof(servaddr));

	// assign IP, PORT
	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = inet_addr(host);
	servaddr.sin_port = htons(porta);

	// connect the client socket to server socket
	if (connect(sockfd, (SA*) &servaddr, sizeof(servaddr)) != 0) {
		printf("Nao conseguiu conectar no servidor...\n");
		exit(0);
	}

	tranferencia(sockfd, host, porta, nome_arquivo, tam_buffer);

}

void tranferencia(int sockfd, char *host, int porta, char nome_arquivo[MAX],
		int tam_buffer) {



	char revbuf[tam_buffer];
	FILE *fr;
	int fr_block_sz = 0;
	int write_sz ;

	write(sockfd, nome_arquivo, (sizeof(nome_arquivo) + 1));

	printf("Recebendo o arquivo...\n");

	fr = fopen(nome_arquivo, "w+");
	if (fr == NULL){
		printf("Não conseguiu abrir o arquivo %s .\n", nome_arquivo);
	}
	else {
		bzero(revbuf, tam_buffer);
		while ((fr_block_sz = recv(sockfd, revbuf, tam_buffer, 0)) > 0) {
			write_sz = fwrite(revbuf, sizeof(char), fr_block_sz, fr);
			if (write_sz < fr_block_sz) {
				printf("Falhou em escrever no arquivo.\n");
			}
			bzero(revbuf, tam_buffer);
			if (fr_block_sz == 0 || fr_block_sz != tam_buffer) {
				break;
			}
		}
		if (fr_block_sz <= 0) {
			printf("Não recebeu o arquivo!\n");
		}
		else{
			printf("Recebeu arquivo do servidor!\n");
		}
		fclose(fr);
	}
	close(sockfd);
}
