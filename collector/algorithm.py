def prop_schedule(queues_estimation, total_capacity):
    """
    prop_schedule is a function to schedule pods for nodes according to the estimated queue length on the nodes
    
    :param queues_estimation: a dict that represents {node: {flow: ave_queue_length, ..., }} and 
    :param total_capacity: total number of pods we use
    :return: a dict that represents {node: pod num}

    let's consider a simple example with two flows and four nodes
    flow 1 goes through {node1, node2, node3} and flow 2 goes through {node1, node2, node4}
    queues_estimation = {node1: {f1: 3, f2: 7}, node2: {f1: 2, f2: 3}, node3: {f1: 5}, node4: {f2: 0}}
    total_capacity = 40
    
    prop_schedule computes and returns the dict pod_on_node
    pod_on_node = {node1: 20, node2: 10, node3: 10, node4: 0}     
    """
    total_queue_in_system = 0.0
    queue_per_node = {}
    for node in queues_estimation:
        queue_per_node[node] = sum([queue_per_flow for _, queue_per_flow in queues_estimation[node].items()])
        total_queue_in_system += queue_per_node[node]
    
    pod_on_node = {}
    for node in queues_estimation:
        pod_on_node[node] = total_capacity*queue_per_node[node]/total_queue_in_system if total_queue_in_system > 0 else 0.0
        pod_on_node[node] = int(pod_on_node[node])
    
        
    return pod_on_node