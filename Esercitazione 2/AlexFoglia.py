import socket
import os.path
import sys
class MyFtpClient:
    def __init__(self,direct):
        if(not os.path.exists(direct)):
            os.mkdir(direct)
        
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.is_conn=False
        self.is_port=False
        self.is_pasv=False
        self.to_quit=False
        self.is_sending=False
        self.type='A'
        self.work_dir=direct
        self.last_code=None
        self.last_message=""
        self.com_log=""
    def isconnected(self):
        return self.is_conn
    def lastcode(self):
        if(not self.is_conn):
            return None
        return int(self.last_code)
    def lastmessage(self):
        return self.last_message
    def log(self):
        return self.com_log
    def connect(self,host,port):
        if self.is_conn:
            raise TypeError()
        try:
            self.sock.connect((host,port))
            self.is_conn=True
            self.com_log=""
            self.receive()
        except Exception as e:
            print str(e)
            self.last_code=None
            self.is_conn=False

    def receive(self):
        ans=""
        primi_quattro=self.sock.recv(4)
        self.last_code=primi_quattro[0]+primi_quattro[1]+primi_quattro[2]
        if(primi_quattro.endswith(" ")):
            ans+=primi_quattro
            while not ans.endswith("\r\n"):
                ans+=self.sock.recv(1)
        else:
            ans+=primi_quattro
            must_finish="\r\n%s "%self.last_code
            while not ans.endswith(must_finish):
                ans+=self.sock.recv(1)
            while not ans.endswith("\r\n"):
                ans+=self.sock.recv(1)
            

        self.last_message=ans
        self.last_code=ans[0]+ans[1]+ans[2]
        self.com_log+="<"+ans+"\r\n"
    def send(self,cmd,doReceive=True):
        if(self.is_conn):
            self.sock.send(cmd)
            self.com_log+=">"+cmd
            if(doReceive):
                try:
                    self.receive()
                except:
                    print "No data is readable now\r\n"
        else:
            raise Exception("Not connected")

    def user(self,user):

        if (not self.is_conn):
            raise Exception("Not connected")
        self.send("USER "+user+"\r\n")
         
        
    
    def password(self,apassword):

        if (not self.is_conn):
            raise Exception("Not connected")
        self.send("PASS "+apassword+"\r\n")
         
    
    def system(self):

        if (not self.is_conn):
            raise Exception("Not connected")        
        self.send("SYST\r\n")
         
    def disconnect(self):
        if (not self.is_conn):
            raise Exception("Not connected")        
        self.send("QUIT\r\n")
        self.sock.close()
        self.is_conn=False
        self.is_pasv=False
        self.is_port=False
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def pwd(self):
        if (not self.is_conn):
            raise Exception("Not connected")
        self.send("PWD\r\n")
         
    def lpwd(self):
        if( not self.is_conn):
            raise Exception("Not connected")
        
        return '"'+ self.work_dir+'"'
    def port(self):

        if (not self.is_conn):
            raise Exception("Not connected")

        self.is_pasv=False
        self.is_port=True
        hostaddr,port=self.sock.getsockname()
        temp_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        temp_socket.bind((hostaddr,0))
        hostaddr,port=temp_socket.getsockname()
        temp_socket.close()
        bytes_ip=hostaddr.split('.')
        hostaddr=""
        for byte in bytes_ip:
            hostaddr+=byte+","

        p1=int(port/256)
        p2=(port%256)
        p1=str(p1)
        p2=str(p2)
        port_command="PORT "+hostaddr+p1+","+p2+"\r\n"
        self.send(port_command)
        if(not self.last_code.startswith("5")):
            self.makesocket(port_command)
    def pasv(self):

        if (not self.is_conn):
            raise Exception("Not connected")

        self.send("PASV\r\n")
        pasv_ans=self.last_message
        if(not pasv_ans.startswith("5")):
            self.is_port=False
            self.is_pasv=True
            first_bracket_index=-1
            last_bracket_index=-1
            for i,char in enumerate(pasv_ans):
                if char=='(':
                    first_bracket_index=i+1
                if char==')':
                    last_bracket_index=i
            in_brackets=pasv_ans[first_bracket_index:last_bracket_index]
            print "Address is: "+in_brackets+"\r\n"
            a1,a2,a3,a4,p1,p2=in_brackets.split(",")
            self.addr_to=a1+"."+a2+"."+a3+"."+a4
            self.port_to= int(p1)*256+int(p2)
        
    def data(self):

        if not self.is_pasv and not self.is_port:
            return None
        elif self.is_pasv:
            return (self.addr_to,self.port_to,True)
        else:
            return (self.addr_in,self.port_in,False)
    def cd(self,ddir):

        if (not self.is_conn):
            raise Exception("Not connected")

        self.send("CWD "+ddir+"\r\n")
         
    def lcd(self,ddir):
        if (not self.is_conn):
            raise Exception("Not connected")
        new_dir=os.path.abspath(os.path.join(self.work_dir,ddir))
        if(not os.path.exists(new_dir)):
            print "Error, local directory does not exists\r\n"
            return
        self.work_dir=new_dir
        print "Now working directory is: "+self.work_dir+"\r\n"
    def list(self,ddir="//"):

        if (not self.is_conn):
            raise Exception("Not connected")

        self.new_file=""
        data=""
        if (not self.is_pasv and not self.is_port):
            raise Exception("No data connection")
        elif(self.is_pasv):
            self.send("LIST -l "+ddir+"\r\n",False) 
            data=self.passiverecv(self.addr_to,self.port_to)
            self.receive()
            self.is_pasv=False
        elif(self.is_port):
            self.send("LIST -l "+ddir+"\r\n",False) 
            data=self.activerecv(self.real_addr_in,self.port_in)
            self.receive()
            self.is_port=False
        self.receive()
        return data
    def cdup(self):

        if (not self.is_conn):
            raise Exception("Not connected")

        self.send("CDUP\r\n")
         
    def lcdup(self):
        if(not self.is_conn):
            raise Exception("Never connected")
        self.lcd("..")
    def ascii(self):

        if (not self.is_conn):
            raise Exception("Not connected")

        self.send("TYPE A\r\n")
        if(not self.last_code.startswith('5')):
            self.type='A'
         
    def binary(self):

        if (not self.is_conn):
            raise Exception("Not connected")
        self.send("TYPE I\r\n")
        if(not self.last_code.startswith("5")):
            self.type='I'
         
    def mode(self):
        if(self.type=='I'):
            return "\"IMAGE\""
        else:
            return "\"ASCII\""
    def get(self,remote,local):

        if (not self.is_conn):
            raise Exception("Not connected")

        if (not self.is_pasv and not self.is_port):
            print "No data connection\r\n"
            raise TypeError()
        cmd="RETR "+remote+"\r\n"
        self.new_file=os.path.join(self.work_dir,local)
        if(self.is_pasv):
            self.sock.settimeout(1)
            self.send(cmd,True)
            if(self.last_code.startswith("5")):
                print "File does not exists\r\n"
                return
            self.sock.settimeout(None)
            self.passiverecv(self.addr_to,self.port_to)
            self.is_pasv=False
        elif(self.is_port):
            self.sock.settimeout(1)
            self.send(cmd,True)
            if(self.last_code.startswith("5")):
                print "File does not exists\r\n"
                return
            self.sock.settimeout(None)
            self.activerecv(self.real_addr_in,self.port_in)
            self.is_pasv=False
        self.receive()
        self.receive()



    def put(self,remote,local):

        if (not self.is_conn):
            raise Exception("Not connected")

        if (not self.is_pasv and not self.is_port):
            raise TypeError()
        cmd="STOR "+remote+"\r\n"
        self.new_file=os.path.join(self.work_dir,local)
        if(not os.path.exists(self.new_file)):
            print "Error, file does not exists\r\n"
            raise TypeError()
        if(self.is_pasv):
            self.send(cmd,False)

            self.passivesend(self.addr_to,self.port_to)
            self.is_pasv=False
        elif(self.is_port):
            self.send(cmd,False)

            self.activesend(self.real_addr_in,self.port_in)
            self.is_port=False
        
        self.receive()
        if(not self.last_code[0]=='5'):
            self.receive()
                       
            
    def passiverecv(self,addr_to,port_to):
        self.is_sending=True
        datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print "Created data socket\r\n"
        datasock.connect((addr_to,port_to))
        line=datasock.recv(1024)
        data=line
        while(line):
            line=datasock.recv(1024)
            data+=line
        try:
            f=open(self.new_file,'w')
            if(self.type=='I'):
                f.close()
                f=open(self.new_file,'wb')
            f.write(data)
            f.close()
        except:
            print "Data weren't saved in any file\r\n"
        datasock.close()
        self.is_pasv=False
        self.is_sending=False
        return data
    def passivesend(self,addr_to,port_to):
        self.is_sending=True
        datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print "Created data socket\r\n"
        datasock.connect((addr_to,port_to))
        f=open(self.new_file,'r')
        if(self.type=='I'):
            f.close()
            f=open(self.new_file,'rb')
        data=f.read()
        f.close()
        datasock.send(data)
        datasock.close()
        self.is_pasv=False
        self.is_sending=False
    def activesend(self,addr_in,port_in):
        self.is_sending=True
        datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print "Created data socket\r\n"
        datasock.bind((addr_in,port_in))
        datasock.listen(50)
        address,client=datasock.accept()
        print "Received a connection from the server: "+str(address)+"\r\n"
        f=open(self.new_file,'r')
        if(self.type=='I'):
            f.close()
            f=open(self.new_file,'rb')
        data=f.read()
        f.close()
        client.send(data)
        datasock.close()
        self.is_port=False
        self.is_sending=False
    def activerecv(self,addr_in,port_in):
        self.is_sending=True
        datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        datasock.bind((addr_in,port_in))
        datasock.listen(50)
        client,address=datasock.accept()
        print "Received a connection from the server: "+str(address)+"\r\n"
        line=client.recv(1024)
        data=line
        while(line):
            line=client.recv(1024)
            data+=line
        try:
            f=open(self.new_file,'w')
            if(self.type=='I'):
                f.close()
                f=open(self.new_file,'wb')
            f.write(data)
            f.close()
        except:
            print "Data weren't saved in any file\r\n"
        datasock.close()
        self.is_port=False
        self.is_sending=False
        return data
    
    def makesocket(self,string):
        cmd,in_brackets=string.split()
        a1,a2,a3,a4,p1,p2=in_brackets.split(",")
        self.addr_in=a1+"."+a2+"."+a3+"."+a4
        self.real_addr_in=self.addr_in
        self.port_in= int(p1)*256+int(p2)
        

    
   
    def esegui(self,stringa):
        string=stringa.lower()
        if(string.startswith("connect ") or string=="connect"):
            try:
                args=string.split()
            except:
                args="connect"
            host=""
            port=""
            if(len(args)==1):
                host=raw_input("to?\r\n")
                if(len (host.split())>1):
                    port=host.split()[1]
                    print "port is: "+port
                else:
                    port=raw_input("port?\r\n")
            elif(len(args)==2):
                host=args[1]
                port=raw_input("port?\r\n")
            else:
                host=args[1]
                port=args[2]
            self.connect(host,int(port))
        elif (string=="isconnected"):
            print self.isconnected()
        elif (string=="lastmessage"):
            print self.lastmessage()
        elif (string=="lastcode"):
            print self.lastcode()
        elif (string=="log"):
            print self.log()
        elif (string.startswith("user ")):
            args=string.split()[1]
            self.user(args)
        elif (string.startswith("pass ")):
            args=string.split()[1]
            self.password(args)
        elif (string=="system"):
            self.system()
        elif (string=="disconnect"):
            self.disconnect()
        elif (string=="pwd"):
            self.pwd()
        elif (string=="lpwd"):
            print self.lpwd()
        elif (string=="port"):
            self.port()
        elif (string=="pasv"):
            self.pasv()
        elif (string=="data"):
            print self.data()
        elif (string.startswith("cd ")):
            self.cd(stringa.split()[1])
        elif (string.startswith("lcd ")):
            self.lcd(stringa.split()[1])
        elif (string=="list"):
            print self.list("")
        elif (string.startswith("list ")):
            print self.list(stringa.split()[1])
        elif (string=="cdup"):
            self.cdup()
        elif (string=="lcdup"):
            self.lcdup()
        elif (string=="ascii"):
            self.ascii()
        elif (string=="binary"):
            self.binary()
        elif (string=="mode"):
            print self.mode()
        elif (string.startswith("get ")):
            parti=stringa.split()
            self.get(parti[1],parti[2])
        elif (string.startswith("put ")):
            parti=stringa.split()
            self.put(parti[1],parti[2])
            
        else:
            self.send(stringa+"\r\n",True)
    def work_cycle(self):
        while True:
            to_invoke=raw_input("\n")
            self.esegui(to_invoke)
            print self.lastmessage()

            

if(__name__=="__main__"):
    while True:
        s=MyFtpClient(raw_input("Insert a local directory"))
        print "FTP Client Started\r\n"
        s.work_cycle()




            
