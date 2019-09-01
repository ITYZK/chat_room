#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import threading


# UDP打洞
# 定长包头(15B) + 变长聊天消息(昵称:聊天内容)

def client_chat(sock_conn, client_addr):
    try:
        while True:
                msg_len_data = sock_conn.recv(15)
                if not msg_len_data:
                    break

                msg_len = int(msg_len_data.decode().rstrip())
                recv_size = 0
                msg_content_data = b""
                while recv_size < msg_len:
                    tmp_data = sock_conn.recv(msg_len - recv_size)
                    if not tmp_data:
                        break
                    msg_content_data += tmp_data
                    recv_size += len(tmp_data)
                else:
                    # 发送给其他所有在线的客户端
                    for sock_tmp, tmp_addr in client_socks: 
                        #判断套接字是不是发送方，如果是就不发送消息，否则发消息
                        if sock_tmp is not sock_conn:
                            try:
                                sock_tmp.send(msg_len_data)
                                sock_tmp.send(msg_content_data)
                            except:
                                client_socks.remove((sock_tmp, tmp_addr))
                                sock_tmp.close()
                    continue
                break
    finally:
            client_socks.remove((sock_conn, client_addr))
            sock_conn.close()


sock_listen = socket.socket()
sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_listen.bind(("0.0.0.0", 9999))
sock_listen.listen(5)

#创建客户端列表
client_socks = []

while True:
    sock_conn, client_addr = sock_listen.accept()
    #将接听到的客户端加入列表，并为客户端创建一个线程
    client_socks.append((sock_conn, client_addr))
    threading.Thread(target=client_chat, args=(sock_conn, client_addr)).start()



