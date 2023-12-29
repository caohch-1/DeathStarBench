# DeathStarBench
Modify some deployment configuration to make DeathStarBench can be deployed on Mac M1 chips.
Wrk2 is also modified for Mac M1 chip.
Now jaeger sample rate is 1.

Run `workloadGeneration.sh` to generate workloads.
Check `collector/main.py` and `collector/jaegerCollector.py` to collect and process traces.
