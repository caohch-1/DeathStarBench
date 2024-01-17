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

    plt.title("Cost")
    plt.xlabel("Epchos")
    plt.ylabel("Pod Number")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()

def plot_latency(path: str=""):
    with open(f"./data/result{path}/latency.json", "r") as json_file:
        data = json.loads(json_file.read())
    average_latency, tail_latency = {}, {}

    for task, latency_dict in data.items():
        average_latency[task] = latency_dict["average"]
        plt.plot(latency_dict["average"], marker='o', linestyle='-', label=f"{task}-average")
        plt.title(f"{task} Average Latency")
        plt.xlabel("Epchos")
        plt.ylabel("latency (ns)")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.show()
    for task, latency_dict in data.items():
        tail_latency[task] = latency_dict["tail"]
        plt.plot(latency_dict["tail"], marker='o', linestyle='-', label=f"{task}-tail")
        plt.title(f"{task} Tail Latency")
        plt.xlabel("Epchos")
        plt.ylabel("latency (ns)")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.show()

    average_latency = 0.25*np.array(average_latency["HTTP GET /hotels"]) + \
                      0.25*np.array(average_latency["HTTP GET /recommendations"]) + \
                      0.35*np.array(average_latency["HTTP POST /reservation"]) + \
                      0.15*np.array(average_latency["HTTP POST /user"])
    plt.plot(average_latency, marker='o', linestyle='-', label=f"All-average")
    plt.title(f"All Average Latency")
    plt.xlabel("Epchos")
    plt.ylabel("latency (ns)")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    plt.show()   

    tail_latency = 0.25*np.array(tail_latency["HTTP GET /hotels"]) + \
                      0.25*np.array(tail_latency["HTTP GET /recommendations"]) + \
                      0.35*np.array(tail_latency["HTTP POST /reservation"]) + \
                      0.15*np.array(tail_latency["HTTP POST /user"])
    plt.plot(tail_latency, marker='o', linestyle='-', label=f"All-tail")
    plt.title(f"All Tail Latency")
    plt.xlabel("Epchos")
    plt.ylabel("latency (ns)")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    plt.show()    

def plot_distribution(path: str="", epcho: int=2):
    datas = []
    epcho = epcho
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

def plot_neigh_distribution(path: str="", epcho: int=2, neighbour: int=2):
    datas = []
    for i in range(epcho, epcho+neighbour):
        with open(f"./data/result{path}/epcho{i}-distribution.json", "r") as json_file:
            datas.append(json.loads(json_file.read()))

    for task, _ in datas[0].items():
        counter = epcho
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
    
    counter = epcho
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
    
def plot_cost(path: str="", epcho: int=2):
    pod_nums_list = []
    for i in range(epcho-1):
        pod_nums_list.append(pd.read_csv(f"./data/result{path}/epcho{i}-pod.csv"))
        pod_nums_list[i]["number"] = pod_nums_list[i]["number"] + 1

    weight_counts = {}
    for df in pod_nums_list:
        for index, row in df.iterrows():
            deployment = row['Deployment']
            number = row['number']
            if deployment not in weight_counts:
                weight_counts[deployment] = [3]
            weight_counts[deployment].append(number)
    weight_counts = {deployment: np.array(numbers) for deployment, numbers in weight_counts.items()}
    species = [f"{i}" for i in range(epcho)]

    width = 0.5
    fig, ax = plt.subplots()
    bottom = np.zeros(epcho)
    for boolean, weight_count in weight_counts.items():
        p = ax.bar(species, weight_count, width, label=boolean, bottom=bottom)
        bottom += weight_count
    ax.set_xlabel('Epochs')
    ax.set_ylabel('Number of Pods')
    ax.set_title('Cost')
    ax.legend(loc="upper right")

    plt.show()

