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

import random
def normalize_probabilities(probabilities):
    total = sum(probabilities)
    normalized_probabilities = [prob / total for prob in probabilities]
    return normalized_probabilities

def sample_from_prob_list(elements, blocking):
    if len(elements) != len(blocking):
        raise ValueError("Number of elements must be equal to the number of probabilities.")
    probabilities = normalize_probabilities(blocking)
    sampled_element = random.choices(elements, weights=probabilities, k=1)[0]
    return sampled_element


def prop_schedule_sla(queues_estimation, ave_delay_vio_estimation, weight, total_capacity):
    """
    prop_schedule is a function to schedule pods for nodes according to the estimated queue length on the nodes

    :param queues_estimation: a dict that represents {node: {flow: ave_queue_length, ..., }} and
    :param ave_delay_vio_estimation: a dict that represents {node: {flow: ave_delay_vio, ..., }} and
    :param weight: a list denotes to balance three metrics (queue, ave delay vio, tail delay vio) and
    :param total_capacity: total number of pods we use
    :return: a dict that represents {node: pod num}
    """
    total_queue_in_system, total_ave_delay_vio,= 0.0, 0.0,
    queue_per_node, ave_delay_vio_per_node,= {}, {}
    for node in queues_estimation:
        queue_per_node[node] = sum([queue_per_flow for _, queue_per_flow in queues_estimation[node].items()])
        total_queue_in_system += queue_per_node[node]

        ave_delay_vio_per_node[node] = sum([ave_delay_vio_per_flow for _, ave_delay_vio_per_flow in ave_delay_vio_estimation[node].items()])
        total_ave_delay_vio += ave_delay_vio_per_node[node]


    blocking_per_node, total_blocking = {}, 0.0
    for node in queues_estimation:
        blocking_per_node[node] = weight[0] * queue_per_node[node]/total_queue_in_system if total_queue_in_system > 0 else 0.0
        blocking_per_node[node] += weight[1] * ave_delay_vio_per_node[node]/total_ave_delay_vio if total_ave_delay_vio > 0 else 0.0
        total_blocking += blocking_per_node[node]

    pod_on_node = {}
    left_pods = total_capacity
    for node in queues_estimation:
        pod_on_node[node] = total_capacity*blocking_per_node[node]/total_blocking if total_blocking > 0 else 0.0
        pod_on_node[node] = int(pod_on_node[node])
        left_pods -= pod_on_node[node]

    if total_blocking == 0:
        return pod_on_node

    nodes, blocking = zip(*blocking_per_node.items())
    probs = normalize_probabilities(blocking)
    while left_pods > 0:
        node = sample_from_prob_list(nodes, probs)
        pod_on_node[node] += 1
        left_pods -= 1

    return pod_on_node

def prop_schedule_sla2(queues_estimation, ave_delay_vio_estimation, tail_delay_vio_estimation, weight, total_capacity):
    """
    prop_schedule is a function to schedule pods for nodes according to the estimated queue length on the nodes

    :param queues_estimation: a dict that represents {node: {flow: ave_queue_length, ..., }} and
    :param ave_delay_vio_estimation: a dict that represents {node: {flow: ave_delay_vio, ..., }} and
    :param tail_delay_vio_estimation: a dict that represents {node: {flow: tail_delay_vio, ..., }} and
    :param weight: a list denotes to balance three metrics (queue, ave delay vio, tail delay vio) and
    :param total_capacity: total number of pods we use
    :return: a dict that represents {node: pod num}
    """
    total_queue_in_system, total_ave_delay_vio, total_tail_delay_vio = 0.0, 0.0, 0.0
    queue_per_node, ave_delay_vio_per_node, tail_delay_vio_per_node = {}, {}, {}
    for node in queues_estimation:
        queue_per_node[node] = sum([queue_per_flow for _, queue_per_flow in queues_estimation[node].items()])
        total_queue_in_system += queue_per_node[node]

        ave_delay_vio_per_node[node] = sum([ave_delay_vio_per_flow for _, ave_delay_vio_per_flow in ave_delay_vio_estimation[node].items()])
        total_ave_delay_vio += ave_delay_vio_per_node[node]

        tail_delay_vio_per_node[node] = sum([tail_delay_vio_per_flow for _, tail_delay_vio_per_flow in tail_delay_vio_estimation[node].items()])
        total_tail_delay_vio += tail_delay_vio_per_node[node]

    blocking_per_node, total_blocking = {}, 0.0
    for node in queues_estimation:
        blocking_per_node[node] = weight[0] * queue_per_node[node]/total_queue_in_system if total_queue_in_system > 0 else 0.0
        blocking_per_node[node] += weight[1] * ave_delay_vio_per_node[node]/total_ave_delay_vio if total_ave_delay_vio > 0 else 0.0
        blocking_per_node[node] += weight[2] * total_tail_delay_vio[node]/total_tail_delay_vio if total_tail_delay_vio > 0 else 0.0
        total_blocking += blocking_per_node[node]

    pod_on_node = {}
    left_pods = total_capacity
    for node in queues_estimation:
        pod_on_node[node] = total_capacity*blocking_per_node[node]/total_blocking if total_blocking > 0 else 0.0
        pod_on_node[node] = int(pod_on_node[node])
        left_pods -= pod_on_node[node]

    if total_blocking == 0:
        return pod_on_node

    nodes, blocking = zip(*blocking_per_node.items())
    probs = normalize_probabilities(blocking)
    while left_pods > 0:
        node = sample_from_prob_list(nodes, probs)
        pod_on_node[node] += 1
        left_pods -= 1

    return pod_on_node