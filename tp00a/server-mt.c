#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <signal.h>

#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>

void sigint_handler(int signun) {
	close(signun);
	exit(EXIT_SUCCESS);
}

void logexit(const char *str) {
	perror(str);
	exit(EXIT_FAILURE);
}

void print_bin(int x) {
	for (int i = 31; i >= 0; i--) {
		printf("%d", x&(1<<i) == 1);
	}
	printf("\n");
}

struct dados {
	int sock;
	struct sockaddr_in addr;
};

void * client_thread(void *param) {
	pthread_t tid = pthread_self();
	struct dados *dd = param;
	int r = dd->sock;

	char ipcliente[512];
	inet_ntop(AF_INET, &(dd->addr.sin_addr),
			ipcliente, 512);

	printf("conexao de %s %d\n", ipcliente,
			(int)ntohs(dd->addr.sin_port));

	printf("thread %x esperando receber\n",
			(unsigned int)tid);
	
	char buf[512];
	// size_t c = recv(r, buf, 512, 0);
	// printf("recebemos %d bytes\n", (int)c);
	// puts(buf);
	
	uint32_t size;
	size_t c = recv(r, &size, sizeof(uint32_t), 0);
	printf("recebemos %d bytes\n", (int) c);
	printf("%d %d\n", size, ntohl(size));
	print_bin(size);
	print_bin(ntohl(size));
	size = ntohl(size);

	sprintf(buf, "seu IP eh %s %d\n", ipcliente,
			(int)ntohs(dd->addr.sin_port));
	printf("enviando %s\n", buf);

	send(r, buf, strlen(buf)+1, 0);
	printf("enviou\n");

	close(r);
	pthread_exit(EXIT_SUCCESS);
}

int main(int argc, char **argv) {
	signal(SIGINT, sigint_handler);

	int port = atoi(argv[1]);

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
	// Interface for sockets. It's a parameter for connect function
	struct sockaddr *addrptr = (struct sockaddr *)&addr;
	addr.sin_family = AF_INET; // address family, AF_xxx. If it were IPv6, then it wold be AF_INET6. 
	addr.sin_port = htons(port); // converts the unsigned short integer hostshot for host byte order to netword byte order.
	addr.sin_addr = inaddr;

	// Assign a local socket address to a socket identified by descriptor
	// that has no local socket address assigned.
	// int bind(int socket, const struct sockaddr *address, socklen_t
	// address_len))
	if (bind(s, addrptr, sizeof(struct sockaddr_in)))
		logexit("bind");

	// Listen for socket connections and limit the queue for incoming
	// connections.
	// int listen(int socket, int backlog)
	if(listen(s, 10))
		logexit("listen");
	printf("esperando conexao\n");

	while(1) {
		struct sockaddr_in raddr;
		struct sockaddr *raddrptr =
			(struct sockaddr *)&raddr;
		socklen_t rlen = sizeof(struct sockaddr_in);

		// Accept a connection on a socket
		// int accept(int sockfd, struct sockaddr *addr, socklen_t
		// *addrlen);
		// Return a file descriptor for the accepted socket or -1.
		int r = accept(s, raddrptr, &rlen);
		if (r == -1)
			logexit("accept");

		struct dados *dd = malloc(sizeof(*dd));
		if (!dd)
			logexit("malloc");
		dd->sock = r;
		dd->addr = raddr;

		pthread_t tid;
		pthread_create(&tid, NULL, client_thread, dd);
	}

	exit(EXIT_SUCCESS);
}





