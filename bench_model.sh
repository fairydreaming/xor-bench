#!/bin/bash

model="$1"
echo "$model"

for length in 2 4 8 16 32 64 128 256
do
	echo $length
	mkdir -p results/$length
	log_file="results/$length/`echo $model|sed 's/\//-/g'`.log"
	echo $log_file
	./xor_bench.py -l $length -n 10|./run_openrouter.py -m "$model"|tee "$log_file"
	if ! tail -n 1 $log_file|grep -q "$length: 100.00"
	then
		break
	fi
done

