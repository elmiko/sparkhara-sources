#!/bin/sh

. /common.sh

MASTER_SERVICE_NAME=${1//-/_}
echo "$(eval echo \$${MASTER_SERVICE_NAME^^}_SERVICE_HOST) spark-master" >> /tmp/hosts

MONGODB_SERVICE_NAME=${2//-/_}
echo "$(eval echo \$${MONGODB_SERVICE_NAME^^}_SERVICE_HOST) mongodb" >> /tmp/hosts

# because the hostname only resolves locally
export SPARK_LOCAL_HOSTNAME=$(hostname -i)

spark-submit /caravan_master.py --port 1984 \
                                --master spark://spark-master:7077 \
                                --mongo mongodb://mongodb \
                                --rest http:XYZ
