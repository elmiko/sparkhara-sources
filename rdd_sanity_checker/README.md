#rdd sanity checker

this is a simple pyspark application that will read from a text socket and
print the contents of each RDD that is generated. it will attempt to read
information from port 9900 of any interface.

    $ spark-submit --master="local[2]" rdd_sanity_checker.py
