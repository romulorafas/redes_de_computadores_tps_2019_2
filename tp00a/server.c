#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>

#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>

void logexit(const char *str) {
	perror(str);
	exit(EXIT_FAILURE);
}


int main(void) {
	int s;
	// sockfd = socket(int socket_family, int socket_type, int protocol);
	s = socket(AF_INET, SOCK_STREAM, 0);
	if (s == -1)
		logexit("socket");

	// internet address, used by sockaddr_in
	struct in_addr inaddr;
	// convert IPv4 and IPv6 adsresses from text to binary form
	inet_pton(AF_INET, "127.0.0.1", &inaddr);

	// IPv4 AF_INET6 sockets
	struct sockaddr_in addr;
	// Interface for sockets. It's a parameter for connect function.
	struct sockaddr *addrptr = (struct sockaddr *)&addr;
	addr.sin_family = AF_INET; // address family, AF_xxx. If it were IPv6, then it would be AF_INET6.
	addr.sin_port = htons(5152); // converts the unsigned short integer hostshot for host byte order to network byte order.
	addr.sin_addr = inaddr;

	// Assign a local socket address to a socket identified by descriptor that
	// has no local socket address assigned.
	// int bind( int socket, const struct sockaddr *address, socklen_t
	// address_len)
	if (bind(s, addrptr, sizeof(struct sockaddr_in)))
		logexit("bind");

	// Listen for socket connections and limit the queue of incoming
	// connections.
	// int listen(int socket, int backlog)
	if (listen(s, 10))
		logexit("listen");
	printf("esperando conexao\n");

	while(1) {
		struct sockaddr_in raddr;
		struct sockaddr *raddrptr =
			(struct sockaddr *)&raddr;
		socklen_t rlen = sizeof(struct sockaddr_in);

		int r = accept(s, raddrptr, &rlen);
		if(r == -1)
			logexit("accept");

		char buf[512];
		char ipcliente[512];
		inet_ntop(AF_INET, &(raddr.sin_addr),
				ipcliente, 512);

		printf("conexao de %s %d\n", ipcliente,
				(int)ntohs(raddr.sin_port));

		size_t c = recv(r, buf, 512, 0);
		printf("recebemos %d bytes\n", (int)c);
		puts(buf);

		sprintf(buf, "seu IP eh %s %d\n", ipcliente,
				(int)ntohs(raddr.sin_port));
		printf("enviando %s\n", buf);

		send(r, buf, strlen(buf)+1, 0);
		printf("enviou\n");

		close(r);
	}

	exit(EXIT_SUCCESS);
}

