#!/bin/python
''' rando whirlwind

this app will create a connection for the caravan master to connect, it
well then begin sending random messages to the master.

'''
import argparse
import json
import random
import socket
import time
import uuid


def accept(port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    return sock.accept()


class RandoMessage(object):
    '''a helper class to generate random messages

    this class will create a list of service names and choose one at random
    from the list for each new message.

    '''
    def __init__(self, services):
        self.services = ['service{}'.format(i+1) for i in range(services)]

    def new(self):
        '''create a new message'''
        message = {self.services[random.randint(0, len(self.services)-1)]:
                   'a randomg log message, collect them all! {}'.
                   format(uuid.uuid4().hex)}
        return json.dumps(message)


def main():
    parser = argparse.ArgumentParser(
        description='send some random stuff to a caravan master')
    parser.add_argument('--port', help='the port to send on (default: 1984)',
                        type=int,
                        default=1984)
    parser.add_argument('--services', help='the number of services to send '
                        '(default: 1)',
                        type=int,
                        default=1)
    args = parser.parse_args()

    while True:
        send, send_addr = accept(args.port)
        print('connection from: {}'.format(send_addr))
        try:
            message = RandoMessage(args.services)
            while True:
                for i in range(random.randint(1 * args.services,
                                              3 * args.services)):
                    s = send.send(message.new() + '\n')
                    print('sent {} bytes'.format(s))
                time.sleep(1)
        except socket.error:
            pass
        finally:
            send.close()
            pass

if __name__ == '__main__':
    main()
