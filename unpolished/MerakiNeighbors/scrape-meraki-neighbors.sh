#!/bin/bash
IP=$1
OUTFILE=$2

# ts	meraki_ip	auth	bssid	chan	chan_s	chanw	enc	ibss	last_rx	meraki_gw_metric	meraki_nid_hash	rev_rssi	rssi	ssid	wmode
# epoch-seconds	string:"psk"|?	string	int	string	int	string:"wpa"|"wpa2"|"wpa,wpa2"|?	bool	float(interval-in-days?)	int-nullable	int-nullable	int	int	string	string:"y"|"n"

curl --silent -X GET  "http://${IP}/scan.json" 2>>err.log | jq -r '(map(keys_unsorted) | add | unique) as $cols | $cols, map(. as $row | $cols | map($row[.]))[] | @tsv' | tail +2 | sed -e s/^/`date +'%s'`$'\t'${IP}$'\t'/ >> ${OUTFILE}


	
