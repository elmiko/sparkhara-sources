# whirlwind caravan

the whirlwind caravan is a set of applications that can process data from
log files into a mongo database and signal a restful http application.

the applications here are:

* data whirlwind
* caravan pathfinder
* caravan master

## data whirlwind

read a log file and send it line by line over the openstack queue
service(zaqar).

## caravan pathfinder

listen for messages sent by the data whirlwind, the messages are redirected
to localhost ports.

## caravan master

listens for incoming messages on localhost ports and processing them. the
messages are normalized and stored in a mongo database as well as signaling
a restful http endpoint(presumably provided by shiny squirrel).
