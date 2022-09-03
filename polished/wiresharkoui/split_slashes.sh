grep -v '^#' wireshark_oui.txt | sed -e 's/\s*#.*//g' > wireshark_oui.no_comments.txt
grep '/36' wireshark_oui.no_comments.txt > wireshark_oui.slash_36.txt
grep '/28' wireshark_oui.no_comments.txt > wireshark_oui.slash_28.txt
grep -v '/28' wireshark_oui.no_comments.txt | grep -v '/36' | sed '/^$/d' > wireshark_oui.slash_24.txt

