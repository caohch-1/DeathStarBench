#!/bin/bash
csv_file="./data/pattern.csv"

rates=()
first_row=true
while IFS="," read -r _ col2 || [[ -n $col2 ]]; do
    if [ "$first_row" = true ]; then
        first_row=false
        continue
    fi
    # int_rate=$(printf "%.0f" "$col2")
    int_rate=$(echo "$col2" | tr -d '\r' | xargs)
    int_rate=$(printf "%.0f" "$int_rate")
    rates+=("$int_rate")
done < "$csv_file"

cd ../hotelReservation
for value in "${rates[@]}"; do
    echo "=============================At rate of $value rps============================="
    ../wrk2/wrk -t 15 -c 45 -d 2m -L -s ./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://127.0.0.1:45647 -R "$value"
done

