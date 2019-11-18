/* tp_socket.h - Interface a ser usada no acesso a sockets UDP. Essa
 * interface serve para simplificar as chamadas de manipula��o de sockets
 * e para permitir que durante os testes do trabalho erros espec�ficos
 * sejam injetados no canal de transmiss�o (ex. perdas de pacotes ou 
 * erros de bits)... :-)
 */

#ifndef _TP_SOCKET_H_ 
#define _TP_SOCKET_H_ 

#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <strings.h>

/* tp_init � uma fun��o de inicializa��o que deve ser chamada antes de
 * qualquer outra fun��o desta interface. Ela � respons�vel pela
 * configura��o da interface e da prepara��o de testes especiais quando
 * da avalia��o do tp (quando ser� usada uma vers�o especial da
 * implementa��o da interface). Retorna zero se tudo estiver certo e 
 * um valor menor que zero em caso de erro.
 */

int tp_init(void);

/* so_addr deve ser considerado como um tipo opaco que n�o precisa ser
 * manipulado diretamente, para simplificar o c�digo. Endere�os s�o
 * criados atrav�s da chamada da fun��o tp_build_addr ou no recebimento
 * de uma mensagem com recvfrom.
 */
typedef struct sockaddr_in so_addr;

/* tp_socket cria um socket associado ao porto passado como par�metro, ou
 * a um porto escolhido aleatoriamente pelo SO, no caso do par�metro ser
 * zero.
 */
int tp_socket(unsigned short port);

/* tp_build_addr cria a struct sockaddr_in correspondente ao par
 * (host,porto) indicados pelos par�metros. Serve para construir o
 * par�metro que ser� usado nas chamadas a sendto se a chamada n�o for em
 * resposta a uma mensagem recebida com recvfrom.
 */
int tp_build_addr(so_addr* addr, char* hostname, int port);

/* tp_sendto � apenas um encapsulamento � chamada sendto da biblioteca de
 * sockets e deve ser usada sempre em seu lugar. Os par�metros s�o uma
 * simplifica��o dos daquela fun��o e o comportamento deve ser
 * considerado id�ntico, inclusive em termos dos valores de retorno.
 */
int tp_sendto(int so, char* buff, int buff_len, so_addr* to_addr);

/* tp_recvfrom � a sim�trica da anterior. Nesse caso, from_addr � um
 * buffer que ser� preenchido no retorno da fun��o com o endere�o de
 * origem da mensagem recebida.
 */
int tp_recvfrom(int so, char* buff, int buff_len, so_addr* from_addr);

#endif /* _TP_SOCKET_H_ */
