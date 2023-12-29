# DeathStarBench
Modify some deployment configuration to make DeathStarBench can be deployed on Mac M1 chips.
Wrk2 is also modified for Mac M1 chip.
Now jaeger sample rate is 1.

SocialNetwork is now deployed on `http://10.19.127.115:8080`.
The frontend url of it is `http://localhost:8080/wrk2-api/xxx`, three types of requests.
The Jaeger can be accessed on `http://localhost:16686`.


Run `workloadGeneration.sh` to generate workloads.
Check `collector/main.py` and `collector/jaegerCollector.py` to collect and process traces. You will get raw json for trces and processed data in csv. To calculate average and further calculate, check scripts.
