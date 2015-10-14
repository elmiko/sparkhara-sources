import threading
import time

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import requests


def total_emitter(acc):
    time.sleep(2)
    while True:
        data = {'totals': {'all': acc.value}}
        requests.post('http://10.0.1.107:9050/totals', json=data)
        time.sleep(0.5)

if __name__ == '__main__':
    sc = SparkContext(appName='SparkharaLogCounter')
    ssc = StreamingContext(sc, 1)

    total_lines = sc.accumulator(0)

    def rdd_process(rdd):
        a = rdd.collect()
        total_lines.add(len(a))

    lines = ssc.socketTextStream('0.0.0.0', 9901)
    lines.foreachRDD(rdd_process)

    th = threading.Thread(target=total_emitter, args=(total_lines,))
    th.start()
    ssc.start()
    ssc.awaitTermination()
