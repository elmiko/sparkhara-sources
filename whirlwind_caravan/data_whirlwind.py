import argparse
import os
import time

import kombu


def main():
    parser = argparse.ArgumentParser(
        description='read a file and send its lines to an amqp broker')
    parser.add_argument('--file', help='the file to read', required=True)
    parser.add_argument('--url', help='the amqp broker url',
                        required=True)
    parser.add_argument('--name', help='the service name of the log',
                        required=True)
    parser.add_argument('--tail', help='only send new lines appended to file',
                        action='store_true')
    args = parser.parse_args()

    logfile = open(args.file, 'r')
    if args.tail:
        logfile.seek(0, os.SEEK_END)

    conn = kombu.Connection(args.url)
    queue = conn.SimpleQueue('sparkhara')

    done = False
    while not done:
        pos1 = logfile.tell()
        l = logfile.readline()
        pos2 = logfile.tell()
        if pos1 != pos2:
            message = {args.name: l}
            queue.put(message)
            print('sent: {}'.format(message))
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()
