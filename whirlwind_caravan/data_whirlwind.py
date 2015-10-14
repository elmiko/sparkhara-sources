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

ZAQAR_URL='http://10.0.1.107:8888/'
ZAQAR_VERSION=1.1

def get_client():
    return zaqarclient.Client(ZAQAR_URL, ZAQAR_VERSION, conf=conf)

def main():
    parser = argparse.ArgumentParser(
        description='read a file and send it to the host:port')
    parser.add_argument('--file', help='the file to read', required=True)
    parser.add_argument('--queue', help='the zaqar queue name for messages',
                        required=True)
    args = parser.parse_args()

    f = open(args.file, 'r')
    done = False

    client = get_client()
    queue = client.queue(args.queue)
    while not done:
        pos1 = f.tell()
        l = f.readline()
        pos2 = f.tell()
        if pos1 != pos2:
            queue.post({'body': l, 'ttl': 60})
            print('sent: {}'.format(l))
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()
