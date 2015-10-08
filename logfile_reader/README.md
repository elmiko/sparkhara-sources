#log file reader


## socket_logfile_reader

this application reads from an ever growing log file and sends each line to
the specified host and port.

    $ socket_logfile_reader.py --file ./logfile.txt --host 192.168.0.1 --port 8000
