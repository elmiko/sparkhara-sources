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


def store_packets(id, count, log_ids, log_packets, mongo_url):
    data = {'_id': id,
            'processed-at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'count': count,
            'log-ids': log_ids,
            }
    db = pymongo.MongoClient(mongo_url).sparkhara
    db.count_packets.insert_one(data)
    db.log_packets.insert_many(log_packets, ordered=False)


def repack(line):
    (service, log) = json.loads(line).items()[0]

    return  {'_id': uuid.uuid4().hex,
             'service': service,
             'log': log}


def process_generic(rdd, mongo_url, rest_url):
    count = rdd.count()
    if count is 0:
        return

    print "processing", count, "entries"

    normalized_rdd = rdd.map(repack)

    ids = normalized_rdd.map(lambda e: e['_id']).collect()

    id = uuid.uuid4().hex

    store_packets(id,
                  count,
                  ids,
                  normalized_rdd.collect(),
                  mongo_url)

    signal_rest_server(id,
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
                        help='the socket to attach for streaming text data '
                        '(default: caravan-pathfinder)',
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
