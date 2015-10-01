from pyspark import SparkContext
from pyspark.streaming import StreamingContext


def rdd_print(rdd):
    a = rdd.collect()
    print(a)

if __name__ == '__main__':
    sc = SparkContext(appName='SparkharaLogCounter')
    ssc = StreamingContext(sc, 1)

    lines = ssc.socketTextStream('0.0.0.0', 9900)
    lines.foreachRDD(rdd_print)
    ssc.start()
    ssc.awaitTermination()
