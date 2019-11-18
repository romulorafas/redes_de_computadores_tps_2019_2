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
	typedef struct frame
	    {
	        char frame_kind; //FRAME NORMAL
	        unsigned int sq_no;//Para FRAME 0
	        unsigned int ack;//VALOR ARBITRARIO
	        unsigned int QtBDados;
	        char dados[tam_buffer];
	    } Frame;

	    struct timeval tv;
	    int f_recv_size,tamanho_arquivo;
	    unsigned int frame_id = 0 , QtBytes = tam_buffer;
	    Frame frame_send;
	    Frame frame_recv;
	    int ack_recv = 0;
	    int i=0;
	    struct timeval now;
	    double inicio, fim;
	    char *ptr; 
	    int buffer_t=0;

		//Timer
	    tv.tv_sec = SegundosEspera;
	    tv.tv_usec = 0;
	    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (char*)&tv, sizeof(struct timeval));


	   //Arquivo
	        frame_send.sq_no = frame_id; 
	        frame_send.frame_kind = 1; 
	        frame_send.ack = 0; 


	        fp = fopen(nome_arquivo, "wb");

	        strcpy(frame_send.dados, nome_arquivo);


	        while(ack_recv == 0 && i<Tentativas_s)
	        {
	            tp_sendto(sockfd,(char*)&(frame_send),sizeof(frame_send),(struct sockaddr_in*)&si_other);
	            printf("[+]Arquivo solicitado\n");

	            f_recv_size = tp_recvfrom(sockfd,(char*)&frame_recv,sizeof(frame_recv),(struct sockaddr_in*)&si_other);

	            if( f_recv_size > 0 && frame_recv.sq_no == 0 && frame_recv.ack == frame_id)
	            {
	                printf("[+]Ack Recebido\n");
	                ack_recv = 1;
	                break;
	            }

	            else
	            {
	                i++;
	            }

	        }
	        if(i>Tentativas_s-1)
	        {
	            printf("Servidor Não localizado,foram feitas %d tentativas, Programa Finalizado\n",Tentativas_s);
	            die("");
	        }
	        frame_id++; 



			//Tempo 
	        gettimeofday(&now,NULL);
	        inicio = ( (double) now.tv_usec )/ 1000000.0;
	        inicio += ( (double) now.tv_sec );

	 
			//Transmitir
	        while(frame_recv.frame_kind !=2)  
	        {

	            f_recv_size = tp_recvfrom(sockfd,(char*)&frame_recv,sizeof(frame_recv),(struct sockaddr_in*)&si_other);
	                printf("\n RECEBEU-sqn: %d",frame_recv.sq_no);
	            if (f_recv_size>0 && frame_id == frame_recv.sq_no)
	            {
	                frame_send.ack = frame_recv.sq_no+1;
	                frame_send.sq_no = frame_recv.sq_no;
	                frame_send.frame_kind = 0;
	                if(frame_recv.frame_kind == 2)
	                {
	                    frame_send.frame_kind = 2;
	                }

	                fwrite(frame_recv.dados, sizeof(char),frame_recv.QtBDados,fp); 
	                printf("\n ACK - %d -- kind: %d",frame_send.ack,frame_send.frame_kind);
	                tp_sendto(sockfd,(char*)&(frame_send),sizeof(frame_send),(struct sockaddr_in*)&si_other);
	                frame_id++; 

	            }

	            else if (f_recv_size<0) 
	            {
	                printf("\n\n(Estourou o tempo) %d Segundos sem resposta do servidor\nPrograma Finalizado\n",SegundosEspera);
	                die("");
	            }
	            else  
	            {
	                if(frame_recv.frame_kind == 3)
	                {
	                    printf("Erro no servidor (ARQ ñ Localizado,etc)\n");
	                    die("");
	                }
	                printf("\n----Reenviou --- ACK : %d",frame_send.ack);
	                tp_sendto(sockfd,(char*)&(frame_send),sizeof(frame_send),(struct sockaddr_in*)&si_other);

	            }
	        }

	       
			//Tmepo
	        tp_sendto(sockfd,(char*)&(frame_send),sizeof(frame_send),(struct sockaddr_in*)&si_other); 
	        gettimeofday(&now,NULL);
	        fim = ( (double) now.tv_usec ) / 1000000.0 ;
	        fim += ( (double) now.tv_sec );

	        tamanho_arquivo = (frame_recv.sq_no-1)*QtBytes + frame_recv.QtBDados;

	        printf("\n\nBuffer = \%5d bytes,\%10.2lf kbps (\%d bytes em %lf s)\n\n",QtBytes,tamanho_arquivo/(1000.0*(fim - inicio)),tamanho_arquivo,fim - inicio);

	        fclose(fp);


}
