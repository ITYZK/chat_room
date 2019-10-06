#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import tkinter as tk
import socket
from tkinter import messagebox
from threading import Thread,Lock
from multiprocessing import Process
from solo_char_client import Solo


#定长包头（15B）+ 变长聊天记录（格式：昵称:聊天内容）

solo_peoples = {}
lock = Lock()


def on_send_msg():
    '''发送包头和消息，并将信息显示在接受框内'''
    
    #获取消息编辑框的消息
    chat_msg = chat_msg_box.get(1.0,'end')
    if chat_msg == '\n':
        return
    chat_data = name + ': ' + chat_msg
    chat_data = chat_data.encode()
    data_len = "{:<15}".format(len(chat_data)).encode()
    try:
        sock.send(data_len )
        sock.send(chat_data)
    except:
        tk.messagebox.showerror('网络上天了',"发送失败，请检查网络")
    else:
        #将消息编辑框内的消息删除
        chat_msg_box.delete(1.0,'end')
        #设置接收框为可编辑模式（正常模式）
        chat_record_box.configure(state=tk.NORMAL)
        #将数据显示在接收框内
        chat_record_box.insert("end",chat_data.decode() + '\n')
        #将接收框设置为不可编辑模式
        chat_record_box.configure(state=tk.DISABLED)
        chat_record_box.see(tk.END)


def recv_msg():

        '''接收包头，分析操作码'''
        
    # try:
        while True:
            #接收操作码
            op_data = sock.recv(2)
            print(op_data)
            if not op_data:
                break
            # print(op_data.decode())
            if op_data.decode() == '01':
                #接收群聊天消息
                show_info()
            elif op_data.decode() == '00':
                #更新列表
                show_people_list()
               
    # except Exception as e:
    #     print(e)
    # finally:
    #     sock.close()
        # sock = socket.socket()
        # sock.connect(('127.0.0.1',9999))

def solo():
    '''接收单人聊天信息'''
    while True:
        #解析发送方ID
        sender_size = sock2.recv(3)
        print(sender_size)
        sender_size = int(sender_size.decode().rstrip())
        # print(sender_size)
        recv_size = 0
        sender_data = b''
        while recv_size < sender_size:
            tmp = sock2.recv(sender_size-recv_size)
            if not tmp:
                break
            sender_data += tmp 
            recv_size += len(sender_data)
        print("sender:",sender_data)
        sender_id = sender_data.decode()
        if sender_id not in solo_peoples:
            print("new a object")
            open_new_win(sender_id,sock2,solo_peoples,mainwnd)
            # Thread(target=open_new_win,args=(sender_id,sock2,solo_peoples,mainwnd)).start()
            so = solo_peoples.get(sender_id)
            so.solo_msg()
        else:
            so = solo_peoples.get(sender_id)
            so.solo_msg()
    

def new_sole(event):
    '''创建新的单人聊天窗口'''
    
    #获取鼠标点击对象
    targ = people_list.get(people_list.curselection())
    print("target:",targ)
    #发送目标地址
    targ_len = "{:<3}".format(len(targ.encode())).encode()
    sock2.send(targ_len)
    sock2.send(targ.encode())
    #发送消息
    msg = "系统通知：您的基友正在呼叫你".encode()
    msg_len = "{:<15}".format(len(msg)).encode()
    sock2.send(msg_len)
    sock2.send(msg)
    # open_new_win(targ,sock)
    open_new_win(targ,sock2,solo_peoples,mainwnd)
    # Thread(target=open_new_win,args=(targ,sock2,solo_peoples,mainwnd)).start()
    

def open_new_win(targ,sock2,solo_peoples,mainwnd):
    #打开新窗口
    lock.acquire()
    print('open windows')
    so = Solo(targ,sock2,solo_peoples,mainwnd)
    solo_peoples[targ] = so
    lock.release()
    
    
def show_people_list():
    size = sock.recv(15)
    msg_len = int(size.decode().rstrip())
    recv_size = 0
    people_data = b''
    while recv_size < msg_len:
        tmp = sock.recv(msg_len-recv_size)
        if not tmp:
            break
        people_data += tmp 
        recv_size += len(tmp)
    else:  
        #显示
        # print(people_data.decode())
        people_list.delete(0,tk.END)
        data = people_data.decode().split(',')
        for sc in data:
            # print(sc)
            people_list.insert(tk.END, sc)
    


def show_info():
    size = sock.recv(15)
    msg_len = int(size.decode().rstrip())
    recv_size = 0
    data = b''
    while recv_size < msg_len:
        tmp = sock.recv(msg_len-recv_size)
        if not tmp:
            break
        data += tmp 
        recv_size = len(data)
    else:
        #显示
        #设置接收框为可编辑模式（正常模式）
        chat_record_box.configure(state=tk.NORMAL)
        chat_record_box.insert(tk.END,data.decode() + '\n')
        #设置接收框为不可编辑模式
        chat_record_box.configure(state=tk.DISABLED)
        chat_record_box.see(tk.END)
        
        


#多人聊天端口
sock = socket.socket()
sock.connect(('127.0.0.1',9999))

#单人聊天端口
sock2 = socket.socket()
sock2.connect(('127.0.0.1',9998))

#发送名字
name = "YZK"
Solo.Solo_name = name
name_len = "{:<2}".format(len(name.encode())).encode()
sock2.send(name_len)
sock2.send(name.encode())

mainwnd = tk.Tk()
mainwnd.title("聊骚专用聊天室")
mainwnd.minsize(800,800)

#显示窗口
chat_record_box = tk.Text(mainwnd)
chat_record_box.configure(state=tk.DISABLED,width=70)
chat_record_box.grid(row=0,column=0,pady=10,padx=5)
chat_record_box.configure(state=tk.DISABLED)

#成员列表框
people_list_root = tk.LabelFrame(mainwnd,width=300,height=700,text="在线成员")
people_list_root.grid(row=0,column=1,padx=5,sticky='E',rowspan=2)
people_list = tk.Listbox(people_list_root)
people_list.bind("<Double-Button-1>",new_sole)
people_list.place(x=3,y=5,width=280,height=650)

#发送窗口
chat_msg_box = tk.Text(mainwnd)
chat_msg_box.configure(width=60,height=10)
chat_msg_box.grid(row=1,column=0,sticky='W',padx=5)

#发送按钮
send_msg_btn = tk.Button(mainwnd,text='发送',command=on_send_msg)
send_msg_btn.place(x=560,y=560,width=70,height=80)


Thread(target=recv_msg).start()
Thread(target=solo).start()

mainwnd.mainloop()
sock.close()
sock2.close()

