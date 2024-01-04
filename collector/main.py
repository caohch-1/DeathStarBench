from jaegerCollector import JaegerCollector
import subprocess
from time import time, sleep
from utils import get_trace_deployment_table, transform_queue_estimation, init_env, save_dict_to_json, calculate_ave_latency_vio, calculate_tail,calculate_tail_latency_vio
from algorithm import prop_schedule, prop_schedule_sla, prop_schedule_sla2
from k8sManager import K8sManager
import pandas as pd
import datetime

if __name__=="__main__":
    k8sManager = K8sManager("hotel")
    # init_env(k8sManager)
    # exit()

    # Workload generation
    # command = "cd ../socialNetwork && ../wrk2/wrk -t 10 -c 30 -d 7m -L -s ./wrk2/scripts/social-network/mixed-workload.lua http://10.19.127.115:8080 -R 1000"
    # command = "cd ../socialNetwork && ../wrk2/wrk -t 10 -c 30 -d 7m -L -s ./wrk2/scripts/social-network/mixed-workload.lua http://127.0.0.1:8080 -R 1000"
    command = "cd ../hotelReservation && ../wrk2/wrk -t 15 -c 45 -d 10m -L -s ./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://127.0.0.1:44011 -R 1000"
    workload_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(datetime.datetime.now(), "[Workload] Generating..")

    # Tracing and Adjusting
    epcho = 2
    duration = 120*1 # Look backward
    limit = 10000 # Trace number limit
    total_capacity = 8*3 - 8
    weight= [0.2, 0.3, 0.5]
    # tasks = ["/wrk2-api/user-timeline/read", "/wrk2-api/post/compose", "/wrk2-api/home-timeline/read"]
    tasks = ["HTTP GET /hotels", "HTTP GET /recommendations", "HTTP POST /reservation", "HTTP POST /user"]
    collector = JaegerCollector("http://127.0.0.1:40973/api/traces")
    counter = 0
    result = {task:{"average":[], "normal":[], "tail":[]} for task in tasks}
    while(counter < epcho):
        sleep(120) # Time window
        print("="*20+f"{counter} Start:"+str(datetime.datetime.now())+"="*20)

        queues_estimation = dict()
        all_trace_latency = dict()
        tail_estimation = dict()
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

            # Step3. Calculate algorithm inputs
            queues_estimation[task] = trace_deployment_table.mean(axis=0, numeric_only=True).to_dict()
            all_trace_latency[task] = collector.get_all_latency()
            tail_estimation[task] = calculate_tail(trace_deployment_table)
            print(datetime.datetime.now(), f"[Jaeger Collector] {task}:")
            avg_lat, normal_lat, tail_lat = collector.calculate_average_latency()
            result[task]["average"].append(avg_lat)
            result[task]["normal"].append(normal_lat)
            result[task]["tail"].append(tail_lat)
        save_dict_to_json(result, "./data/result/latency.json") # Save
        save_dict_to_json(all_trace_latency, f"./data/result/epcho{counter}-distribution.json") # Save

        
        queues_estimation = transform_queue_estimation(queues_estimation)
        ave_delay_vio_estimation = transform_queue_estimation(calculate_ave_latency_vio(pd.DataFrame(queues_estimation).T.fillna("/")))
        tail_delay_vio_estimation = transform_queue_estimation(calculate_tail_latency_vio(pd.DataFrame(tail_estimation).fillna("/")))

        print(datetime.datetime.now(), "[Algorithm Input]\nqueues_estimation:\n", pd.DataFrame(queues_estimation).T.fillna("/"))
        print("ave_delay_vio_estimation\n", pd.DataFrame(ave_delay_vio_estimation).T.fillna("/"))
        print("tail_delay_vio_estimation\n", pd.DataFrame(tail_delay_vio_estimation).T.fillna("/"))
        pd.DataFrame(queues_estimation).T.fillna("/").to_csv(f"./data/result/epcho{counter}-queue.csv", index=True) # Save
        
        # Step4. Algorithm
        # pod_on_node = prop_schedule(queues_estimation, total_capacity)
        # pod_on_node = prop_schedule_sla(queues_estimation, ave_delay_vio_estimation, weight, total_capacity)
        pod_on_node = prop_schedule_sla2(queues_estimation, ave_delay_vio_estimation, tail_delay_vio_estimation, weight, total_capacity)
        print(datetime.datetime.now(), "[Algorithm Output]\n", pd.DataFrame(list(pod_on_node.items()), columns=['Deployment', 'number']))
        pd.DataFrame(list(pod_on_node.items()), columns=['Deployment', 'number']).to_csv(f"./data/result/epcho{counter}-pod.csv", index=False) # Save

        # Step5. Adjust
        for deployment_name, pod_num in pod_on_node.items():
            pod_num += 1
            k8sManager.scale_deployment(deployment_name+"-hotel-hotelres", pod_num)

        print("="*20+f"{counter} Finish:"+str(datetime.datetime.now())+"="*20, end="\n\n")
        counter += 1
    
    workload_process.kill()
    output, error = workload_process.communicate()
    if error.decode():
        print(datetime.datetime.now(), "Command error:", error.decode())
    else:
        print(datetime.datetime.now(), "Command output:", output.decode())
    
    init_env(k8sManager)
