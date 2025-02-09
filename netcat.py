import argparse
import socket
import shlex        
import subprocess   
import sys
import textwrap 
import threading
#接受一条命令并执行，将结果作为一段字符串返回
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()
class Netcat:
    def __init__(self,args,buffer=None):#初始化一个NetCat对象
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket()#创建一个socket对象
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def run(self):#如果是接收方，就监听端口，如果是发送方，就执行send函数
        if self.args.listen:
            self.listen()
        else:
            self.send()
    def send(self):
        self.socket.connect((self.args.target,self.args.port))#连接到target和port
        if self.buffer:
            self.socket.send(self.buffer)#如果缓冲区有数据的话，就先把这些数据发过去
        try:#直接用ctrl+c退出程序
            while True:#创建一个大循环，一轮一轮接受target返回的数据
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break#大循环里的小循环，用来读取socket本轮返回的数据，如果数据目前已经读到头就推出小循环
                if response:#如果读出了什么，就输出到屏幕上，并暂停，等待用户输入新的内容，再把新的内容发给target，接着开始下一轮的大循环
                    print(response)
                    buffer = input('')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:#按下ctrl+c组合键触发KeyboardInterrupt中断循环，关闭socket对象
            print('User terminated.')
            self.socket.close()
            sys.exit()
    def listen(self):
        self.socket.bind((self.args.target,self.args.port))#绑定到target和port
        self.socket.listen(5)#开始监听
        while True:
            client_socket, _ = self.socket.accept()#接受连接
            client_thread = threading.Thread(target=self.handle,args=(client_socket,))
            client_thread.start()
    def handle(self,client_socket):
        if self.args.execute:#如果要执行命令，handle函数会把命令传递给execute函数，然后把输出结果通过socket发回去
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:#如果要上传文件，就建立一个循环来接受socket传过来的数据，然后把数据写到参数指定的文件里
            file_buffer = b''
            while True:
                data = client_socket.recv(1024)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload,'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        elif self.args.command:#如果要创建一个命令shell，就建立一个循环来接受socket传过来的数据，然后把数据传递给execute函数，然后把输出结果通过socket发回去
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(1024)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:#帮助信息
            netcat.py -t 127.0.0.1 -p 5555 -l -c # command shell
            netcat.py -t 127.0.0.1 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 127.0.0.1 -p 5555 -l -e="cat /etc/passwd" # execute command
            echo 'ABC' | ./netcat.py -t 127.0.0.1 -p 135 # echo text to server port 135
            netcat.py -t 127.0.0.1 -p 5555 # connect to server
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')#用来控制程序的行为
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='127.0.0.1', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    if args.listen:#如果确定程序要进行监听，在缓冲区里填上空白数据，把空白缓冲区传给NetCat对象。反之把stdin里的数据通过缓冲区传进去
        buffer = ''
    else:
        buffer = sys.stdin.read()
    