#sock serve

the `sock_serve.py` script is a simple helper to smooth the transaction
between the log file sender and the pyspark listener. this app is currently
very dumb and can be improved.

this should be started before the log sender and the pyspark app. it will
listen for the pyspark app on port 9901 and the log sender on port 9900.
