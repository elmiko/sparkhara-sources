import socket
import time

from zaqarclient.queues import client as zaqarclient

conf = {
        'auth_opts': {
            'backend': 'keystone',
            'options': {
                'os_username': 'demo',
                'os_password': 'openstack',
                'os_project_name': 'demo',
                'os_auth_url': 'http://10.0.1.107:5000/v2.0/',
                }
            }
        }

ZAQAR_URL='http://10.0.1.107:8888/'
ZAQAR_VERSION=1.1

def get_client():
    return zaqarclient.Client(ZAQAR_URL, ZAQAR_VERSION, conf=conf)

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
    try:
        client = get_client()
        queue = client.queue('sahara')
        while True:
            messages = queue.pop(count=10)
            for msg in messages:
                print('received {} bytes'.format(len(msg.body)))
                s = send.send(msg.body)
                print('sent {} bytes'.format(s))
            else:
                time.sleep(1)
    finally:
        send.close()

if __name__ == '__main__':
    main()
