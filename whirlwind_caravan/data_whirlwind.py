import argparse
import os
import socket
import time


def accept(port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    return sock.accept()


def ship_it(line, send):
    s = send.send(line)
    print('sent {} bytes'.format(s))


def main():
    parser = argparse.ArgumentParser(
        description='read a file and send its lines to a zaqar queue')
    parser.add_argument('--file', help='the file to read', required=True)
    parser.add_argument('--port', help='the port to send on', type=int)
    parser.add_argument('--tail', help='only send new lines appended to file',
                        action='store_true')
    args = parser.parse_args()

    print('awaiting connection')
    send, send_addr = accept(args.port)
    print('connection from: {}'.format(send_addr))

    logfile = open(args.file, 'r')
    if args.tail:
        logfile.seek(0, os.SEEK_END)
    done = False
    while not done:
        pos1 = logfile.tell()
        l = logfile.readline()
        pos2 = logfile.tell()
        if pos1 != pos2:
            ship_it(l, send)
            print('sent: {}'.format(l))
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()