def plot_dis_all(path: str="", path2: str="", epcho: int=2):
    datas = []
    epcho = epcho
    for i in range(epcho):
        with open(f"./data/result{path}/epcho{i}-distribution.json", "r") as json_file:
            datas.append(json.loads(json_file.read()))
    
    all_data = []
    for data in datas:
        for task, _ in data.items():
            all_data += data[task]
    
    datas2 = []
    epcho2 = epcho
    for i in range(epcho2):
        with open(f"./data/result{path2}/epcho{i}-distribution.json", "r") as json_file:
            datas2.append(json.loads(json_file.read()))
    
    all_data2 = []
    for data in datas2:
        for task, _ in data.items():
            all_data2 += data[task]

    sns.histplot(all_data, bins="auto", kde=False, label=f"Our", stat="probability", cumulative=False, log_scale=LOG_SCALE, color="red")
    sns.histplot(all_data2, bins="auto", kde=False, label=f"Avg", stat="probability", cumulative=False, log_scale=LOG_SCALE, color="green")
    plt.title(f"Distribution for all tasks")
    plt.xlabel("Latency (ns)")
    plt.ylabel("Probability")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    # plt.ticklabel_format(style='plain', axis='x')
    plt.show() 

def plot_dis_each(path: str="", path2: str="", epcho: int=2):
    datas = []
    epcho = epcho
    for i in range(epcho):
        with open(f"./data/result{path}/epcho{i}-distribution.json", "r") as json_file:
            datas.append(json.loads(json_file.read()))

    all_data = {task:[] for task, _ in datas[0].items()}
    for task, _ in datas[0].items():
        for data in datas:
            all_data[task] += data[task]
    
    datas2 = []
    epcho2 = epcho
    for i in range(epcho2):
        with open(f"./data/result{path2}/epcho{i}-distribution.json", "r") as json_file:
            datas2.append(json.loads(json_file.read()))
    
    all_data2 = {task:[] for task, _ in datas2[0].items()}
    for task, _ in datas2[0].items():
        for data in datas2:
            all_data2[task] += data[task]

    for task, _ in datas[0].items():
        sns.histplot(all_data[task], bins="auto", kde=False, label=f"Our", stat="probability", cumulative=False, log_scale=LOG_SCALE, color="red")
        sns.histplot(all_data2[task], bins="auto", kde=False, label=f"Avg", stat="probability", cumulative=False, log_scale=LOG_SCALE, color="green")
        plt.title(f"Distribution for {task}")
        plt.xlabel("Latency (ns)")
        plt.ylabel("Probability")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        # plt.ticklabel_format(style='plain', axis='x')
        plt.show()


def plot_delay_each(path: str="", path2: str=""):
    with open(f"./data/result{path}/latency.json", "r") as json_file:
        data = json.loads(json_file.read())
    average_latency, tail_latency = {}, {}

    with open(f"./data/result{path2}/latency.json", "r") as json_file:
        data2 = json.loads(json_file.read())
    average_latency2, tail_latency2 = {}, {}

    for task, latency_dict in data.items():
        average_latency[task] = latency_dict["average"]
        average_latency2[task] = data2[task]["average"]

        plt.plot(latency_dict["average"], marker='o', linestyle='-', label=f"Our")
        plt.plot(data2[task]["average"], marker='.', linestyle='--', label=f"Avg")

        plt.title(f"{task} Average Latency")
        plt.xlabel("Epchos")
        plt.ylabel("latency (ns)")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.show()

    for task, latency_dict in data.items():
        tail_latency[task] = latency_dict["tail"]
        tail_latency2[task] = data2[task]["tail"]

        plt.plot(latency_dict["tail"], marker='o', linestyle='-', label=f"Our")
        plt.plot(data2[task]["tail"], marker='.', linestyle='--', label=f"Avg")

        plt.title(f"{task} Tail Latency")
        plt.xlabel("Epchos")
        plt.ylabel("latency (ns)")
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.show()   

