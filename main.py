# Author : Aakash Kardam
# Student PhD CIS
# UMASS DARTMOUTH

import random
from ilp_solver import generate_problem, solve_iterative_ilp, build_graph
from visualization import animate_solution_iterative

num_tasks = 15
num_edge_nodes = 5
num_cloud_nodes = 5
task_execution_times = {f"Task_{i+1}": random.randint(2, 5) for i in range(num_tasks)}

tasks, edge_nodes, cloud_nodes, costs = generate_problem(num_tasks, num_edge_nodes, num_cloud_nodes)

# Solve ILP iteratively
capacities = {node: 5 for node in edge_nodes + cloud_nodes}
allocation_sequence = solve_iterative_ilp(tasks, edge_nodes, cloud_nodes, costs, capacities, task_execution_times)

G = build_graph(tasks, edge_nodes, cloud_nodes, allocation_sequence, costs)
animate_solution_iterative(G, allocation_sequence, tasks, edge_nodes, cloud_nodes, task_execution_times,costs)