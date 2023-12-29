import requests
import json
import numpy as np
from time import time
import pandas as pd
import re
from utils import get_trace_deployment_table



class JaegerCollector:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.traces = None

    # Collect traces from Jaeger
    def collect(self, end_time, duration, limit, service, task_type):
        request_data = {
            "start": int((end_time - int(duration) * 1000) * 1000000),
            "end": int(end_time * 1000000),
            "operation": task_type,
            "limit": limit,
            "service": service,
            "tags": '{"http.status_code":"200"}'
        }

        response = requests.get(self.endpoint, params=request_data)
        self.traces = json.loads(response.content)["data"]

        task_type = task_type.replace("/", "")
        with open(f"./trace_{task_type}_{end_time}_{duration}.json", "w") as f:
            json.dump(self.traces, f)

        print(f"{task_type} Collected!")
        return self.traces
    
    def calculate_duration_difference(self, row, grouped_children):
        if row["childProcessId"] == "NoChild":
            return row["parentDuration"]
        else:
            same_parent_duration_sum = grouped_children.get(row["parentId"], 0)
            return row["parentDuration"] - same_parent_duration_sum

    def process_trace_data(self):
        raw_trace = self.traces
        service_id_mapping = (
            pd.json_normalize(raw_trace)
            .filter(regex="serviceName|traceID|tags")
            .rename(
                columns=lambda x: re.sub(
                    r"processes\.(.*)\.serviceName|processes\.(.*)\.tags",
                    lambda match_obj: match_obj.group(1)
                    if match_obj.group(1)
                    else f"{match_obj.group(2)}Pod",
                    x,
                )
            )
            .rename(columns={"traceID": "traceId"})
        )

        service_id_mapping = (
            service_id_mapping.filter(regex=".*Pod")
            .applymap(
                lambda x: [v["value"] for v in x if v["key"] == "hostname"][0]
                if isinstance(x, list)
                else ""
            )
            .combine_first(service_id_mapping)
        )
        spans_data = pd.json_normalize(raw_trace, record_path="spans")[
            [
                "traceID",
                "spanID",
                "operationName",
                "duration",
                "processID",
                "references",
                "startTime",
            ]
        ]

        spans_with_parent = spans_data[~(spans_data["references"].astype(str) == "[]")]
        root_spans = spans_data[(spans_data["references"].astype(str) == "[]")]
        root_spans = root_spans.rename(
            columns={
                "traceID": "traceId",
                "startTime": "traceTime",
                "duration": "traceLatency"
            }
        )[["traceId", "traceTime", "traceLatency"]]
        spans_with_parent.loc[:, "parentId"] = spans_with_parent["references"].map(
            lambda x: x[0]["spanID"]
        )
        temp_parent_spans = spans_data[
            ["traceID", "spanID", "operationName", "duration", "processID"]
        ].rename(
            columns={
                "spanID": "parentId",
                "processID": "parentProcessId",
                "operationName": "parentOperation",
                "duration": "parentDuration",
                "traceID": "traceId",
            }
        )
        temp_children_spans = spans_with_parent[
            [
                "operationName",
                "duration",
                "parentId",
                "traceID",
                "spanID",
                "processID",
                "startTime",
            ]
        ].rename(
            columns={
                "spanID": "childId",
                "processID": "childProcessId",
                "operationName": "childOperation",
                "duration": "childDuration",
                "traceID": "traceId",
            }
        )
        
        # A merged data frame that build relationship of different spans
        merged_df = pd.merge(
            temp_parent_spans, temp_children_spans, on=["parentId", "traceId"], how="left"
        )

        merged_df = merged_df[
            [
                "traceId",
                "childOperation",
                "childDuration",
                "parentOperation",
                "parentDuration",
                "parentId",
                "childId",
                "parentProcessId",
                "childProcessId",
                "startTime",
            ]
        ]

        # Map each span's processId to its microservice name
        merged_df = merged_df.merge(service_id_mapping, on="traceId")
        merged_df = merged_df.merge(root_spans, on="traceId")
        merged_df = merged_df.fillna("NoChild")  # Replace NaN with "NoChild"

        
        merged_df = merged_df.assign(
            childMS=merged_df.apply(
                lambda x: x[x["childProcessId"]] if x["childProcessId"] != "NoChild" else "NoChild",
                axis=1,
            ),
            childPod=merged_df.apply(
                lambda x: x[f"{str(x['childProcessId'])}Pod"] if x["childProcessId"] != "NoChild" else "NoChildPod",
                axis=1,
            ),
            parentMS=merged_df.apply(
                lambda x: x[x["parentProcessId"]],
                axis=1,
            ),
            parentPod=merged_df.apply(
                lambda x: x[f"{str(x['parentProcessId'])}Pod"],
                axis=1,
            ),
            endTime=merged_df.apply(
                lambda x: x["startTime"] + x["childDuration"] if x["childProcessId"] != "NoChild" else "NoChild",
                axis=1,
            ),
        )
        
        grouped_children = merged_df[merged_df["childProcessId"] != "NoChild"].groupby("parentId")["childDuration"].sum()
        # Apply the function to calculate durationDifference
        merged_df["durationDifference"] = merged_df.apply(lambda x: self.calculate_duration_difference(x, grouped_children), axis=1)
        
        merged_df = merged_df[
            [
                "traceId",
                "traceTime",
                "startTime",
                "endTime",
                "parentId",
                "childId",
                "childOperation",
                "parentOperation",
                "childMS",
                "childPod",
                "parentMS",
                "parentPod",
                "parentDuration",
                "childDuration",
                "durationDifference",
            ]
        ]
        return merged_df

    




