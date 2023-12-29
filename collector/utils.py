import pandas as pd

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