#!/bin/sh
#
# You can use this script to launch Redis and minio on Kubernetes
# and forward their connections to your local computer. That means
# you can then work on your worker-server.py and rest-server.py
# on your local computer rather than pushing to Kubernetes with each change.
#
# To kill the port-forward processes us e.g. "ps augxww | grep port-forward"
# to identify the processes ids
# Start by installing minio helm
me=`basename "$0"`
usage() {
    echo "Usage: $me APPLY"
    echo "APPLY - [0-1]"
    exit $1
}

fatal() {
    echo error: $*
    usage 1
}

[ "$1" = -h ] && usage 0
[ $# -lt 1 ] && fatal "$me: No argument provided"

if [ $1 -eq 0 ]; then
    OPERATION=delete
    kubectl delete ns minio-ns
else
    OPERATION=apply
    helm repo add bitnami https://charts.bitnami.com/bitnami || echo "Bitnami repo found"
    helm install -f ../minio/minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio || echo "Minio Already exists"
fi
echo $OPERATION
kubectl $OPERATION -f ../minio/minio-external-service.yaml
kubectl $OPERATION -f ../redis/redis-deployment.yaml
kubectl $OPERATION -f ../redis/redis-service.yaml

kubectl $OPERATION -f ../logs/logs-deployment.yaml

kubectl $OPERATION -f ../worker/worker-deployment.yaml

kubectl $OPERATION -f ../mysql/mysql-pv.yaml &
kubectl $OPERATION -f ../mysql/mysql-pvc.yaml &
kubectl $OPERATION -f ../mysql/mysql-deployment.yaml
kubectl $OPERATION -f ../mysql/mysql-service.yaml

#kubectl $OPERATION -f ../rest/rest-deployment.yaml
#kubectl $OPERATION -f ../rest/rest-service.yaml
#kubectl $OPERATION -f ../rest/rest-ingress.yaml

if [ $DELETE -ne 0 ]; then
    echo "Port forwarding redis and minio"
    sleep 7
    kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9000:9000 &
    kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9001:9001 &
    kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
    # If you're using minio from the kubernetes tutorial this will forward those
fi