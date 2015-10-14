import argparse
import socket
import time


def main():
    parser = argparse.ArgumentParser(
        description='read a file and send it to the host:port')
    parser.add_argument('--file', help='the file to read', required=True)
    parser.add_argument('--host', help='the host ip of the listener',
                        required=True)
    parser.add_argument('--port', help='the host port of the listener',
                        type=int, required=True)
    args = parser.parse_args()

    f = open(args.file, 'r')
    done = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((args.host, args.port))
        while not done:
            pos1 = f.tell()
            l = f.readline()
            pos2 = f.tell()
            if pos1 != pos2:
                sock.sendall(l)
                print('sent: {}'.format(l))
            else:
                time.sleep(1)
    finally:
        sock.close()

if __name__ == '__main__':
    main()
