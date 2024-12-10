# Author : Aakash Kardam
# Student PhD CIS
# UMASS DARTMOUTH

import pandas as pd
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import plotly.graph_objects as go
from mpl_interactions import panhandler, zoom_factory
import plotly.graph_objects as go
from mpl_interactions import panhandler, zoom_factory
from matplotlib.animation import FuncAnimation
import numpy as np
plt.rc('font', size=5)


def create_positions(tasks, edge_nodes, cloud_nodes, layout="circular"):
    """Create custom positions for tasks, edge nodes, and cloud nodes."""
    if layout == "spring":
        G = nx.Graph()
        G.add_nodes_from(tasks + edge_nodes + cloud_nodes)
        return nx.spring_layout(G, seed=42)
    elif layout == "circular":
        return nx.circular_layout(tasks + edge_nodes + cloud_nodes)
    elif layout == "kamada_kawai":
        G = nx.Graph()
        G.add_nodes_from(tasks + edge_nodes + cloud_nodes)
        return nx.kamada_kawai_layout(G)
    else:
        # Default to a simple custom layout
        pos = {}
        for i, task in enumerate(tasks):
            pos[task] = (i, 3)
        for i, edge in enumerate(edge_nodes):
            pos[edge] = (i, 1.5)
        for i, cloud in enumerate(cloud_nodes):
            pos[cloud] = (i, 0)
        return pos


def annotate_node_details(G, allocation, tasks, edge_nodes, cloud_nodes, capacities):
    """Update node annotations to show details dynamically."""
    allocated_tasks = {alloc[0] for alloc in allocation}  # Extract allocated tasks
    for node in G.nodes:
        if node in tasks:
            G.nodes[node]["detail"] = "Allocated" if node in allocated_tasks else "Unallocated"
        elif node in edge_nodes + cloud_nodes:
            remaining_capacity = capacities[node]
            G.nodes[node]["detail"] = f"Capacity: {remaining_capacity}"



