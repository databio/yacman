#!/bin/bash

if [ $# -ne 2 ]; then
    echo $0: usage: test_locking.sh iter max_wait
    exit 1
fi

echo "processes count: $1"
echo "wait max: $2"

rm test.yaml
touch test.yaml
for (( i=1; i<=$1; i++ ))
do  
   ./test_locking.py --id $i --path test.yaml --wait $2&
   echo "submitted: $i"
done