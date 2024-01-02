# DeathStarBench

```bash
cd ~/Desktop/DeathStarBench/hotelReservation/helm-chart/hotelreservation
helm install hotel --namespace hotel --create-namespace .
minikube service frontend-hotel-hotelres --url -n hotel 
minikube service jaeger-hotel-hotelres --url -n hotel
cd ~/Desktop/DeathStarBench/collector
python main.py
```
Problems:
1. Zero pod problem
2. Different request has different SLA. Some requests are naturally longer than others. Current algorithm doesn't care about SLA.
3. Algorithm won't use all resources. 
