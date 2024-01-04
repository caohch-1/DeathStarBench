import pandas as pd
import matplotlib.pyplot as plt
import json
import seaborn as sns

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

def plot_pod_num(path: str=""):
    pod_nums = []
    for i in range(1):
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

def plot_distribution(path: str=""):
    with open(f"./data/result{path}/epcho0-distribution.json", "r") as json_file:
        data0 = json.loads(json_file.read())
    with open(f"./data/result{path}/epcho1-distribution.json", "r") as json_file:
        data1 = json.loads(json_file.read())

    for task, _ in data0.items():
        sns.histplot(data0[task], bins="auto", kde=True, color="green", label="Average")
        sns.histplot(data1[task], bins="auto", kde=True, color="red", label="Algorithm")
        # sns.histplot(data2[task], bins="auto", kde=True, color="green", label="2")
        plt.title(f"Distribution for {task}")
        plt.xlabel("Latency (ns)")
        plt.ylabel("Frequency")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.ticklabel_format(style='plain', axis='x')
        plt.show()
    
    all_data0 = list()
    all_data1 = list()
    for task, _ in data0.items():
        all_data0 += data0[task]
        all_data1 += data1[task]
    sns.histplot(all_data0, bins="auto", kde=True, color="green", label="0")
    sns.histplot(all_data1, bins="auto", kde=True, color="red", label="1")
    plt.title(f"Distribution for all tasks")
    plt.xlabel("Latency (ns)")
    plt.ylabel("Frequency")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    plt.ticklabel_format(style='plain', axis='x')
    plt.show()
    
 
# plot_queue("_old")
# plot_latency("_old)
# plot_pod_num("_old")
# plot_distribution("_old")
    
# plot_queue("_sla55")
# plot_latency("_sla55")
# plot_pod_num("_sla55")
# plot_distribution("_sla55")
    
# plot_queue("_sla73")
# plot_latency("_sla73")
# plot_pod_num("_sla73")
# plot_distribution("_sla73")
    
# plot_queue("_sla37")
# plot_latency("_sla37")
# plot_pod_num("_sla37")
# plot_distribution("_sla37")
    
# plot_queue()
# plot_latency()
# plot_pod_num()
# plot_distribution()
        