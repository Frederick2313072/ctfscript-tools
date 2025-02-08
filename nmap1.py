import nmap
target = "192.168.157.133"
port="80"
nm = nmap.PortScanner()
nm.scan(target, port)
for host in nm.all_host():
    print("Host:{0} ({1})".format(host, nm[host].hostname()))
    print("State:{0}".format(nm[host].state()))
    for proto in nm[host].all_protocols():
        print("Protocol:{0}".format(proto))
        lport = nm[host][proto].keys()
        lport.sort()
        for port in lport:
            print("port:{0}\tstate:{1}".format(port, nm[host][proto][port]["state"]))