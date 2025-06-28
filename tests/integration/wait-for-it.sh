#!/bin/sh

HOST=$(echo $1 | cut -d: -f1)
PORT=$(echo $1 | cut -d: -f2)
SHIFT=1

while getopts "t:" opt; do
    case $opt in
        t) TIMEOUT=$OPTARG; SHIFT=$((SHIFT+2));;
        *) ;;
    esac
done

shift $SHIFT

if [ -z "$TIMEOUT" ]; then
    TIMEOUT=15
fi

echo "Ожидание $HOST:$PORT до $TIMEOUT секунд..."

count=0
while ! nc -z $HOST $PORT; do
    if [ $count -ge $TIMEOUT ]; then
        echo "Таймаут после $TIMEOUT секунд, выход..."
        exit 1
    fi
    echo "$HOST:$PORT еще не доступен. Ожидание..."
    sleep 1
    count=$((count+1))
done

echo "$HOST:$PORT доступен"
exec "$@"
