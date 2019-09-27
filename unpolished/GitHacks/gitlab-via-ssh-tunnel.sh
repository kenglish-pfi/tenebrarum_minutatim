#/bin/bash
#  NOTE:  Setting the --user-data-dir IS REQUIRED to get this to work
#         see:  https://superuser.com/questions/1281208/command-line-option-to-open-new-chrome-process-group
#
#  Excerpt from ~/.ssh/config:
#
#   Host <gitlab-host>
#       HostName <gitlab-host>
#       User <gilab-user>
#       IdentityFile ~/.ssh/<user--gitlab>.ED25519
#
#   Host <staging-server-alias>
#       HostName 172.21.10.111
#       User <user>
#       IdentityFile ~/.ssh/<user--staging>.ED25519

gnome-terminal --command='ssh -D 8099 <user>@<staging-server-alias>' &
sleep 1
nohup /opt/google/chrome/chrome --new-window --user-data-dir=~/proxy-home --proxy-server="socks5://127.0.0.1:8099" 'https://<gitlab-host>' &
