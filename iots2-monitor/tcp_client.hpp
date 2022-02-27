#include "Helper.hpp"
#include <string>
#include <thread>
#include <chrono>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<errno.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<unistd.h>

#define MAXLINE 4096

static int tcp_client(const std::string server_ip, const int server_port)
{
    int   sockfd, n;
    char  recvline[4096];
    struct sockaddr_in  servaddr;

    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("create socket error: %s(errno: %d)\n", strerror(errno),errno);
        return -1;
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(server_port);
    if (inet_pton(AF_INET, server_ip.c_str(), &servaddr.sin_addr) <= 0)
    {
        printf("inet_pton error for %s\n", server_ip.c_str());
        return -1;
    }

    if (connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
    {
        printf("connect error: %s(errno: %d)\n",strerror(errno),errno);
        return -1;
    }
    
    // while (true)
    // {
    //     send(sockfd, msg.c_str(), msg.length(), 0);
    // }
    return sockfd;
}