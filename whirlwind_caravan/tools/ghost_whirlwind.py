#!/bin/env python
'''
ghost whirlwind

this application will attempt to parse a log file and play back the log
messages as they occurred. meaning that it will read the date stamp from each
log line and attempt to calculcate the time difference and sleep between
sends. it will send the lines to a port specified on the command line.

this is intended to help feed the caravan master in cases where no
queue is present, or no services are available to provide live logs.

'''
import argparse
import collections
import datetime
import re
import os
import socket
import time


LogEntry = collections.namedtuple('LogEntry', ['datestamp', 'body'])


def accept(port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    return sock.accept()


def process_log_entry(logfile, filesize):
    '''
    attempt to read log lines and group them

    this will read the next line in the log file, if it does not begin
    with a recognized date stamp (YYYY-MM-DD HH:MM:SS.mmm) it will
    return None. if the line does begin with a recognized date stamp,
    the line will be added to the current log entry and the next line
    will be inspected for a date stamp. if the next line does not
    contain a date stamp, it will appended to the current entry. if the
    next line does contain a date stamp, the file position will be set
    to the start of that line and the function will return the current
    entry.

    '''
    def datestamp_match(line):
        DATESTAMP_RE = '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}'
        datestamp = line[:23]
        return re.match(DATESTAMP_RE, datestamp)

    nextline = logfile.readline()

    match = datestamp_match(nextline)
    if match is None:
        return None

    datestamp = datetime.datetime.strptime(match.group(),
                                           '%Y-%m-%d %H:%M:%S.%f')

    entry = nextline
    done_peeking = False
    while not done_peeking:
        saved_pos = logfile.tell()
        if saved_pos == filesize:
            done_peeking = True
            continue
        nextline = logfile.readline()
        if datestamp_match(nextline) is None:
            entry += nextline
        else:
            logfile.seek(saved_pos)
            done_peeking = True
    return LogEntry(datestamp, entry)


def replace_newlines(logentries, separator='::newline::'):
    '''
    replace the newlines with a separator

    to reduce the possibility of logs getting split when sending over a
    socket, the newlines are replaced with a separator.

    '''
    for i, entry in enumerate(logentries):
        logentries[i] = LogEntry(entry.datestamp,
                                 entry.body.replace('\n', separator))


def ship_it(logentries, send):
    '''
    ship the log entries somewhere

    '''
    print('shipping {} entries'.format(len(logentries)))
    for entry in logentries:
        s = send.send(entry.body)
        print('sent {} bytes from {} entries'.format(s, len(logentries)))


def main():
    parser = argparse.ArgumentParser(
        description='read a log file and send its lines to a socket')
    parser.add_argument('--file', help='the file to read', required=True)
    parser.add_argument('--port', help='the port to send on', required=True,
                        type=int)
    args = parser.parse_args()

    send, send_addr = accept(args.port)
    print('connection from: {}'.format(send_addr))

    logfile = open(args.file, 'r')
    logfile.seek(0, os.SEEK_END)
    lfsize = logfile.tell()
    logfile.seek(0)

    logentries = []
    badentries = 0
    shippedentries = 0
    while logfile.tell() != lfsize:
        logentry = process_log_entry(logfile, lfsize)
        previous_datestamp = (logentry.datestamp if len(logentries) == 0
                              else logentries[-1].datestamp)
        datestamp_delta = logentry.datestamp - previous_datestamp
        if datestamp_delta.total_seconds() != 0:
            replace_newlines(logentries)
            ship_it(logentries)
            shippedentries += len(logentries)
            logentries = []
            time.sleep(datestamp_delta.total_seconds())
        if logentry is not None:
            logentries.append(logentry)
        else:
            badentries += 1

    print('shipped {} valid entries'.format(shippedentries))
    print('found {} bad entries'.format(badentries))


if __name__ == '__main__':
    main()
