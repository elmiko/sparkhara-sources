whirlwind caravan tools
=======================

this directory contains tools to aid in testing and debugging the whirlwind
caravan suite.

ghost whirlwind
---------------

this application can replay a log file and send the output to a socket. this
is useful in cases where the data_whirlwind is not being used. it will
read a log file and send it log lines to a socket, if the log file is
formatted properly it will do this while preserving time delays between the
logs. for more information see the `ghost_whirlwind.py` file.
