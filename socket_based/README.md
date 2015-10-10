# socket based solutions

these solutions all send text over a socket from the host reading the log
files to the spark driver running the application.

## basic operation

to begin, the sanity checker can be used to confirm that all portions of
the pipeline are working.

the `socket_logfile_reader` is used to send logs from a machine that is
storing them to a machine that is listening.

the `sock_serve` is used to facilitate the communication between the
logfile reader and the spark application.

the `socket_rdd_sanity_checker` is a pyspark application that will simply
print out each rdd as it is created.

to make this demonstration work, i recommend starting the `sock_serve` first
on the machine that will also run the spark application. then start the
the `rdd_sanity_checker`, and finally start the `logfile_reader`.

the `sock_serve` will wait for the spark app to attach before allowing the
logfile reader to attach.

## individual components

### `sock_serve`

the `sock_serve.py` script is a simple helper to smooth the transaction
between the log file sender and the pyspark listener. this app is currently
very dumb and can be improved.

this should be started before the log sender and the pyspark app. it will
listen for the pyspark app on port 9901 and the log sender on port 9900.

### `socket_logfile_reader`

this application reads from an ever growing log file and sends each line to
the specified host and port.

    $ socket_logfile_reader.py --file ./logfile.txt --host 192.168.0.1 --port 8000

### `socket_rdd_sanity_checker`

this is a simple pyspark application that will read from a text socket and
print the contents of each RDD that is generated. it will attempt to read
information from port 9900 of any interface.

    $ spark-submit --master="local[2]" socket_rdd_sanity_checker.py
