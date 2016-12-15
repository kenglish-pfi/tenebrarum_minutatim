#!/bin/bash
while read I; do
  tracert $I > $I"_trace.log"
done <IPList.txt