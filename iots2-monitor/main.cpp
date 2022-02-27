#include "Helper.hpp"
#include <iostream>
#include <thread>
#include <chrono>
#include "tcp_client.hpp"

constexpr int refresh = 1000;

int main()
{
    auto sockfd = tcp_client("10.10.10.17", 7788);
    std::string msg = "";
    std::string ip = "10.10.10.3";
    std::string host = "pdnas";
    char recv_data[MAXLINE];
    memset(recv_data, '\0', MAXLINE);

    while (true)
    {
        //! 进行清除，否则会造成格式混乱！
        msg.clear();

        msg.append(host);
        msg.append("#");
        msg.append(Helper::uptime());
        msg.append("#");
        msg.append(ip);
        msg.append("#");
        msg.append(Helper::cpu_model());
        msg.append("#");
        msg.append(Helper::cpu_temp());
        msg.append("#");
        msg.append(Helper::cpu_freq());
        msg.append("#");
        msg.append(Helper::mem_available());
        msg.append("#");
        msg.append(Helper::mem_max());

        send(sockfd, msg.c_str(), msg.length(), 0);

        // 接收到服务端发送的 'OK'，进行下一次发送。
        while (true)
        {
            recv(sockfd, recv_data, MAXLINE, 0);

            if (std::string(recv_data) == "OK")
            {
                // std::cout << recv_data << '\n';
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(refresh / 10));
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(refresh));
    }

    return 0;
}