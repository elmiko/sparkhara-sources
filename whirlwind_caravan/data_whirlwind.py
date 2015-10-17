import argparse
import os
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


def main():
    parser = argparse.ArgumentParser(
        description='read a file and send it to the host:port')
    parser.add_argument('--file', help='the file to read', required=True)
    parser.add_argument('--queue', help='the zaqar queue name for messages',
                        required=True)
    parser.add_argument('--tail', help='only send new lines appended to file',
                        action='store_true')
    args = parser.parse_args()

    logfile = open(args.file, 'r')
    if args.tail:
        logfile.seek(0, os.SEEK_END)
    client = get_client()
    queue = client.queue(args.queue)
    done = False
    while not done:
        pos1 = logfile.tell()
        l = logfile.readline()
        pos2 = logfile.tell()
        if pos1 != pos2:
            queue.post({'body': l, 'ttl': 60})
            print('sent: {}'.format(l))
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()
