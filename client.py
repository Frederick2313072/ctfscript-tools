import socket
s=socket.socket()
s.connect(("127.0.0.1",2345))
data = s.recv(1024)
#对传输数据使用encode处理，python3不再支持str类型传输
data = bytes.decode(data)