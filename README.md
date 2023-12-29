# DeathStarBench

# Done 
Implement a tracer collecter for DeathstarBench.

Modify some deployment configuration to make DeathStarBench can be deployed on Mac M1 chips.

Wrk2 is also modified for Mac M1 chip. If you find it doesn't work on your linux or windows, visit the offical repo of wrk2 and compile it.

Now jaeger sample rate is 0.3 for SocialNetwork, higher value makes cluster crash easier.

# How to use
SocialNetwork is now deployed on `http://10.19.127.115:8080`.

The frontend url of it is `http://10.19.127.115:8080/wrk2-api/xxx`, three types of requests.

The Jaeger can be accessed on `http://10.19.127.115:16686`.

Run `collector/main.py` to generate workload and collect traces every two minutes. If the blocking phenomenon is unconspicuous, incresing rate (i.e., -R in command) or decrease resource limit of pods (i.e., can reuse implementation in POBO).

