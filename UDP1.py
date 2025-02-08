import socket
target_host="127.0.0.1"
target-port = 8081
#UDP是无连接的，不需要调用connect
# create a socket objectIPV4地址，UDP协议
client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  
#send some data，发送字节串b"AABBBCCC"
client.sendto(b"AAABBBCCC",(target_host,target_port))   
#receive some data，最多接受4096字节
data,addr = client.recvfrom(4096)

print(data.decode())
client.close()