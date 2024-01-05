import pandas as pd
import matplotlib.pyplot as plt
import json
import seaborn as sns
import numpy as np

LOG_SCALE = 2

def plot_queue(path: str=""):
    queues = list()
    for i in range(2):
        queues.append(pd.read_csv(f"./data/result{path}/epcho{i}-queue.csv", index_col=0, na_values="/"))

    tasks_latency_average = [df.apply(pd.to_numeric, errors="coerce").sum() for df in queues]


    for col_name in tasks_latency_average[0].index:
        data = [df[col_name] for df in tasks_latency_average]
        plt.plot(data, marker="o", linestyle="-", label=col_name)

    plt.plot([df.sum()/4 for df in tasks_latency_average], marker="o", linestyle="-", label="Average", color="black")

    plt.title("Queue Estimation")
    plt.xlabel("Epchos")
    plt.ylabel("Latency (ns)")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()

def plot_pod_num(path: str="", epcho: int=2):
    pod_nums = []
    for i in range(epcho-1):
        pod_nums.append(pd.read_csv(f"./data/result{path}/epcho{i}-pod.csv", index_col=0))

    for deployment_name in pod_nums[0].index:
        plt.plot([3]+[df.loc[deployment_name, "number"]+1 for df in pod_nums], marker="o", linestyle="-", label=deployment_name)

    plt.plot("Cost")
    plt.xlabel("Epchos")
    plt.ylabel("Pod Number")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()

def plot_latency(path: str=""):
    with open(f"./data/result{path}/latency.json", "r") as json_file:
        data = json.loads(json_file.read())
    for task, latency_dict in data.items():
        plt.plot(latency_dict["average"], marker='o', linestyle='-', label=f"{task}-average")
        plt.plot(latency_dict["tail"], marker='o', linestyle='-', label=f"{task}-tail")
        plt.title(f"{task} Latency")
        plt.xlabel("Epchos")
        plt.ylabel("latency (ns)")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.show()

def plot_distribution(path: str="", epcho: int=2):
    datas = []
    for i in range(epcho):
        with open(f"./data/result{path}/epcho{i}-distribution.json", "r") as json_file:
            datas.append(json.loads(json_file.read()))

    for task, _ in datas[0].items():
        counter = 0
        for data in datas:
            sns.histplot(data[task], bins="auto", kde=True, label=f"Epcho{counter}", stat="probability", log_scale=LOG_SCALE)
            counter += 1
        plt.title(f"Distribution for {task}")
        plt.xlabel("Latency (ns)")
        plt.ylabel("Probability")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        # plt.ticklabel_format(style='plain', axis='x')
        plt.show()
    
    counter = 0
    for data in datas:
        all_data = []
        for task, _ in data.items():
            all_data += data[task]
        sns.histplot(all_data, bins="auto", kde=True, label=f"Epcho{counter}", stat="probability", log_scale=LOG_SCALE)
        counter += 1
    plt.title(f"Distribution for all tasks")
    plt.xlabel("Latency (ns)")
    plt.ylabel("Probability")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    # plt.ticklabel_format(style='plain', axis='x')
    plt.show()
    

# plot_queue("_old")
# plot_latency("_old")
# plot_pod_num("_old")
# plot_distribution("_old") # Normal
    
# plot_queue("_sla55")
# plot_latency("_sla55")
# plot_pod_num("_sla55")
# plot_distribution("_sla55") # Good
    
# plot_queue("_sla73")
# plot_latency("_sla73")
# plot_pod_num("_sla73")
# plot_distribution("_sla73") # Good
    
# plot_queue("_sla37")
# plot_latency("_sla37")
# plot_pod_num("_sla37")
# plot_distribution("_sla37") # Bad
    
# plot_queue("_sla333")
# plot_latency("_sla333")
# plot_pod_num("_sla333")
# plot_distribution("_sla333") # Bad
    
# plot_queue("_sla235")
# plot_latency("_sla235")
# plot_pod_num("_sla235")
# plot_distribution("_sla235") # Normal
    
# plot_queue("_sla532")
# plot_latency("_sla532")
# plot_pod_num("_sla532")
# plot_distribution("_sla532") # Normal

# plot_queue("_sla532_2")
# plot_latency("_sla532_2")
# plot_pod_num("_sla532_2")
# plot_distribution("_sla532_2") # Normal

# plot_queue("_sla811")
# plot_latency("_sla811")
# plot_pod_num("_sla811")
# plot_distribution("_sla811") # Bad
    
# plot_queue()
# plot_latency()
# plot_pod_num(epcho=5)
plot_distribution(epcho=5)
        