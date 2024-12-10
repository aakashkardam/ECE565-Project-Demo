# Author : Aakash Kardam
# Student PhD CIS
# UMASS DARTMOUTH

from pulp import LpProblem, LpMinimize, LpVariable, lpSum
import networkx as nx
import random

def generate_problem(num_tasks, num_edge_nodes, num_cloud_nodes, connection_probability=0.8):
    """Generate random tasks, edge/cloud nodes, and costs."""
    tasks = [f"Task_{i+1}" for i in range(num_tasks)]
    edge_nodes = [f"Edge_{i+1}" for i in range(num_edge_nodes)]
    cloud_nodes = [f"Cloud_{i+1}" for i in range(num_cloud_nodes)]
    nodes = edge_nodes + cloud_nodes

    # Randomly generate costs
    costs = {
        (task, node): random.randint(1, 10)
        for task in tasks
        for node in nodes
        if random.random() < connection_probability
    }

    return tasks, edge_nodes, cloud_nodes, costs


def solve_ilp(tasks, edge_nodes, cloud_nodes, costs):
    """Solve the ILP for task allocation."""
    nodes = edge_nodes + cloud_nodes
    model = LpProblem("Task_Allocation", LpMinimize)

    # Define decision variables
    x = LpVariable.dicts("alloc", costs, cat="Binary")

    # Objective: Minimize total cost
    model += lpSum([costs[key] * x[key] for key in costs]), "Total_Cost"

    # Constraints: Each task must be assigned to exactly one node
    for task in tasks:
        model += lpSum([x[(task, node)] for node in nodes if (task, node) in costs]) == 1, f"Task_Assign_{task}"

    # Solve the ILP
    model.solve()

    # Extract the solution
    allocation = {key: x[key].varValue for key in x if x[key].varValue == 1}
    total_cost = model.objective.value()

    return allocation, total_cost


def build_graph(tasks, edge_nodes, cloud_nodes, allocation, costs):
    """Build a NetworkX graph for visualization."""
    G = nx.Graph()
    for node in edge_nodes + cloud_nodes:
        G.add_node(node, type="resource")
    for task, resource in allocation:
        G.add_edge(task, resource, cost=costs[(task, resource)])
    return G

def solve_iterative_ilp(tasks, edge_nodes, cloud_nodes, costs, capacities, task_execution_times):
    """Solve the ILP iteratively, considering task execution times and dynamic capacities."""
    nodes = edge_nodes + cloud_nodes
    allocation_sequence = []
    remaining_tasks = tasks.copy()

    while remaining_tasks:
        # Solve ILP for remaining tasks and available resources
        available_nodes = [node for node in nodes if capacities[node] > 0]
        current_costs = {(task, node): cost for (task, node), cost in costs.items() if task in remaining_tasks and node in available_nodes}

        if not current_costs:
            break  # No feasible solution for remaining tasks

        # Solve ILP for current state
        allocation, _ = solve_ilp(remaining_tasks, edge_nodes, cloud_nodes, current_costs)

        # Update capacities and track allocated tasks
        for (task, node), allocated in allocation.items():
            if allocated:
                allocation_sequence.append((task, node))
                capacities[node] -= 1  # Decrease capacity
                remaining_tasks.remove(task)

    return allocation_sequence