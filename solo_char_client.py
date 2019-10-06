#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import tkinter as tk
from tkinter import messagebox
from threading import Thread,Lock


lock = Lock()


class Solo():
    Solo_name = ''
    def __init__(self,targ ,sock,solo_peoples,mainwnd):
        '''参数说明：目标id，套接字，单人列表，主窗口对象'''
        self.sock = sock
        self.targ = targ
        self.solo_peoples = solo_peoples
     
        #创建新窗口
       
        self.solo_root = tk.Toplevel(mainwnd)
        title =self.targ
        self.solo_root.title("%s" % title)
        self.solo_root.minsize(610,630)

        #显示窗口
        self.solo_record_box = tk.Text(self.solo_root)
        self.solo_record_box.configure(state=tk.DISABLED,width=70)
        self.solo_record_box.grid(row=0,column=0,pady=10,padx=5)

        #发送窗口
        self.solo_msg_box = tk.Text(self.solo_root)
        self.solo_msg_box.configure(width=60,height=10)
        self.solo_msg_box.grid(row=1,column=0,sticky='W',padx=5)

        #发送按钮
        self.send_solo_btn = tk.Button(self.solo_root,text='发送',command=self.on_send_msg)
        self.send_solo_btn.place(x=560,y=480,width=70,height=80)

        #绑定窗口关闭事件
        self.solo_root.protocol("WM_DELETE_WINDOW",self.callback)

       
    def callback(self):
        """处理子窗口关闭事件"""
        del self.solo_peoples[self.targ]
        self.solo_root.destroy()

    def solo_msg(self):
        '''接收消息并显示在接收框内'''
        # lock.acquire()
        #获取消息框对象
        try:
            print("^^^^^^^^^^^^^^^^^^^^^^^^^")
            size = self.sock.recv(15)
            print("msgsize:",size)
            msg_len = int(size.decode().rstrip())
            recv_size = 0
            data = b''
            while recv_size < msg_len:
                tmp = self.sock.recv(msg_len-recv_size)
                if not tmp:
                    break
                data += tmp 
                recv_size += len(tmp)
            else:
                #显示
                self.solo_record_box.configure(state=tk.NORMAL)
                self.solo_record_box.insert("end",data.decode() + '\n')
                self.solo_record_box.configure(state=tk.DISABLED)
                self.solo_record_box.see(tk.END)
        except Exception as e:
            self.solo_record_box.configure(state=tk.NORMAL)
            self.solo_record_box.insert("end","内部错误。。。",'\n')
            self.solo_record_box.insert("en",e,'\n')
            self.solo_record_box.configure(state=tk.DISABLED)
        # lock.release()

    def on_send_msg(self):
        '''发送包头和消息，并将信息显示在接受框内'''
        #获取消息编辑框的消息
        chat_msg = self.solo_msg_box.get(1.0,'end')
        if chat_msg == '\n':
            return
        chat_data = self.Solo_name + ': ' + chat_msg
        chat_data = chat_data.encode()
        data_len = "{:<15}".format(len(chat_data)).encode()
        targ = (self.targ).encode()
        print(targ)
        targ_len = "{:<3}".format(len(targ)).encode()
        try:
            #目标地址
            self.sock.send(targ_len)
            self.sock.send(targ)
            #消息内容
            self.sock.send(data_len + chat_data)
        except:
            tk.messagebox.showerror('网络上天了',"发送失败，请检查网络")
        else:
            #将消息编辑框内的消息删除
            self.solo_msg_box.delete(1.0,'end')
            #设置接收框为可编辑模式（正常模式）
            self.solo_record_box.configure(state=tk.NORMAL)
            #将数据显示在接收框内
            self.solo_record_box.insert("end",chat_data.decode() + '\n')
            #将接收框设置为不可编辑模式
            self.solo_record_box.configure(state=tk.DISABLED)
            #焦点显示在最后
            self.solo_record_box.see(tk.END)



