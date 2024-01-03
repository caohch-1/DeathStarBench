import pandas as pd
import matplotlib.pyplot as plt
import json

def plot_queue():
    queues = list()
    for i in range(15):
        queues.append(pd.read_csv(f"./data/result/epcho{i}-queue.csv", index_col=0, na_values="/"))

    tasks_latency_average = [df.apply(pd.to_numeric, errors="coerce").sum() for df in queues]


    for col_name in tasks_latency_average[0].index:
        data = [df[col_name] for df in tasks_latency_average]
        plt.plot(data, marker="o", linestyle="-", label=col_name)

    plt.plot([df.sum()/4 for df in tasks_latency_average], marker="o", linestyle="-", label="Average", color="black")

    plt.xlabel("Epchos")
    plt.ylabel("Latency(ns)")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()

def plot_pod_num():
    pod_nums = []
    for i in range(15):
        pod_nums.append(pd.read_csv(f"./data/result/epcho{i}-pod.csv", index_col=0))

    for deployment_name in pod_nums[0].index:
        plt.plot([df.loc[deployment_name, "number"]+1 for df in pod_nums], marker="o", linestyle="-", label=deployment_name)

    plt.xlabel("Epchos")
    plt.ylabel("Pod Number")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()

def plot_latency():
    with open("./data/result/latency.json", "r") as json_file:
        data = json.loads(json_file.read())
    for task, latency_dict in data.items():
        plt.plot(latency_dict["average"], marker='o', linestyle='-', label=f"{task}-average")
        plt.plot(latency_dict["tail"], marker='o', linestyle='-', label=f"{task}-tail")
        plt.xlabel("Epchos")
        plt.ylabel("latency (ns)")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.show()

plot_queue()
plot_latency()
plot_pod_num()
        