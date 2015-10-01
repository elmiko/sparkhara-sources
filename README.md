# sparkhara-sources

source files associated with the sparkhara presentation

## sanity check

to begin, the sanity checker can be used to confirm that all portions of
the pipeline are working.

the `logfile_reader` is used to send logs from a machine that is storing
them to a machine that is listening.

the `sock_serve` is used to facilitate the communication between the
logfile reader and the spark application.

the `rdd_sanity_checker` is a pyspark application that will simply print out
each rdd as it is created.

to make this demonstration work, i recommend starting the `sock_serve` first
on the machine that will also run the spark application. then start the
the `rdd_sanity_checker`, and finally start the `logfile_reader`.

the `sock_serve` will wait for the spark app to attach before allowing the
logfile reader to attach.
