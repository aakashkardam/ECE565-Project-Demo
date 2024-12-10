# **Dynamic ILP Task Allocation and Visualization**

This project demonstrates a simplified **dynamic task allocation** using **Integer Linear Programming (ILP)** and provides a comprehensive **visualization** of the task assignment process in a simulated environment. It assigns computational tasks to nodes (Edge or Cloud) while minimizing the overall cost of execution, adhering to resource constraints, and dynamically updating the allocations.

---

## **Project Structure**

### 1. **`main.py`**
This is the entry point of the project. It orchestrates the task allocation and visualization by calling functions from the other modules.

#### **Key Responsibilities:**
- **Generate Problem Setup:**
  - Dynamically creates tasks, edge nodes, cloud nodes, and costs for task-node assignments using the `generate_problem()` function from `ilp_solver.py`.
  
- **Solve ILP Iteratively:**
  - Allocates tasks to nodes in a step-by-step manner using `solve_iterative_ilp()`, taking into account dynamic capacity constraints of nodes.
  
- **Build Network Graph:**
  - Constructs a task-node graph using `build_graph()` to visually represent task assignments.
  
- **Visualization:**
  - Uses the `animate_solution_iterative()` function from `visualization.py` to show the allocation process step-by-step with:
    - A dynamic **network graph**.
    - A **task execution timeline** (Gantt chart).
    - A **cost heatmap**.
    - A **node utilization graph**.
    - A **progress bar** to track the allocation process.

---

### 2. **`ilp_solver.py`**
This module contains functions to solve the ILP and generate problem data.

#### **Key Functions:**

1. **`generate_problem(num_tasks, num_edge_nodes, num_cloud_nodes, connection_probability=0.8)`**
   - Randomly generates:
     - A list of tasks (`Task_1`, `Task_2`, ...).
     - A set of edge and cloud nodes (`Edge_1`, `Cloud_1`, ...).
     - A cost matrix representing the cost of assigning each task to each node, with a probability of task-node connectivity.

2. **`solve_ilp(tasks, edge_nodes, cloud_nodes, costs)`**
   - Solves a single instance of the ILP problem to minimize the total cost of task assignment while ensuring:
     - Each task is assigned to exactly one node.
     - Node capacities are respected.

3. **`solve_iterative_ilp(tasks, edge_nodes, cloud_nodes, costs, capacities, task_execution_times)`**
   - Iteratively solves the ILP problem, dynamically updating node capacities and tracking task execution times.

4. **`build_graph(tasks, edge_nodes, cloud_nodes, allocation, costs)`**
   - Builds a network graph using **NetworkX** to represent tasks, nodes, and their allocations.

---

### 3. **`visualization.py`**
This module visualizes the ILP solution and provides insights into the task allocation process.

#### **Key Functions:**

1. **`create_positions(tasks, edge_nodes, cloud_nodes)`**
   - Generates node positions for the network graph using a circular or custom layout.

2. **`animate_solution_iterative(G, allocation_sequence, tasks, edge_nodes, cloud_nodes, task_execution_times, costs)`**
   - Creates an interactive animation that includes:
     - **Network Graph:** Shows dynamic task-node assignments and edge costs.
     - **Progress Bar:** Tracks the overall allocation progress.
     - **Task Execution Timeline:** A Gantt chart visualizing when tasks are executed.
     - **Node Resource Utilization:** Displays the number of tasks allocated to each node.
     - **Cost Heatmap:** Highlights the cost matrix for task-node assignments.

---

## **How It Works**

1. **Problem Generation:**
   - `main.py` generates tasks, nodes, and their associated costs using `generate_problem()`. Each task is connected to certain nodes with a probability, and costs are assigned randomly within a range.

2. **Task Allocation:**
   - The ILP solver iteratively assigns tasks to nodes while minimizing the total cost and respecting capacity constraints. The solver dynamically adjusts the node capacities after each allocation step.

3. **Visualization:**
   - The visualization module dynamically updates the graph to reflect task assignments and provides insights into task execution timelines, costs, and resource utilization.

---

## **Demo Visualization Features**

- **Network Graph:**
  - Nodes are color-coded:
    - **Orange** for tasks.
    - **Blue** for edge nodes.
    - **Green** for cloud nodes.
  - Allocated tasks are labeled dynamically.
  - Edge annotations display the cost of assignment.

- **Progress Bar:**
  - A thin blue line at the top tracks the number of tasks allocated.

- **Task Execution Timeline:**
  - A Gantt chart visualizes when each task is executed and its assigned node type.

- **Node Resource Utilization:**
  - A bar chart shows the number of tasks allocated to each node.

- **Cost Heatmap:**
  - A heatmap displays the cost matrix, where lower costs are shown in blue and higher costs in red.

---

## **Requirements**

- Python 3.x
- Libraries:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `networkx`
  - `pulp`

---

## **How to Run**

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>

