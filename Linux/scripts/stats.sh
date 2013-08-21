#!/bin/bash

CPU=$(mpstat | awk '$12 ~ /[0-9.]+/ { printf("%.1f%%",100 - $12) }')

MEM=$(free -m | grep "Mem:" | awk '$3 ~ /[0-9.]+/ { printf("%.2f%%",$3 / $2) }')

echo "C=$CPU M=$MEM"


