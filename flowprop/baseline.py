from jaegerCollector import JaegerCollector
import subprocess
from time import time, sleep
from utils import *
from algorithm import prop_schedule, prop_schedule_sla, vs_schedule
from k8sManager import K8sManager
from workloadGenerator import WorkloadGenerator
import pandas as pd
import datetime
import asyncio

def main():
    k8sManager = K8sManager("hotel")
    # init_env(k8sManager)
    # exit()
    # scale_checkpoint(k8sManager)
    # exit()

    # # Workload generation
    # workloadGenerator = WorkloadGenerator(endpoint="40425", rate=1500, duration="120m")
    # workloadGenerator.generate_stationary()
    # workloadGenerator.generate_nonstationary(prepare_dynamic_workload())
    # exit()


    # Tracing and Adjusting
    epcho = 25
    duration = 90*1 # Look backward
    limit = 1500 # Trace number limit
    total_capacity = 8*2 - 8
    # tasks = ["/wrk2-api/user-timeline/read", "/wrk2-api/post/compose", "/wrk2-api/home-timeline/read"]
    tasks = ["HTTP GET /hotels", "HTTP GET /recommendations", "HTTP POST /reservation", "HTTP POST /user"]
    collector = JaegerCollector(endpoint="43909")
    counter = 0
    result = {task:{"average":[], "normal":[], "tail":[]} for task in tasks}
    while(counter < epcho):
        sleep(duration) # Time window
        print("="*20+f"{counter} Start:"+str(datetime.datetime.now())+"="*20)

        queues_estimation = dict()
        all_trace_latency = dict()
        tail_estimation = dict()
        for task in tasks:
            collector.clear()
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
        # ave_delay_vio_estimation = transform_queue_estimation(calculate_ave_latency_vio(pd.DataFrame(queues_estimation).T.fillna("/")))
        # tail_delay_vio_estimation = transform_queue_estimation(calculate_tail_latency_vio(pd.DataFrame(tail_estimation).fillna("/")))

        print(datetime.datetime.now(), "[Algorithm Input]\nqueues_estimation:\n", pd.DataFrame(queues_estimation).T.fillna("/"))
        # print("ave_delay_vio_estimation\n", pd.DataFrame(ave_delay_vio_estimation).T.fillna("/"))
        # print("tail_delay_vio_estimation\n", pd.DataFrame(tail_delay_vio_estimation).T.fillna("/"))
        pd.DataFrame(queues_estimation).T.fillna("/").to_csv(f"./data/result/epcho{counter}-queue.csv", index=True) # Save
        
        # Step4. Algorithm
        # pod_on_node = prop_schedule(queues_estimation, total_capacity)
        # pod_on_node = prop_schedule_sla(queues_estimation, ave_delay_vio_estimation, weight, total_capacity)
        # Todo: Violation sum minus slo
        pod_on_node = vs_schedule(queues_estimation, {
            'frontend': 4000,
            'geo': 200,
            'profile': 500,
            'rate': 5000,
            'reservation': 20000,
            'search': 7000,
            'recommendation': 100,
            'user':25
        }, total_capacity, 500, collector, k8sManager)
        print(datetime.datetime.now(), "[HAB Algorithm Final Output]\n", pd.DataFrame(list(pod_on_node.items()), columns=['Deployment', 'number']))
        pd.DataFrame(list(pod_on_node.items()), columns=['Deployment', 'number']).to_csv(f"./data/result/epcho{counter}-pod.csv", index=False) # Save


        # Step5. Adjust
        if counter == epcho:
            print("="*20+f"{counter} Finish:"+str(datetime.datetime.now())+"="*20, end="\n\n")
            break
        for deployment_name, pod_num in pod_on_node.items():
            pod_num += 1
            try:
                if deployment_name == "reservation":
                    k8sManager.scale_deployment("memcached-reserve-1-hotel-hotelres", max(1, int(pod_num/3)))
                else:
                    k8sManager.scale_deployment("memcached-"+deployment_name+"-1-hotel-hotelres", max(1, int(pod_num/3)))
            except:
                pass

            try:
                k8sManager.scale_deployment("mongodb-"+deployment_name+"-hotel-hotelres", max(1, int(pod_num/3)))
            except:
                pass
                
            # # Test, comment it
            # if deployment_name == "reservation" or deployment_name == "search":
            #     pod_num = min(2, pod_num)

            k8sManager.scale_deployment(deployment_name+"-hotel-hotelres", pod_num)

        print("="*20+f"{counter} Finish:"+str(datetime.datetime.now())+"="*20, end="\n\n")
        counter += 1

    init_env(k8sManager)
    

if __name__=="__main__":
    main()
