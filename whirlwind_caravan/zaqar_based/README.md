# zaqar based solutions

the files in this directory are all based on the idea of reading a log file
and sending the lines through the zaqar message queue service to the spark
driver node where it is received and relayed to a spark application. the
spark application then totals the messages send and updates a zaqar queue
with the results oonce every 5 seconds.

## basic operations

1. start the `zaqar_sock_serve.py` on the spark driver node

2. start the `zaqar_total_viewer.py` on a host to display the results

3. start the `zaqar_rdd_sanity_checker.py` on the spark driver node

4. finally, start the `zaqar_logfile_reader.py` and watch the fun!
