#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import tkinter as tk
import socket
from tkinter import messagebox
from threading import Thread

#定长包头（15B）+ 变长聊天记录（格式：昵称:聊天内容）

def on_send_msg():
    '''发送包头和消息，并将信息显示在接受框内'''
    name = "  "
    #获取消息编辑框的消息
    chat_msg = chat_msg_box.get(1.0,'end')
    if chat_msg == '\n':
        return
    chat_data = name + ': ' + chat_msg
    chat_data = chat_data.encode()
    data_len = "{:<15}".format(len(chat_data)).encode()
    try:
        sock.send(data_len + chat_data)
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

def recv_msg():
    '''接收消息并显示在接收框内'''
    global sock
    try:
        while True:
            header = sock.recv(15)
            if not header:
                break
            msg_len = int(header.decode().rstrip())
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
                chat_record_box.configure(state=tk.NORMAL)
                chat_record_box.insert("end",data.decode() + '\n')
                chat_record_box.configure(state=tk.DISABLED)
                continue
            break

    finally:
        sock.close()
        sock = socket.socket()
        sock.connect(('itmojun.com',9999))


sock = socket.socket()
sock.connect(('itmojun.com',9999))

mainwnd = tk.Tk()
mainwnd.title("聊骚专用聊天室")
mainwnd.minsize(800,800)

chat_record_box = tk.Text(mainwnd)
chat_record_box.configure(state=tk.DISABLED)
chat_record_box.pack(pady=10,padx=20)

chat_msg_box = tk.Text(mainwnd)
chat_msg_box.configure(width=60,height=10)
chat_msg_box.pack(side=tk.LEFT,pady=10,padx=20)

send_msg_btn = tk.Button(mainwnd,text='发送',command=on_send_msg)
send_msg_btn.pack(side=tk.RIGHT,pady=10,padx=20,ipadx=15,ipady=15)

Thread(target=recv_msg).start()

mainwnd.mainloop()

sock.close()


















