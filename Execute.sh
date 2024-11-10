#!/bin/bash
export HOME=`pwd`
echo "===> Home Directory:"; echo $HOME

## print environment information
printf "===> Python3 information: "; which python3; which pip3
printf "===> Start time: "; /bin/date
printf "===> Job is running on node: "; /bin/hostname
printf "===> Job running as user: "; /usr/bin/id; voms-proxy-info
printf "===> Job is running in directory: "; /bin/pwd
printf "===> Running on file: "; echo $1

## execute main.py
python3 main.py -f $1 -t $2 -y $3
