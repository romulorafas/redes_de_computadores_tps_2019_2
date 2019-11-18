/* tp_socket.c - funções auxiliares para uso de sockets UDP
 */

#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <strings.h>

#include "tp_socket.h"

#define MTU 1024 

int tp_mtu(void)
{
    fprintf(stderr,"tp_mtu called\n");
    /*******************************************************
     * A alteração do MTU oferecido para o PJD pode ser    *
     * feita alterando-se o valor da macro usada a seguir. *
     *******************************************************/
    return MTU;
}

int tp_sendto(int so, char* buff, int buff_len, so_addr* to_addr)
{
    int count;
    fprintf(stderr,"tp_sendto called (%d bytes)\n", buff_len);
    /*******************************************************
     * Aqui seria um bom lugar para injetar erros a fim de *
     * exercitar a funcionalidade do protocolo da camada   *
     * acima (o PJD).                                      *
     *******************************************************/
    count = sendto(so, (void*)buff, buff_len, 0,
            (struct sockaddr*) to_addr, sizeof(struct sockaddr_in));
    fprintf(stderr,"tp_sendto returning (sent %d bytes)\n", count);
    return count;
    
}

int tp_recvfrom(int so, char* buff, int buff_len, so_addr* from_addr)
{
    int count;
    unsigned int sockaddr_len = sizeof(struct sockaddr_in);
    fprintf(stderr,"tp_recvfrom called (%d bytes)\n",buff_len);
    /*******************************************************
     * Aqui seria um bom lugar para injetar erros a fim de *
     * exercitar a funcionalidade do protocolo da camada   *
     * acima (o PJD).                                      *
     *******************************************************/
    count = recvfrom(so,(void*)buff,(size_t)buff_len,0,
            (struct sockaddr*) from_addr, &sockaddr_len);
    fprintf(stderr,"tp_recvfrom returning (received %d bytes)\n",count);
    return count;
}

int tp_init(void)
{
    fprintf(stderr,"tp_init called\n");
    /*********************************************************
     * Exceto para fins de automatizar os testes com versões *
     * alteradas deste código (para injetar erros), não deve *
     * haver motivo para se alterar esta função.             *
     *********************************************************/
    return 0;
}

/*****************************************************
 * A princípio não deve haver motivo para se alterar *
 * as funções a seguir.                              *
 *****************************************************/

int tp_socket(unsigned short port)
{
    int    so;
    struct sockaddr_in local_addr;
    int    addr_len =sizeof(local_addr);

    fprintf(stderr,"tp_socket called\n");
    if ((so=socket(PF_INET,SOCK_DGRAM,0))<0) {
        return -1;
    }
    if (tp_build_addr(&local_addr,INADDR_ANY,port)<0) {
        return -2;
    }
    if (bind(so, (struct sockaddr*)&local_addr, sizeof(local_addr))<0) {
        return -3;
    }
    return so;
}

int tp_build_addr(so_addr* addr, char* hostname, int port)
{
    struct hostent* he;

    fprintf(stderr,"tp_build_addr called\n");
    addr->sin_family = PF_INET;
    addr->sin_port   = htons(port);
    if (hostname==NULL) {
        addr->sin_addr.s_addr = INADDR_ANY;
    } else {
        if ((he=gethostbyname(hostname))==NULL) {
            return -1;
        }
        bcopy(he->h_addr,&(addr->sin_addr.s_addr),sizeof(in_addr_t));
    }
    return 0;
}
