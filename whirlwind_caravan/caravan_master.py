import argparse
import datetime
import json
import sys
import uuid

import pymongo
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import requests

from operator import add


def signal_rest_server(id, count, service_counts, rest_url):
    data = {'id': id,
            'count': count,
            'service-counts': service_counts,
            }
    try:
        requests.post(rest_url, json=data)
    except Exception as ex:
        print('handled: {}'.format(ex))


def store_packets(id, count, normalized_rdd, mongo_url):
    # TODO: consider changing this to:
    # 0. rdd.foreachPartition(lambda p: code to do log_packets.insert_many)
    # 1. code to insert log-ids document
    log_packets = normalized_rdd.collect()
    data = {'_id': id,
            'processed-at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'count': count,
            }
    db = pymongo.MongoClient(mongo_url).sparkhara
    db.count_packets.insert_one(data)
    db.log_packets.insert_many(log_packets, ordered=False)


def repack(line, count_packet_id):
    (service, log) = json.loads(line).items()[0]

    return  {'count-packet': count_packet_id,
             'service': service,
             'log': log}


def process_generic(rdd, mongo_url, rest_url):
    count = rdd.count()
    if count is 0:
        return

    print "processing", count, "entries"

    count_packet_id = uuid.uuid4().hex

    normalized_rdd = rdd.map(lambda e: repack(e, count_packet_id)).cache()

    store_packets(count_packet_id, count, normalized_rdd, mongo_url)

    signal_rest_server(count_packet_id,
                       count,
                       dict(normalized_rdd.map(
                           lambda e: (e['service'], 1)).reduceByKey(add).collect()),
                       rest_url)

def main():
    parser = argparse.ArgumentParser(
        description='process some log messages, storing them and signaling '
                    'a rest server')
    parser.add_argument('--mongo', help='the mongodb url',
                        required=True)
    parser.add_argument('--rest', help='the rest endpoint to signal',
                        required=True)
    parser.add_argument('--port', help='the port to receive from '
                        '(default: 1984)',
                        default=1984, type=int)
    parser.add_argument('--appname', help='the name of the spark application '
                        '(default: SparkharaLogCounter)',
                        default='SparkharaLogCounter')
    parser.add_argument('--master',
                        help='the master url for the spark cluster')
    parser.add_argument('--socket',
                        help='the socket ip address to attach for streaming '
                        'text data (default: caravan-pathfinder)',
                        default='caravan-pathfinder')
    args = parser.parse_args()
    mongo_url = args.mongo
    rest_url = args.rest

    sconf = SparkConf().setAppName(args.appname)
    if args.master:
        sconf.setMaster(args.master)
    sc = SparkContext(conf=sconf)
    ssc = StreamingContext(sc, 1)

    lines = ssc.socketTextStream(args.socket, args.port)
    lines.foreachRDD(lambda rdd: process_generic(rdd, mongo_url, rest_url))

    ssc.start()
    ssc.awaitTermination()


if __name__ == '__main__':
    main()
