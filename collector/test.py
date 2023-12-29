import requests
import json
import numpy as np
from time import time
import pandas as pd
import re
from utils import get_trace_deployment_table
from jaegerCollector import JaegerCollector

if __name__=="__main__":
    # task = "/wrk2-api/user-timeline/read"
    # task = "/wrk2-api/post/compose"
    task = "/wrk2-api/home-timeline/read"
    duration = 60*3
    limit = 5000

    # Step1. Collect and process data
    end_time = time()
    collector = JaegerCollector("http://10.19.127.115:16686/api/traces")
    raw_traces = collector.collect(end_time=end_time, duration=duration, limit=limit, service="nginx-web-server", task_type=task)
    merged_traces = collector.process_trace_data()
    trace_deployment_table = get_trace_deployment_table(merged_df=merged_traces)

    # Step2. Store data
    task = task.replace("/", "")
    trace_deployment_table.to_csv(f'{task}_{end_time}_{duration}.csv', index=False)

    # Step3. Read data and calculate average
    data_path = 'wrk2-apihome-timelineread_1703851104.0243788_180.csv'
    # data_path = 'wrk2-apipostcompose_1703851065.923563_180.csv'
    # data_path = 'wrk2-apiuser-timelineread_1703851047.265698_180.csv'
    read_df = pd.read_csv(data_path)
    average_per_parentMS = read_df.mean(axis=0, numeric_only=True)
    print(data_path.split("_")[0], average_per_parentMS.to_dict())
