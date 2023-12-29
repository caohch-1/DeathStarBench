 cd ./socialNetwork
 ../wrk2/wrk -t 10 -c 30 -d 2m -L -s ./wrk2/scripts/social-network/mixed-workload.lua http://10.19.127.115:8080 -R 1200