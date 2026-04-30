#!/bin/bash
input="$1"
nshared=10

total=$(wc -l < "$input")
nsystems=$((total-nshared))

tail -n "$nshared" "$input" > .shared_tail.tmp

for i in $(seq 1 "$nsystems"); do
   {
      sed -n "${i}p" "$input"
      cat .shared_tail.tmp
   } > "input_${i}.csv"
done

rm .shared_tail.tmp
