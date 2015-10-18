import argparse
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

ZAQAR_URL = 'http://10.0.1.107:8888/'
ZAQAR_VERSION = 1.1


def get_client():
    return zaqarclient.Client(ZAQAR_URL, ZAQAR_VERSION, conf=conf)


def accept(port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    return sock.accept()


def main():
    parser = argparse.ArgumentParser(
        description='read messages from a zaqar queue and send them to a port')
    parser.add_argument('--port', help='the port to send on', required=True,
                        type=int)
    parser.add_argument('--queue', help='the zaqar queue name for messages',
                        required=True)
    args = parser.parse_args()

    send, send_addr = accept(args.port)
    print('connection from: {}'.format(send_addr))
    try:
        client = get_client()
        queue = client.queue(args.queue)
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
