#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import threading

'''
包头：
    1.操作代码（大小：2B 0.更新列表 1.发送聊天内容 2.单人聊天模式）
    2.数据的大小（15B）
    3.变长聊天消息(昵称:聊天内容)
'''

# def header_rev(sock_conn, client_addr):
#     try:
#         while True:
#             op_data = sock_conn.recv(2)
#             if op_data.decode().rstrip() == '01':
#                 client_chat(sock_conn, client_addr)
#             elif op_data.decode().rstrip() == '02':
#                 solo_chat(sock_conn, client_addr)
#     except Exception as e:
#         print(e)
#     # finally:
#     #     client_socks.remove((sock_conn, client_addr))
#     #     sock_conn.close()
#     #     updata_people()


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
                    for sock_tmp in client_socks.keys(): 
                        #判断套接字是不是发送方，如果是就不发送消息，否则发消息
                        if sock_tmp is not sock_conn:
                            try:
                                sock_tmp.send('01'.encode())
                                sock_tmp.send(msg_len_data)
                                sock_tmp.send(msg_content_data)
                            except:
                                del client_socks[sock_tmp]
                                sock_tmp.close()   
                                   
                    continue
                break
    finally:
        del solo_socks[client_socks[sock_conn]]
        del client_socks[sock_conn]
        sock_conn.close()
        updata_people()

def solo_chat(sock_conn2, client_addr1):
    print("solo start")
    try:
        while True:
            #接收目标
            target_size = sock_conn2.recv(3)
            target_size = int(target_size.decode().rstrip())
            recv_size = 0
            target = b""
            # print('target_size',target_size)
            while recv_size < target_size:
                tmp_data = sock_conn2.recv(target_size - recv_size)
                if not tmp_data:
                    break
                target += tmp_data
                recv_size += len(tmp_data)
            target = target.decode()
            print('target:',target)
            
            if target in solo_socks:
                #接收消息
                msg_len_data = sock_conn2.recv(15)
                msg_len = int(msg_len_data.decode().rstrip())
                recv_size = 0
                msg_content_data = b""
                while recv_size < msg_len:
                    tmp_data = sock_conn2.recv(msg_len - recv_size)
                    if not tmp_data:
                        break
                    msg_content_data += tmp_data
                    recv_size += len(tmp_data)
                else:
                    # 目标对象
                    targ_sock = solo_socks.get(target)
                    try:
                        '''发送发送方的ID'''
                        #根据sock获取响应的id
                        sender_id = list(filter(lambda x:solo_socks[x] == sock_conn2, solo_socks))
                        print('sender:',sender_id)
                        sender_len = "{:<3}".format(len(sender_id[0])).encode() 
                        targ_sock.send(sender_len)
                        targ_sock.send(sender_id[0].encode())
                        #发送内容
                        targ_sock.send(msg_len_data)
                        targ_sock.send(msg_content_data)
                    except:
                        sock_conn2.send("{:<15}".format(len('系统通知: 对方已下线'.encode())).encode())
                        sock_conn2.send('系统通知: 对方已下线'.encode())             
            else:
                sock_conn2.send('02'.encode())
                sock_conn2.send("{:<15}".format(len('系统通知: 对方已下线'.encode())).encode())
                sock_conn2.send('系统通知: 对方已下线'.encode())  
    except Exception as e:
        print("solo error:",e)
    finally:
        
        sock_conn2.close()


def updata_people():
    try:
        #取出用户名，放入列表
        people_list = client_socks.values()
        people_sock = client_socks.keys()
        for ps,pl in zip(people_sock,people_list): 
            name_tmp = people_list
           
            # #判断套接字是不是发送方，如果是就不发送消息，否则发消息
            # name_tmp.remove(pl)

            list_data  = ",".join(name_tmp)
            list_len = "{:<15}".format(len(str(list_data).encode())).encode()
            try:
                print(list_data,list_len)
                ps.send('00'.encode())
                ps.send(list_len)
                ps.send(str(list_data).encode())
            except:
                del client_socks[ps]
                ps.close()

    except Exception as e:
        print("1",e)

#创建主监听套接字
sock_listen = socket.socket()
sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_listen.bind(("127.0.0.1", 9999))
sock_listen.listen(5)

#创建单人聊天的套接字
sock2_listen = socket.socket()
sock2_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock2_listen.bind(("127.0.0.1", 9998))
sock2_listen.listen(5)

#存储群聊客户端列表
client_socks = {}
#存储单人聊天客户端列表
solo_socks = {}

while True:
    #客户端监听
    sock_conn, client_addr = sock_listen.accept()
    sock2_conn, client2_addr = sock2_listen.accept()

    #接收客户端的昵称，并判断是否已存在
    while True:
        #接收用户名
        name_size = sock2_conn.recv(2)
        name_size = int(name_size.decode().rstrip())
        recv_size = 0
        name = b""
        while recv_size < name_size:
            tmp_data = sock2_conn.recv(name_size - recv_size)
            if not tmp_data:
                break
            name += tmp_data
            recv_size += len(tmp_data)
        else:
            #存储用户信息
            if name.decode() not in solo_socks:
                sock2_conn.send('0'.encode())
                client_socks[sock_conn]=name.decode()
                solo_socks[name.decode()]=sock2_conn
                #更新列表
                threading.Thread(target=updata_people).start()

                #多人聊天及在线列表
                threading.Thread(target=client_chat, args=(sock_conn, client_addr)).start()

                #单人聊天    
                threading.Thread(target=solo_chat, args=(sock2_conn, client2_addr)).start()
                break
            else: 
                #返回客户端，用户名已存在
                sock2_conn.send('1'.encode())
        

    

   