def plot_delay_all(path: str="", path2: str="", epchos: int=15):
    with open(f"./data/result{path}/latency.json", "r") as json_file:
        data = json.loads(json_file.read())
    average_latency, tail_latency = {}, {}

    for task, latency_dict in data.items():
        average_latency[task] = latency_dict["average"][:epchos+1]

    for task, latency_dict in data.items():
        tail_latency[task] = latency_dict["tail"][:epchos+1]

    average_latency = 0.35*np.array(average_latency["HTTP GET /hotels"]) + \
                      0.15*np.array(average_latency["HTTP GET /recommendations"]) + \
                      0.3*np.array(average_latency["HTTP POST /reservation"]) + \
                      0.2*np.array(average_latency["HTTP POST /user"])
    

    with open(f"./data/result{path2}/latency.json", "r") as json_file:
        data2 = json.loads(json_file.read())
    average_latency2, tail_latency2 = {}, {}

    for task, latency_dict in data2.items():
        average_latency2[task] = latency_dict["average"][:epchos+1]

    for task, latency_dict in data2.items():
        tail_latency2[task] = latency_dict["tail"][:epchos+1]

    average_latency2 = 0.35*np.array(average_latency2["HTTP GET /hotels"]) + \
                      0.15*np.array(average_latency2["HTTP GET /recommendations"]) + \
                      0.3*np.array(average_latency2["HTTP POST /reservation"]) + \
                      0.2*np.array(average_latency2["HTTP POST /user"])
    

    plt.plot(average_latency, marker='o', linestyle='-', label=f"Our")
    plt.plot(average_latency2, marker='.', linestyle='--', label=f"Avg")
    plt.title(f"All Average Latency")
    plt.xlabel("Epchos")
    plt.ylabel("latency (ns)")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    plt.show()   

    tail_latency = 0.35*np.array(tail_latency["HTTP GET /hotels"]) + \
                      0.15*np.array(tail_latency["HTTP GET /recommendations"]) + \
                      0.3*np.array(tail_latency["HTTP POST /reservation"]) + \
                      0.2*np.array(tail_latency["HTTP POST /user"])
    tail_latency2 = 0.35*np.array(tail_latency2["HTTP GET /hotels"]) + \
                      0.15*np.array(tail_latency2["HTTP GET /recommendations"]) + \
                      0.3*np.array(tail_latency2["HTTP POST /reservation"]) + \
                      0.2*np.array(tail_latency2["HTTP POST /user"])
    plt.plot(tail_latency, marker='o', linestyle='-', label=f"Our")
    plt.plot(tail_latency2, marker='.', linestyle='--', label=f"Avg")
    plt.title(f"All Tail Latency")
    plt.xlabel("Epchos")
    plt.ylabel("latency (ns)")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.ticklabel_format(style='plain', axis='y')
    plt.show()    

# plot_queue("_old")
# plot_latency("_old")
# plot_pod_num("_old")
# plot_distribution("_old") # Normal
    
# plot_queue("_sla532")
# plot_latency("_sla532")
# plot_pod_num("_sla532")
# plot_distribution("_sla532") # Normal

# plot_queue()
# plot_latency(path="531-rateDynamic-limit500")
# plot_pod_num(path="531-rateDynamic-limit500",epcho=20)
# plot_distribution(epcho=15)
    


# plot_neigh_distribution(epcho=0, neighbour=3)
# plot_neigh_distribution(epcho=0, neighbour=1)
    
# plot_cost(path="",epcho=19)
# plot_dis_all(path="532-rate1500-our",epcho=14)
# plot_dis_all(path="",epcho=14)
# plot_dis_each(path="",epcho=20)
# plot_delay_each(path="")

    

# plot_delay_all(path="_rate500_AVG", epchos=15)
    
# plot_dis_all(path="_rate500_OUR",  path2="_rate500_AVG", epcho=15)
# plot_dis_each(path="_rate500_OUR",  path2="_rate500_AVG", epcho=15)
# plot_delay_all(path="_rate500_OUR", path2="_rate500_AVG", epchos=15)
# plot_delay_each(path="_rate500_OUR", path2="_rate500_AVG")
    
# plot_dis_all(path="_rate500_OUR",  path2="_rate500_HPA", epcho=15)
# plot_dis_each(path="_rate500_OUR",  path2="_rate500_HPA", epcho=15)
# plot_delay_all(path="_rate500_OUR", path2="_rate500_HPA", epchos=15)
# plot_delay_each(path="_rate500_OUR", path2="_rate500_HPA")

# plot_dis_each(path="_rate500_OUR",epcho=15)
# plot_dis_each(path="_rate500_AVG",epcho=15)


# plot_delay_all(path="", epchos=15)
