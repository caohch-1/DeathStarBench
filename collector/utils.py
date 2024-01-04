import pandas as pd
from k8sManager import K8sManager
import json
from time import sleep

def get_trace_deployment_table(merged_df):
    unique_rows_df = merged_df.drop_duplicates(subset=["traceId", "parentId"])
    sum_duration_difference_parent = unique_rows_df.groupby(["traceId", "parentMS"])["durationDifference"].sum().reset_index()


    result_list = []
    for trace_id, group in sum_duration_difference_parent.groupby("traceId"):
        trace_dict = {"traceID": trace_id}
        
        for index, row in group.iterrows():
            trace_dict[row["parentMS"]] = row["durationDifference"]
        
        result_list.append(trace_dict)
    return pd.DataFrame(result_list)

def transform_queue_estimation(input_dict: dict):
    output_dict = {}
    # Iterate through the input dictionary
    for func, nodes in input_dict.items():
        for node, value in nodes.items():
            if node == "frontend-hotel-hotelres":
                continue
            # If the node is not already in the output dictionary, add it
            if node not in output_dict:
                output_dict[node] = {}

            # If the function is not already in the output dictionary for the node, add it
            if func not in output_dict[node]:
                output_dict[node][func] = 0

            # Increment the value for the current function and node in the output dictionary
            output_dict[node][func] += value
    return output_dict

def init_env(manager: K8sManager, cpu: int=300, mem: int=500):
    for deployment in manager.deployment_list.items:
        if deployment.metadata.name == "frontend-hotel-hotelres":
            manager.set_limit(deployment.metadata.name, 300, 500)
            manager.scale_deployment(deployment.metadata.name, 1+2)
        elif deployment.metadata.name == "consul-hotel-hotelres":
            manager.set_limit(deployment.metadata.name, 500, 500)
            manager.scale_deployment(deployment.metadata.name, 1)
        elif deployment.metadata.name == "jaeger-hotel-hotelres":
            continue
        else:
            manager.set_limit(deployment.metadata.name, cpu, mem)
            sleep(2)
            if "mongodb" not in deployment.metadata.name and "memcached" not in deployment.metadata.name:
                manager.scale_deployment(deployment.metadata.name, 1+2)

def save_dict_to_json(data: dict, path):
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def calculate_ave_latency_vio(ave_latency: pd.DataFrame):
    sla = pd.read_csv("./data/ave_sla.csv", index_col=0)
    ave_latency_numeric = ave_latency.apply(pd.to_numeric, errors="coerce")
    sla_numeric = sla.apply(pd.to_numeric, errors="coerce")
    return ave_latency_numeric-sla_numeric


