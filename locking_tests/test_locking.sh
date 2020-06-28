#!/bin/bash

if [ $# -ne 2 ]; then
    echo $0: usage: test_locking.sh iter max_wait
    exit 1
fi

rm lock.test.yaml
rm test.yaml

echo "processes count: $1"
echo "wait max: $2"

touch test.yaml
for (( i=1; i<=$1; i++ ))
do
	echo "submitting: $i"
   ./test_locking.py --id $i --path test.yaml --wait $2&
done