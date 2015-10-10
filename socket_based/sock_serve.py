import socket
import time

def accept_9900():
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 9900))
    sock.listen(1)
    return sock.accept()

def accept_9901():
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 9901))
    sock.listen(1)
    return sock.accept()

def main():
    send, send_addr = accept_9901()
    print('connection from: {}'.format(send_addr))
    recv, recv_addr = accept_9900()
    print('connection from: {}'.format(recv_addr))
    try:
        while True:
            r = recv.recv(4096)
            print('received {} bytes'.format(len(r)))
            if len(r) != 0:
                s = send.send(r)
                print('sent {} bytes'.format(s))
            else:
                time.sleep(1)
    finally:
        recv.close()
        send.close()

if __name__ == '__main__':
    main()
