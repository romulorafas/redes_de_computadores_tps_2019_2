/* tp_socket.h - Interface a ser usada no acesso a sockets UDP. Essa
 * interface serve para simplificar as chamadas de manipulação de sockets
 * e para permitir que durante os testes do trabalho erros específicos
 * seja injetados no canal de transmissão... :-)
 */

#ifndef _TP_SOCKET_H_ 
#define _TP_SOCKET_H_ 

/* tp_init é uma função de inicialização que deve ser chamada antes de
 * qualquer outra função desta interface. Ela é responsável pela
 * configuração da interface e da preparação de testes especiais quando
 * da avaliação do tp (quando será usada uma versão especial da
 * implementação da interface). Retorna zero se tudo estiver certo e 
 * um valor menor que zero em caso de erro.
 */

int tp_init(void);

/* so_addr deve ser considerado como um tipo opaco que não precisa ser
 * manipulado diretamente, para simplificar o código. Endereços são
 * criados através da chamada da função tp_build_addr ou no recebimento
 * de uma mensagem com recvfrom.
 */
typedef struct sockaddr_in so_addr;

/* tp_socket cria um socket associado ao porto passado como parâmetro, ou
 * a um porto escolhido aleatoriamente pelo SO, no caso do parâmetro ser
 * zero.
 */
int tp_socket(unsigned short port);

/* tp_build_addr cria a struct sockaddr_in correspondente ao par
 * (host,porto) indicados pelos parâmetros. Serve para construir o
 * parâmetro que será usado nas chamadas a sendto se a chamada não for em
 * resposta a uma mensagem recebida com recvfrom.
 */
int tp_build_addr(so_addr* addr, char* hostname, int port);

/* tp_sendto é apenas um encapsulamento à chamada sendto da biblioteca de
 * sockets e deve ser usada sempre em seu lugar. Os parâmetros são uma
 * simplificação dos daquela função e o comportamento deve ser
 * considerado idêntico, inclusive em termos dos valores de retorno.
 */
int tp_sendto(int so, char* buff, int buff_len, so_addr* to_addr);

/* tp_recvfrom é a simétrica da anterior. Nesse caso, from_addr é um
 * buffer que será preenchido no retorno da função com o endereço de
 * origem da mensagem recebida.
 */
int tp_recvfrom(int so, char* buff, int buff_len, so_addr* from_addr);

/* tp_mtu retorna o tamanho máximo da mensagem que pode ser enviada
 * através desta interface. Esse valor pode variar entre 512 e 2048 bytes
 * e deve ser testado a cada execução do protocolo.
 */
int tp_mtu(void);

#endif /* _TP_SOCKET_H_ */
