import socket
s=socket.socket()
s.bind(("127.0.0.1",2345))
s.listen(5)
string=""
while True:
    conn,address=s.accept()
    print(f"Connection from {address}")
    conn.send(string,encoding="utf-8")
    conn.send(string.encode())
    conn.close()
