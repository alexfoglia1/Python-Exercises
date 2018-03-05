'''
Created on 30/ott/2015

@author: Alex Foglia
'''
import socket
import threading
import os
import platform
class MyFtpServer:
    
    def __init__(self,u_table,port):

        self.portA=port
        self.ascolto = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.transfer = None
        self.server_address= "192.168.0.2"
        self.users=u_table
        self.type='A T'
        self.THE_NEW_LINE="\r\n"
        self.is_pasv=False
        self.is_auth=False
        self.is_port=False
        self.received_quit=False
        self.system_name=platform.system()
        self.system_type=platform.release()
        self.the_code="530"
        self.RETR_OR_LIST_COMMAND=""
        self.is_sending=False
    
    def tellNewConn(self,address):
        print "Received a connection from:\r\n"
        print address
        print "\r\n"    
                     
    def removeCRLF(self):
        line_read=""
        last_line_read=""
        while(not line_read.endswith("\r\n")):
            last_line_read=line_read
            line_read=self.primary_client.recv(1024)
            if(line_read==""):
                break
            
            
        read_data=last_line_read+line_read
        if(read_data.endswith("\r\n")):
            read_data=read_data.split("\r\n")
            read_data=read_data[0]
        elif(read_data.endswith("\n")):
            read_data=read_data.split("\n")
            read_data=read_data[0]
        elif (read_data.endswith("\r")):
            read_data=read_data.split("\r")
            read_data=read_data[0]
        return read_data
    def pass_afterLogin(self):
        self.primary_client.send("230 PASS OK\r\n")                    
    def user_afterLogin(self,command):
        cmd,recv_user=command.split()
        if(recv_user==self.user_in):
            self.primary_client.send("331 USER OK\r\n")
        else:
            self.primary_client.send("530 Wrong username: "+recv_user+"\r\n")
    def containsAtLeast(self,where,times,what):
        i=0
        for char in where:
            if char==what:
                i=i+1
        if(i<times):
            return False
        else:
            return True
    
    def TYPE(self,command):
        if(command=="TYPE A"):
            self.type='A'
            self.THE_NEW_LINE="\n"
            self.primary_client.send("200 OK TYPE A\r\n")
        elif(command=="TYPE A N"):
            self.type='A N'
            self.THE_NEW_LINE="\n"
            self.primary_client.send("200 OK TYPE A N\r\n")
        elif(command=="TYPE A T"):
            self.type='A T'
            self.THE_NEW_LINE="\r\n"
            self.primary_client.send("200 OK TYPE A T\r\n")
        elif(command=="TYPE A C"):
            self.type='A C'
            self.THE_NEW_LINE=" "
            self.primary_client.send("200 OK TYPE A C\r\n")
        elif(command=="TYPE E"):
            self.type='E'
            self.THE_NEW_LINE="\n"
            self.primary_client.send("200 OK TYPE E\r\n")
        elif(command=="TYPE E N"):
            self.THE_NEW_LINE="\n"
            self.type='E N'
            self.primary_client.send("200 OK TYPE E N\r\n")
        elif(command=="TYPE E T"):
            self.THE_NEW_LINE="\n"
            self.type='E T'
            self.primary_client.send("200 OK TYPE E T\r\n")
        elif(command=="TYPE E C"):
            self.THE_NEW_LINE=" "
            self.type='E C'
            self.primary_client.send("200 OK TYPE E C\r\n")
        elif(command=="TYPE I"):
            self.THE_NEW_LINE="\n"
            self.type='I'
            self.primary_client.send("200 OK TYPE I\r\n")
        elif(command.startswith("TYPE L")):
            try:
                a,b,c=command.split()
                d=int(c)
                if(d<1 or d>8):
                    raise Exception
                else:
                    self.type="L "+c
            except:
                self.primary_client("502 Wrong syntax\r\n")
                return
            self.primary_client.send("200 OK "+command+"\r\n")
            self.THE_NEW_LINE="\n"
        else:
            self.primary_client.send("502 Wrong syntax\r\n")
              
    
    def c_interpreter(self,clisock):
        
        read_data=self.removeCRLF()
        
        print "I Received:\r\n"
        print read_data+"\r\n"
        
       
        if(read_data.startswith('USER')):
            if(self.is_auth):
                self.user_afterLogin(read_data)
                return
            cmd,recv_user=read_data.split()
            clisock.send("331 Welcome "+recv_user+", please insert password\r\n")
            self.the_code="331"
            self.user_in=recv_user
            return
        if(read_data.startswith('PASS')):
            if(self.is_auth):
                self.pass_afterLogin()
                return
            cmd,recv_pass=read_data.split()
            if(self.users.has_key(self.user_in)):
                if(self.users[self.user_in][0]==recv_pass):
                    clisock.send("230 You're successfully logged in\r\n")
                    self.act_dir=self.users[self.user_in][1]
                    if not os.path.exists(self.act_dir):
                        os.mkdir(self.act_dir)
                    self.is_auth=True
                else:
                    clisock.send("530 Not authenticated, wrong password\r\n")
                return
            else:
                clisock.send("530 Not authenticated, wrong username\r\n")
                return
        if (read_data== 'QUIT'):
            clisock.send("221 Service is closing your connection\r\n")
            if(self.is_sending):
                self.running_thread.join(10)
                
            self.received_quit=True
            clisock.close()
            return
                
        if(self.is_auth):
            if(read_data=='SYST'):
                to_send='215 '+self.system_name+" "+self.system_type+"\r\n"
                clisock.send(to_send)
            elif (read_data == 'FEAT'):
                to_send='211 \r\n'
                clisock.send(to_send)
            elif (read_data == 'PWD'):
                to_send="257 "+self.act_dir+"\r\n"
                clisock.send(to_send)
            elif (read_data== 'NOOP'):
                clisock.send("200 OK\r\n")
            
            elif (read_data.startswith("TYPE")):
                self.TYPE(read_data)
            elif (read_data.startswith("SIZE")):
                parti=read_data.split()
                dir_target=parti[1]
                if(os.path.exists(dir_target)):
                    stat=os.stat(dir_target)
                    the_size=stat.st_size
                    to_send="213 "+str(the_size)+"\r\n"
                    print to_send
                    clisock.send(to_send)
                else:
                    clisock.send("500 File does not exists\r\n")
            elif (read_data.startswith("CWD")):
                if(read_data=="CWD" or read_data=="CWD "):
                    clisock.send("250 OK CWD\r\n")
                    return
                cwd,dir_target=read_data.split()
                if(dir_target.startswith("..")):
                    clisock.send("550 CWD .. Not allowed, use CDUP instead\r\n")
                    return
                base_dir=self.users[self.user_in][1]
                print "base_dir is "+base_dir
                print "dir_target is "+dir_target
                if(dir_target.startswith(base_dir)):
                    if(os.path.exists(dir_target)):
                        self.act_dir=dir_target
                        clisock.send("250 Succesfully changed work directory: "+self.act_dir+"\r\n")
                    else:
                        clisock.send("550 Error "+dir_target+" does not exists\r\n")
                else:
                        dir_target=self.act_dir+"/"+dir_target
                        if (os.path.exists(dir_target)):
                            self.act_dir=dir_target
                            clisock.send("250 Succesfully changed work directory: "+self.act_dir+"\r\n")
                        else:
                            clisock.send("550 Error "+dir_target+" does not exists\r\n")
                            
                        
            elif (read_data== 'CDUP'):
                if(self.act_dir==self.users[self.user_in][1]):
                    to_send="550 Cannot go further up\r\n"
                    clisock.send(to_send)
                else:   
                    parts=self.act_dir.split("/")
                    self.act_dir=""
                    length=len(parts)
                    for string in parts:
                        if string != '' and string != parts[length-1]:
                            self.act_dir+=("/"+string)
                    to_send="257 Changed work directory: "+self.act_dir+"\r\n"
                    clisock.send(to_send)
            elif (read_data=="PASV"):
                self.PASV()
            elif (read_data.startswith("PORT")):
                self.PORT(read_data)
            elif (read_data.startswith("LIST")):
                if(read_data=="LIST -l"):
                    read_data="LIST"
                if(self.is_sending):
                    clisock.send("425 Can't open data connection: another transfer is waiting to terminate\r\n")
                    return
                self.RETR_OR_LIST_COMMAND=read_data
                self.LIST()
            elif (read_data.startswith("RETR")):
                if(self.is_sending):
                    clisock.send("425 Can't open data connection: another transfer is waiting to terminate\r\n")
                    return
                self.RETR_OR_LIST_COMMAND=read_data
                self.RETR()                 
            else:
                clisock.send("502 '"+read_data+"' Not Implemented\r\n")
        else:
            clisock.send(self.the_code+" Not Authenticated\r\n")
    def PASV(self):
        
        self.transfer=socket.socket(socket.AF_INET,socket.SOCK_STREAM)   
        self.is_pasv=True
        self.is_port=False
        self.transfer.bind((self.server_address,0))
        self.transfer.listen(1)
        addressForPrinting,portForPrinting=self.transfer.getsockname()
        print "Enabled to listen on "+str(addressForPrinting)+" : "+str(portForPrinting)+"\r\n"
        to_send="227 Entering passive mode ("
        parti=addressForPrinting.split('.')
        p1=int(portForPrinting/256)
        p2=int(portForPrinting%256)
        for number in parti:
            to_send+=(number+",")
        to_send+=str(p1)+","
        to_send+=str(p2)+")\r\n"
        self.primary_client.send(to_send)
    
    def RETR(self):
        th=threading.Thread(target=self.TRETR,args=())
        th.setDaemon(True)
        self.running_thread=th
        th.start()
    
    def TRETR(self):
        self.is_sending=True
        print "Start downloading procedure\r\n"
        
        if(self.is_pasv==False and self.is_port==False ):
            self.primary_client.send("550 Error: you need to use PASV or PORT first\r\n")
            self.is_sending=False
            return
        fname=self.RETR_OR_LIST_COMMAND.split()
        fname=fname[1]
        filename=fname
        if not fname.startswith(self.users[self.user_in][1]):
            if(fname.startswith("/")):
                filename=self.act_dir+fname
            else:
                filename=(self.act_dir+"/"+fname)
        if not os.path.exists(filename):
            self.primary_client.send("550 Error: file "+filename+" does not exist\r\n")
            self.is_sending=False
            return
        target_file=open(filename,'r')
        self.primary_client.send('150 RETR OK Start sending file '+filename+"\r\n")
        print "Downloading file "+filename+"\r\n"
        flag=self.enableDataTransfer()
        if not flag:
            self.is_sending=False
            return
        data= target_file.read(1024)
        the_lines=""
        while data:
            the_lines+=(data+self.THE_NEW_LINE)
            data=target_file.read(1024)
        if(self.type!='I'):
            self.secondary_client.send(the_lines)
        else:
            int_list=list()
            for char in the_lines:
                int_list.append(ord(char))
            bin_lines=bytearray(int_list)
            self.secondary_client.send(bin_lines)
            
        print '\r\nDownloaded successfully terminated\r\n'
        target_file.close()
        self.closeDataTransfer()
        print "Data transfer closed\r\n"
        self.primary_client.send('226 Transfer of '+filename+' successfully completed \r\n')
        print "Downloading procedure terminated\r\n"
        self.is_sending=False 
    def checkListItem(self,the_mode,to_check):
        return_to=''
        for i in range(9):
            a= the_mode>>(8-i)
            b= a&1
            b= b and to_check[i] or '-'
            return_to+=b
        return return_to
    def fromFileToLS(self,filename):
        import time
        bn=os.path.basename(filename)
        the_stat=os.stat(filename)
        the_mode=the_stat.st_mode
        the_time=the_stat.st_mtime
        the_size=the_stat.st_size
        string_mode=self.checkListItem(the_mode, 'rwxrwxrwx')      
        flag=(os.path.isdir(filename)) and 'd' or '-'
        the_list_element=flag+string_mode
        time_to_return=time.strftime(" %b %d %H:%M ", time.gmtime(the_time))
        the_list_element+="1 user group "+str(the_size)+time_to_return+bn
        return the_list_element
    def LIST(self):

        th=threading.Thread(target=self.TLIST,args=())
        th.setDaemon(True)
        self.running_thread=th
        th.start()
          
    def TLIST(self):
        
        self.is_sending=True
        if(self.is_pasv==False and self.is_port==False ):
            self.primary_client.send("550 Error: you need to use PASV or PORT first\r\n")
            self.is_sending=False
            return
        print "Retrieveng list to send to the client\r\n"
        parti=self.RETR_OR_LIST_COMMAND.split()
        dir_target=os.path.join(self.act_dir,parti[2])
        if(not os.path.exists(dir_target)):
            self.primary_client.send("550 Error: directory "+dir_target+" does not exist\r\n")
            self.is_sending=False
            return
        
        print "Start sending LIST of: "+dir_target+"\r\n"    
        self.primary_client.send("150 LIST OK - Start sending list of "+dir_target+"\r\n")
        print "Now i'm starting data transfer\r\n"
        
        flag= self.enableDataTransfer()
        if not flag:
            self.is_sending=False
            return
        print "Sending list elements\r\n"
        #---NOW I CAN SEND DATA TO CLIENT---#
        try:
            list_res=""
            for dire in os.listdir(dir_target):
                appoggio=(self.fromFileToLS(os.path.join(dir_target,dire)))
                list_res+=(appoggio+self.THE_NEW_LINE)
            self.secondary_client.send(list_res)
        except:
            self.closeDataTransfer()
            self.primary_client.send('550 Cannot open '+dir_target+'ou have no access to it.\r\n')
            self.is_sending=False
            return
        #---NOW I HAVE TO CLOSE DATA CONNECTION---#
        print "Sent all list elements\r\n"
        self.closeDataTransfer()
        print "Data connection is closed\r\n"
        self.primary_client.send('226 Directory contents were successfully sent\r\n')
        print "All ok\r\n"
        self.is_sending=False 
    def PORT(self,address):
        self.is_port=True
        self.is_pasv=False
        if(len(address.split())!=2):
            self.primary_client.send("500 Missing values: type PORT a1,a2,a3,a4,p1,p2\r\n")
            return
        ADDRESS=address.split()
        if(len(ADDRESS[1].split(','))!=6):
            self.primary_client.send("500 Syntax error on parameters\r\n")
            return
        a1,a2,a3,a4,p1,p2=ADDRESS[1].split(',')
        try:
            A1=int(a1)
            A2=int(a2)
            A3=int(a3)
            A4=int(a4)
            P1=int(p1)
            P2=int(p2)
            theport=P1*256+P2
            max_port=65535
            flag = theport <=0 or theport > max_port
        except:
            self.primary_client.send("500 Invalid literal\r\n")
            return
        if ((A1<0 or A1>255) or (A2<0 or A2>255) or (A3<0 or A3>255 ) or (A4<0 or A4>255 ) or flag ):
            self.primary_client.send("500 Wrong values\r\n")
            return
        self.connect_to=a1+"."+a2+"."+a3+"."+a4
        self.port_to_connect=P1*256+P2
        self.transfer=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.primary_client.send("200 PORT OK\r\n")
    
    def enableDataTransfer(self):
        if(self.is_pasv):
            print1,print2=self.transfer.getsockname()
            print "Waiting for a data connection at "+str(print1)+" : "+str(print2)+"\r\n"
            self.secondary_client,useless=self.transfer.accept()
            return True
        else:
            print "Connecting to "+str(self.connect_to)+":"+str(self.port_to_connect)+"\r\n"
            try:
                self.transfer.connect((self.connect_to,self.port_to_connect))
                self.secondary_client=self.transfer
                print "Connection ok\r\n"
                return True
            except:
                print "Connection not ok\r\n"
                self.primary_client.send("425 Server can't connect to specified hostname: "+self.connect_to+":"+str(self.port_to_connect)+"\n500 Check if the host is ready or try to resend PORT\r\n")
                return False
    def closeDataTransfer(self):
        self.secondary_client.close()
        if self.is_pasv:
            self.transfer.close()
        self.is_pasv=False
        self.is_port=False
        
    def c_thread(self,lst):
        self.ascolto.bind((self.server_address,self.portA))
        self.ascolto.listen(lst) 
        while True:
            self.is_pasv=False
            self.is_auth=False
            self.is_port=False
            self.is_sending=False
            self.received_quit=False
            self.the_code="550"
            self.type='A T'
            print "Listening for clients on "+str(self.server_address)+" : "+str(self.portA)+"\r\n"
            self.primary_client,self.primary_address=self.ascolto.accept()
            self.tellNewConn(self.primary_address)
            self.primary_client.send("220 FTP Server Ready\r\n")
            while not self.received_quit:
                try:
                    self.c_interpreter(self.primary_client)
                except Exception as e:
                    print e
                    print "Session must be terminated\r\n"
                    if(self.is_sending):
                        self.running_thread.join(10)
                    break   
                
                
                    
    def start(self):
        self.ctrl=threading.Thread(target=self.c_thread, args=(1,))
        self.ctrl.start()


ftpserver=MyFtpServer({'user2': ('pwd2', '/tmp/home2'), 'user1': ('pwd1', '/tmp/home1'), 'root': ('root','/tmp')},1200)
ftpserver.start()


    
    
    