def animate_solution(G, allocation, tasks, edge_nodes, cloud_nodes, total_cost, layout="spring"):
    """Visualize the solution with an animated graph."""
    capacities = {node: 5 for node in edge_nodes + cloud_nodes}  # Assume all nodes start with capacity 5
    pos = create_positions(tasks, edge_nodes, cloud_nodes, layout=layout)
    edges = list(allocation.keys())
    node_colors = [
        "orange" if "Task" in node else "blue" if "Edge" in node else "green" for node in G.nodes
    ]
    timeline_colors = {"Edge": "cyan", "Cloud": "magenta"}

    # Animation setup
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [3, 1]})

    def update(frame):
        ax1.clear()
        ax2.clear()

        # Draw the graph with current allocations
        current_edges = edges[:frame + 1]

        # Update node capacities dynamically
        for task, resource in current_edges:
            capacities[resource] -= 1  # Decrease capacity for each allocation
        annotate_node_details(G, allocation, tasks, edge_nodes, cloud_nodes, capacities)

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax1, node_color=node_colors, node_size=700)
        nx.draw_networkx_labels(G, pos, ax=ax1, font_size=10)

        # Annotate node details
        for node, (x, y) in pos.items():
            ax1.text(
                x, y - 0.15,  # Offset annotation to avoid overlap
                G.nodes[node].get("detail", ""),
                fontsize=8,
                horizontalalignment="center",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray", boxstyle="round,pad=0.2")
            )

        # Draw edges
        for idx, edge in enumerate(current_edges):
            color = "cyan" if "Edge" in edge[1] else "magenta"
            nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color=color, ax=ax1, width=2)
            edge_label = f"${G.edges[edge]['cost']}"
            nx.draw_networkx_edge_labels(G, pos, edge_labels={edge: edge_label}, font_size=8, ax=ax1)

        ax1.set_title(f"ILP Task Allocation - Step {frame + 1}/{len(edges)} (Cost: {total_cost})")
        ax1.axis('off')

        # Update task execution timeline
        for idx, (task, resource) in enumerate(current_edges):
            resource_type = "Edge" if "Edge" in resource else "Cloud"
            ax2.barh(task, 1, left=idx, color=timeline_colors[resource_type])

        # Scale timeline dynamically
        ax2.set_yticks(range(len(tasks)))
        ax2.set_yticklabels(tasks, fontsize=max(6, 12 - len(tasks) // 5))  # Adjust font size dynamically
        ax2.set_xlabel("Time Steps")
        ax2.set_title("Task Execution Timeline")

    ani = animation.FuncAnimation(fig, update, frames=len(edges), interval=1000, repeat=False)
    plt.show()



def update_node_status(G, capacities, task_completion):
    """Update node colors and details dynamically."""
    for node in G.nodes:
        if "Edge" in node or "Cloud" in node:  # Only check resource nodes
            if capacities[node] == 0:
                G.nodes[node]["color"] = "grey"
                G.nodes[node]["detail"] = "Unavailable"
            else:
                G.nodes[node]["color"] = "blue" if "Edge" in node else "green"
                G.nodes[node]["detail"] = f"Capacity: {capacities[node]}"

        # Reactivate nodes if tasks complete
        if node in task_completion:
            capacities[node] += 1  # Free up capacity
            del task_completion[node]  # Remove task from completion tracking


def animate_solution_iterative(
    G, allocation_sequence, tasks, edge_nodes, cloud_nodes, task_execution_times, costs
):
    """Visualization with line progress bar at the top and adjusted layout for better spacing."""
    capacities = {node: 5 for node in edge_nodes + cloud_nodes}  # Initial capacities
    task_completion = {}  # Track task completion times for resources
    total_tasks = len(tasks)
    pos = create_positions(tasks, edge_nodes, cloud_nodes)
    timeline_colors = {"Edge": "blue", "Cloud": "green"}

    # Node colors
    node_colors = {node: "orange" for node in tasks}
    node_colors.update({node: "blue" for node in edge_nodes})
    node_colors.update({node: "green" for node in cloud_nodes})

    # Prepare static heatmap data
    cost_matrix = pd.DataFrame(0, index=tasks, columns=edge_nodes + cloud_nodes)
    for (task, node), cost in costs.items():
        cost_matrix.loc[task, node] = cost

    # Initialize figure
    fig = plt.figure(figsize=(30, 20))  # Larger figure size for better spacing
    grid = fig.add_gridspec(10, 8, hspace=1.5, wspace=1.5)  # Adjusted padding

    # Subplots
    ax_progress = fig.add_subplot(grid[0, :6])  # Line progress bar at the top
    ax_main = fig.add_subplot(grid[1:8, :6])  # Main graph (extended vertically)
    ax_timeline = fig.add_subplot(grid[8:10, :6])  # Gantt chart (pushed further down)
    ax_utilization = fig.add_subplot(grid[0:4, 6:])  # Node utilization chart
    ax_heatmap = fig.add_subplot(grid[5:9, 6:])  # Heatmap

    def update(frame):
        ax_main.clear()
        ax_timeline.clear()
        ax_progress.clear()
        ax_utilization.clear()

        # Process completed tasks
        for node, remaining_time in list(task_completion.items()):
            task_completion[node] -= 1
            if task_completion[node] == 0:
                capacities[node] += 1
                del task_completion[node]

        # Allocate next task
        if frame < len(allocation_sequence):
            task, resource = allocation_sequence[frame]
            capacities[resource] -= 1  # Decrease capacity
            task_completion[resource] = task_execution_times[task]  # Track execution time

        # Update graph node statuses
        annotate_node_details(G, allocation_sequence[:frame + 1], tasks, edge_nodes, cloud_nodes, capacities)

        # Draw main graph
        nx.draw_networkx_nodes(G, pos, ax=ax_main, node_color=[node_colors[node] for node in G.nodes], node_size=600)
        nx.draw_networkx_labels(G, pos, ax=ax_main)
        for node, (x, y) in pos.items():
            ax_main.text(
                x, y - 0.2,
                G.nodes[node].get("detail", ""),
                fontsize=8,
                horizontalalignment="center",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray", boxstyle="round,pad=0.2")
            )
        current_edges = allocation_sequence[:frame + 1]
        nx.draw_networkx_edges(G, pos, edgelist=current_edges, edge_color="cyan", ax=ax_main, width=2)
        edge_labels = {(task, resource): f"${G.edges[(task, resource)]['cost']}" for task, resource in current_edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax_main)

        # Cumulative cost
        cumulative_cost = sum(G.edges[edge]["cost"] for edge in current_edges)
        ax_main.set_title(f"ILP Task Allocation - Step {frame + 1}/{len(allocation_sequence)} (Cost: ${cumulative_cost})")
        ax_main.axis("off")

        # Task execution timeline (Gantt chart)
        for idx, (task, resource) in enumerate(current_edges):
            resource_type = "Edge" if "Edge" in resource else "Cloud"
            ax_timeline.barh(task, 1, left=idx, color=timeline_colors[resource_type])
            ax_timeline.text(
                idx + 0.5, task, task, va="center", ha="center", color="white", fontsize=8
            )  # Annotate task names
        ax_timeline.grid(axis="both", linestyle="--", alpha=0.7)  # Full grid
        ax_timeline.set_yticks([])  # Remove cluttered y-axis
        ax_timeline.set_xlabel("Time Steps")
        ax_timeline.set_title("Task Execution Timeline")

        # Line progress bar at the top
        allocated_tasks = len(current_edges)
        progress = allocated_tasks / total_tasks
        ax_progress.plot([0, progress], [0, 0], color="blue", linewidth=3)  # Line progress indicator
        ax_progress.set_xlim(0, 1)
        ax_progress.set_ylim(-0.1, 0.1)  # Thin line space
        ax_progress.axis("off")
        ax_progress.set_title(f"Progress: {allocated_tasks}/{total_tasks}", fontsize=12, pad=5)

        # Node utilization chart
        utilization = {node: 5 - capacities[node] for node in edge_nodes + cloud_nodes}
        ax_utilization.bar(utilization.keys(), utilization.values(), color="green")
        ax_utilization.set_ylim(0, 5)
        ax_utilization.set_title("Node Resource Utilization")
        ax_utilization.set_ylabel("Tasks Allocated")
        ax_utilization.set_xlabel("Nodes")
        ax_utilization.tick_params(axis="x", rotation=45)  # Rotate x-axis labels

        # Static heatmap (No resizing or redrawing of color scale)
        sns.heatmap(
            cost_matrix, ax=ax_heatmap, annot=True, cmap="coolwarm", fmt=".0f", cbar=False,
            linewidths=0.5, linecolor="white", square=True
        )
        ax_heatmap.set_title("Cost Matrix Heatmap")
        ax_heatmap.set_xlabel("Nodes")
        ax_heatmap.set_ylabel("Tasks")
        ax_heatmap.tick_params(axis="x", rotation=45)  # Rotate x-axis labels

    ani = animation.FuncAnimation(fig, update, frames=len(allocation_sequence), interval=1000, repeat=True)
    plt.show()


def animate_solution_iterative1(G, allocation_sequence, tasks, edge_nodes, cloud_nodes, task_execution_times, costs):
    """Enhanced visualization with progress bar, heatmap, and utilization tracking."""
    capacities = {node: 5 for node in edge_nodes + cloud_nodes}  # Initial capacities
    task_completion = {}  # Track task completion times for resources
    total_tasks = len(tasks)
    pos = create_positions(tasks, edge_nodes, cloud_nodes)
    timeline_colors = {"Edge": "cyan", "Cloud": "magenta"}

    # Node colors
    node_colors = {node: "orange" for node in tasks}
    node_colors.update({node: "blue" for node in edge_nodes})
    node_colors.update({node: "green" for node in cloud_nodes})

    # Initialize figure with multiple panels
    fig = plt.figure(figsize=(16, 12))
    grid = fig.add_gridspec(3, 3)
    ax1 = fig.add_subplot(grid[0:2, :])  # Main graph
    ax2 = fig.add_subplot(grid[2, 0])    # Gantt chart
    ax3 = fig.add_subplot(grid[2, 1])    # Progress bar
    ax4 = fig.add_subplot(grid[2, 2])    # Node utilization chart

    def update(frame):
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()

        # Process completed tasks
        for node, remaining_time in list(task_completion.items()):
            task_completion[node] -= 1
            if task_completion[node] == 0:
                capacities[node] += 1
                del task_completion[node]

        # Allocate next task
        if frame < len(allocation_sequence):
            task, resource = allocation_sequence[frame]
            capacities[resource] -= 1  # Decrease capacity
            task_completion[resource] = task_execution_times[task]  # Track execution time

        # Update graph node statuses
        annotate_node_details(G, allocation_sequence[:frame + 1], tasks, edge_nodes, cloud_nodes, capacities)

        # Draw main graph
        nx.draw_networkx_nodes(G, pos, ax=ax1, node_color=[node_colors[node] for node in G.nodes], node_size=500)
        nx.draw_networkx_labels(G, pos, ax=ax1)
        for node, (x, y) in pos.items():
            ax1.text(
                x, y - 0.2,
                G.nodes[node].get("detail", ""),
                fontsize=8,
                horizontalalignment="center",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray", boxstyle="round,pad=0.2")
            )
        current_edges = allocation_sequence[:frame + 1]
        nx.draw_networkx_edges(G, pos, edgelist=current_edges, edge_color="cyan", ax=ax1, width=2)
        edge_labels = {(task, resource): f"${G.edges[(task, resource)]['cost']}" for task, resource in current_edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax1)

        # Cumulative cost
        cumulative_cost = sum(G.edges[edge]["cost"] for edge in current_edges)
        ax1.set_title(f"ILP Task Allocation - Step {frame + 1}/{len(allocation_sequence)} (Cost: ${cumulative_cost})")
        ax1.axis("off")

        # Task execution timeline (Gantt chart)
        for idx, (task, resource) in enumerate(current_edges):
            resource_type = "Edge" if "Edge" in resource else "Cloud"
            ax2.barh(task, 1, left=idx, color=timeline_colors[resource_type])
        ax2.grid(axis="x", linestyle="--", alpha=0.7)
        ax2.set_yticks(range(len(tasks)))
        ax2.set_yticklabels(tasks, fontsize=8)
        ax2.set_xlabel("Time Steps")
        ax2.set_title("Task Execution Timeline")

        # Progress bar
        allocated_tasks = len(current_edges)
        ax3.barh(0, allocated_tasks / total_tasks, color="blue")
        ax3.set_xlim(0, 1)
        ax3.set_yticks([])
        ax3.set_title(f"Progress: {allocated_tasks}/{total_tasks} Tasks Allocated")

        # Node utilization chart
        utilization = {node: 5 - capacities[node] for node in edge_nodes + cloud_nodes}
        ax4.bar(utilization.keys(), utilization.values(), color="green")
        ax4.set_ylim(0, 5)
        ax4.set_title("Node Resource Utilization")
        ax4.set_ylabel("Tasks Allocated")
        ax4.set_xlabel("Nodes")

    ani = animation.FuncAnimation(fig, update, frames=len(allocation_sequence), interval=1000, repeat=True)
    plt.show()