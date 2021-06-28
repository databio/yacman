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
	./locking_tests.py --id $i --path test.yaml --wait $2&
	pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo "finished!"

file_lines=$(cat test.yaml | wc -l)
diff=$(($1 - file_lines))

if (( $diff > 0 )); then
	echo "ERROR: $diff entries have been lost!"
	exit 1
else
	echo "SUCCESS: $1 lines present in the file"
	exit 0
fi
