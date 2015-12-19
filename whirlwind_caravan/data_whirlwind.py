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
    parser.add_argument('--queue', help='the amqp queue name to publish on '
                        '(default: sparkhara)',
                        default='sparkhara')
    args = parser.parse_args()

    logfile = open(args.file, 'r')
    if args.tail:
        logfile.seek(0, os.SEEK_END)

    conn = kombu.Connection(args.url)
    producer = kombu.Producer(conn)

    done = False
    while not done:
        pos1 = logfile.tell()
        l = logfile.readline()
        pos2 = logfile.tell()
        if pos1 != pos2:
            message = {args.name: l}
            producer.publish(message, routing_key=args.queue, expiration=60)
            print('sent: {}'.format(message))
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()
