#!/bin/python

import argparse
import json
import socket
import time

import kombu


def accept(port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    return sock.accept()


def main():
    parser = argparse.ArgumentParser(
        description='read messages from an amqp broker and send them to a port')
    parser.add_argument('--port', help='the port to send on (default: 1984)',
                        type=int,
                        default=1984)
    parser.add_argument('--url', help='the amqp broker url',
                        required=True)
    parser.add_argument('--queue', help='the amqp queue name to subscribe '
                        '(default: sparkhara)',
                        default='sparkhara')
    args = parser.parse_args()

    while True:
        send, send_addr = accept(args.port)
        print('connection from: {}'.format(send_addr))
        try:
            conn = kombu.Connection(args.url)
            queue = conn.SimpleQueue(args.queue)
            while True:
                try:
                    message = queue.get(block=False, timeout=1)
                except kombu.simple.SimpleQueue.Empty:
                    time.sleep(1)
                    continue
                print('Received message:')
                print(message.payload)
                s = send.send(json.dumps(message.payload))
                s += send.send('\n')
                print('sent {} bytes'.format(s))
                message.ack()
        except socket.error:
            pass
        finally:
            send.close()
            pass

if __name__ == '__main__':
    main()
