#!/bin/bash
#   depends on curl, jq
#   assumes ES on locahost_ipv4:9200
#
while [ ! "`curl -s -XGET 127.0.0.1:9200 | jq \".tagline == \\\"You Know, for Search\\\""`" == "true" ]; do echo "waiting for ES"; sleep 1; done
