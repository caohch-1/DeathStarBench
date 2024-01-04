# DeathStarBench

## How to run

### 0. Requirement
```bash
# Kubectl
sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

# Kubernetes cluster (e.g., minikube)
# Download
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 
# Install
sudo install minikube-linux-amd64 /usr/local/bin/minikube 
# Start (set --registry-mirror=https://xxxxx.mirror.aliyuncs.com if you have)
minikube start --nodes 5 --cpus 4 --memory 8192 --image-mirror-country='cn' 
```
### 1. Deploy microsvc
```bash
# Deploy
cd ~/Desktop/DeathStarBench/hotelReservation/helm-chart/hotelreservation
helm install hotel --namespace hotel --create-namespace .
# Wait deployment finish
kubectl get pods -n hotel -w 
# Expose service
minikube service frontend-hotel-hotelres --url -n hotel # Record the url
minikube service jaeger-hotel-hotelres --url -n hotel # Record the fifth url
```

### 2. Run experiment
```python
# Find following 2 lines in main.py and replace the url with what you record
command = "cd ../hotelReservation && ../wrk2/wrk -t 10 -c 30 -d 90m -L -s ./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://127.0.0.1:42435 -R 1000"
collector = JaegerCollector("http://127.0.0.1:37697/api/traces")
```
```bash
#Run
cd ~/Desktop/DeathStarBench/collector
python main.py
#Plot
python plot.py # Under construction, you can check raw result data in ./data/result
```

### 3. Note
I have deployed everything on `10.19.127.115`. You can SSH to the server and run the codes in `/home/caohch1/Desktop/DeathStarBench/collector`.

## Problems:
1. Zero pod problem
2. Algorithm won't use all resources. 
3. SLA is for per task, now is per task-node.
