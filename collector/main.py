from jaegerCollector import JaegerCollector
import subprocess
from time import time, sleep
from utils import get_trace_deployment_table, transform_queue_estimation, init_env, save_dict_to_json
from algorithm import prop_schedule
from k8sManager import K8sManager
import pandas as pd

if __name__=="__main__":
    k8sManager = K8sManager("hotel")
    init_env(k8sManager)

    # Workload generation
    # command = "cd ../socialNetwork && ../wrk2/wrk -t 10 -c 30 -d 7m -L -s ./wrk2/scripts/social-network/mixed-workload.lua http://10.19.127.115:8080 -R 1000"
    # command = "cd ../socialNetwork && ../wrk2/wrk -t 10 -c 30 -d 7m -L -s ./wrk2/scripts/social-network/mixed-workload.lua http://127.0.0.1:8080 -R 1000"
    command = "cd ../hotelReservation && ../wrk2/wrk -t 10 -c 30 -d 90m -L -s ./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://127.0.0.1:36873 -R 1000"
    workload_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("[Workload] Generating..")

    # Tracing and Adjusting
    epcho = 30
    total_capacity = 20
    # tasks = ["/wrk2-api/user-timeline/read", "/wrk2-api/post/compose", "/wrk2-api/home-timeline/read"]
    tasks = ["HTTP GET /hotels", "HTTP GET /recommendations", "HTTP POST /reservation", "HTTP POST /user"]
    duration = 60*1 # Look backward
    limit = 6000 # Trace number limit
    # collector = JaegerCollector("http://10.19.127.115:16686/api/traces")
    collector = JaegerCollector("http://127.0.0.1:40299/api/traces")
    counter = 0
    result = {task:{"average":[], "normal":[], "tail":[]} for task in tasks}
    while(counter <= epcho):
        sleep(60) # Time window
        print("="*20+f"{counter} Start:"+str(time())+"="*20)

        queues_estimation = dict()
        for task in tasks:
            # Step1. Collect and process data
            end_time = time()
            # raw_traces = collector.collect(end_time=end_time, duration=duration, limit=limit, service="nginx-web-server", task_type=task)
            raw_traces = collector.collect(end_time=end_time, duration=duration, limit=limit, service="frontend", task_type=task)
            merged_traces = collector.process_trace_data()
            trace_deployment_table = get_trace_deployment_table(merged_df=merged_traces)

            # # Step2. Store data
            # task = task.replace("/", "")
            # trace_deployment_table.to_csv(f'./data/{task}_{end_time}_{duration}.csv', index=False)

            # Step3. Calculate and record result
            average_per_parentMS = trace_deployment_table.mean(axis=0, numeric_only=True)
            queues_estimation[task] = average_per_parentMS.to_dict()
            print(f"[Jaeger Collector] {task}:")
            avg_lat, normal_lat, tail_lat = collector.calculate_average_latency()
            result[task]["average"].append(avg_lat)
            result[task]["normal"].append(normal_lat)
            result[task]["tail"].append(tail_lat)
        save_dict_to_json(result, "./data/result/latency.json")

        queues_estimation = transform_queue_estimation(queues_estimation)
        print("[Algorithm Input]\n", pd.DataFrame(queues_estimation).T.fillna("/"))
        pd.DataFrame(queues_estimation).T.fillna("/").to_csv(f"./data/result/epcho{counter}-queue.csv", index=True)

        # Step4. Algorithm
        pod_on_node = prop_schedule(queues_estimation, total_capacity)
        print("[Algorithm Output]\n", pd.DataFrame(list(pod_on_node.items()), columns=['Deployment', 'number']))
        pd.DataFrame(list(pod_on_node.items()), columns=['Deployment', 'number']).to_csv(f"./data/result/epcho{counter}-pod.csv", index=False)

        # Step5. Adjust
        for deployment_name, pod_num in pod_on_node.items():
            pod_num += 1
            k8sManager.scale_deployment(deployment_name+"-hotel-hotelres", pod_num)

        print("="*20+f"{counter} Finish:"+str(time())+"="*20, end="\n\n")
        counter += 1
    
    output, error = workload_process.communicate()
    if error.decode():
        print("Command error:", error.decode())
    else:
        print("Command output:", output.decode())
