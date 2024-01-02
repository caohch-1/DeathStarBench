from jaegerCollector import JaegerCollector
import subprocess
from time import time, sleep
from utils import get_trace_deployment_table, transform_queue_estimation
from algorithm import prop_schedule
from k8sManager import K8sManager


if __name__=="__main__":
    k8sManager = K8sManager("social")

    # Workload generation
    command = " cd ../socialNetwork && ../wrk2/wrk -t 10 -c 30 -d 7m -L -s ./wrk2/scripts/social-network/mixed-workload.lua http://10.19.127.115:8080 -R 1000"
    workload_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Tracing and Adjusting
    epcho = 2
    tasks = ["/wrk2-api/user-timeline/read", "/wrk2-api/post/compose", "/wrk2-api/home-timeline/read"]
    duration = 60*1 # Look backward
    limit = 3000 # Trace number limit
    collector = JaegerCollector("http://10.19.127.115:16686/api/traces")
    counter = 0
    while(counter <= epcho):
        sleep(90) # Time window
        print("="*20+f"{counter} Start:"+str(time())+"="*20)

        queues_estimation = dict()
        for task in tasks:
            # Step1. Collect and process data
            end_time = time()
            raw_traces = collector.collect(end_time=end_time, duration=duration, limit=limit, service="nginx-web-server", task_type=task)
            merged_traces = collector.process_trace_data()
            trace_deployment_table = get_trace_deployment_table(merged_df=merged_traces)

            # # Step2. Store data
            # task = task.replace("/", "")
            # trace_deployment_table.to_csv(f'./data/{task}_{end_time}_{duration}.csv', index=False)

            # Step3. Calculate average
            average_per_parentMS = trace_deployment_table.mean(axis=0, numeric_only=True)
            queues_estimation[task] = average_per_parentMS.to_dict()

        queues_estimation = transform_queue_estimation(queues_estimation)
        print(queues_estimation)

        # Step4. Algorithm
        total_capacity = 30
        pod_on_node = prop_schedule(queues_estimation, total_capacity)
        print("For deployment xxxxxx, adjust pod num. to xxxxx.")
        print(pod_on_node)

        # Step5. Adjust (can reuse code in POBO)
        for deployment_name, pod_num in pod_on_node.items():
            k8sManager.scale_deployment(deployment_name, pod_num)
        print("Scale pods of deployment xxxxx to xxxxxx.")

        print("="*20+f"{counter} Finish:"+str(time())+"="*20, end="\n\n")
        counter += 1
    
    output, error = workload_process.communicate()
    print("Command output:", output.decode())
    print("Command error:", error.decode())
