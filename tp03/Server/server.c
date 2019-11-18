#include "server.h"

void die(char *s) {
	perror(s);
	exit(1);
}

void inicializa(int porta, int tam_buffer) {

	int sockfd;
	char buf[tam_buffer];

	sockfd = tp_socket(porta);

	transferencia(sockfd, tam_buffer, buf);
	close(sockfd);
}

void transferencia(int sockfd, int tam_buffer, char nome_arquivo[MAX]) {

	FILE *fp;
	struct timeval begintime, endtime, tv;

	int i, bytes;
	int w;
	int EndFrame = 0;
	int flag;
	int tamanho_janela = TAM_MAX_JANELA;
	unsigned int frame_id = 0;
	unsigned int QtBytes = tam_buffer;
	unsigned int tamanho_arq;
	int f_recv_size;
	unsigned int qtpacotes;
	double throughput;
	double seg;

	typedef struct frame
	    {
	        char frame_kind; 
	        unsigned int sq_no;
	        unsigned int ack;
	        unsigned int QtBDados;
	        char dados[tam_buffer];
	    } Frame;
	Frame frame_recv;
	Frame frame_send[tamanho_janela];

	f_recv_size = tp_recvfrom(sockfd, (char*) &frame_recv,
			sizeof(frame_recv), (struct sockaddr_in*) &si_me);
	if (f_recv_size == -1) {
		die("recvfrom()");
	}

	if (f_recv_size < sizeof(frame_recv)) {
	
		QtBytes = QtBytes - (sizeof(frame_recv) - f_recv_size);
	}

	else if (f_recv_size != sizeof(frame_recv)) {
		
		die("frame_recv");
	}

	if (f_recv_size > 0 && frame_recv.frame_kind == 1
			&& frame_recv.sq_no == frame_id) {
		printf("[+]Frame Recebido: %s\n", frame_recv.dados);

		frame_send[0].sq_no = 0;
		frame_send[0].frame_kind = 0;
		frame_send[0].ack = frame_recv.sq_no;
		tp_sendto(sockfd, (char*) &(frame_send[0]), sizeof(frame_send[0]),
				(struct sockaddr_in*) &si_me);
		printf("[+]Ack enviado\n");
	} else //fechar o programa
	{

	}
	frame_id++;

	
	/*
	 * Comeca a trabalhar com o arquivo
	 * */
	fp = fopen(frame_recv.dados, "rb");
	if (fp <= 0) {
		printf("Arquivo não localizado\n");
		frame_send[0].frame_kind = 3;
		tp_sendto(sockfd, (char*) &(frame_send[0]), sizeof(frame_send[0]),
				(struct sockaddr_in*) &si_me);
		die("fopen()");
	} else if ((fseek(fp, 0, SEEK_END)) < 0) {
		printf("Arquivo Corrompido\n");
		frame_send[0].frame_kind = 3;
		tp_sendto(sockfd, (char*) &(frame_send[0]), sizeof(frame_send[0]),
				(struct sockaddr_in*) &si_me);
		die("fseek()");
	}
	tamanho_arq = ftell(fp);
	printf("qtb: %d\n", tamanho_arq);
	rewind(fp);


	/*
	 * Calculo para a transferencia
	 * */
	if (tamanho_arq % QtBytes != 0) {
		flag = 1;
	}

	qtpacotes = tamanho_arq / QtBytes + flag;
	printf("Pacotes que seram transmitidos %d\n", qtpacotes);

	

	tv.tv_sec = 1; 
	tv.tv_usec = 0;
	setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (char*) &tv,
			sizeof(struct timeval));

	

	while (frame_recv.frame_kind != 2) //TENTA ENVIAR/RECEBER DADOS ATE RECEBER A CONFIRMACAO DO ULTIMO FRAME
	{

		for (w = 0; w < tamanho_janela; w++) {

			bytes = fread(frame_send[w].dados, sizeof(char), QtBytes, fp);

			frame_send[w].sq_no = frame_id + w; 
			frame_send[w].frame_kind = 1; 
			frame_send[w].QtBDados = bytes;
			frame_send[w].ack = 0;
			EndFrame = w;
			if (bytes != QtBytes) {
				frame_send[w].frame_kind = 2;
			}

			tp_sendto(sockfd, (char*) &(frame_send[w]), sizeof(frame_send[w]),
					(struct sockaddr_in*) &si_me); 

			printf("\nEnviando - frame_id+w:%d", frame_id + w);

			if (bytes != QtBytes) {
				printf("\nEnviou o fim do arquivo");
				break;
			}

		}

		for (i = 0; i < MaxTentativas_msg; i++) 
				{
			for (w = 0; w < tamanho_janela; w++) {

				f_recv_size = tp_recvfrom(sockfd, (char*) &frame_recv,
						sizeof(frame_recv), (struct sockaddr_in*) &si_me);
				printf("\nRecebe W:%d", w);
				if (f_recv_size > 0 && frame_recv.ack > frame_id
						&& frame_recv.ack < frame_id + tamanho_janela) {

					frame_id = frame_recv.ack;
					printf("\n recebe -- frame_id:%d -- resposta do frame %d",
							frame_id, frame_recv.frame_kind);

					if (frame_recv.frame_kind == 2
							|| (frame_send[EndFrame].sq_no + 1) == frame_id) 
									{
						break;
					}

				}

				else if (f_recv_size <= 0) {
					printf("\nTempo acabou.");

					break;
				}

				else if ((frame_send[0].sq_no < frame_recv.ack
						&& frame_send[0].sq_no < frame_recv.ack)) {
					printf("\nRecebeu fora de ordem ACK = %d", frame_recv.ack);

					
				} else {
					printf("\nRecebeu cabeçalho errado");
				}

			}

			if (frame_send[EndFrame].sq_no < frame_id) 
					{
				
				break;

			}

			else if (frame_recv.frame_kind == 2) {
				break;
			}

			else {
				//GO BACK N
				for (w = (frame_id - frame_send[0].sq_no); w < tamanho_janela;
						w++) 
						{

					printf("\nReenviar - %d -", frame_send[w].sq_no);
					tp_sendto(sockfd, (char*) &(frame_send[w]),
							sizeof(frame_send[w]),
							(struct sockaddr_in*) &si_me); 

				}
			}

		}

		if (i >= MaxTentativas_msg && frame_send[EndFrame].frame_kind != 2) {
			printf(
					"\nErro de envio de mensagem %d - sem ACK - %d tentaticas realizadas\n",
					frame_id, i);
			die(""); 
		}

	}

	fclose(fp);

	/*Calculo de tempo*/
	gettimeofday(&endtime, NULL);

	seg = (endtime.tv_sec - begintime.tv_sec) * 1000.0;	// sec para ms
	seg += (endtime.tv_usec - begintime.tv_usec) / 1000.0; // us para ms
	seg /= 1000;

	throughput = ((tamanho_arq * 8) / 1024) / seg; 

	printf("Buffer = \%5u byte(s), \%10.2f kbps (\%u bytes em \%lf s)\n",
			tam_buffer, tamanho_arq, throughput, seg);

}
