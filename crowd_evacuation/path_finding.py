from heapq import heappush, heappop
from itertools import count, product

import numpy as np
import networkx as nx

from crowd_evacuation.wall_agent import WallAgent


def euc_dist(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def create_graph(model):
    height = model.grid.height
    width = model.grid.width
    # Creating a 2D grid-like graph, each node represents a position
    graph = nx.grid_graph(dim=[height, width])
    # Adding diagonal connectivity
    for row in range(0, height - 1):
        for col in range(0, width):
            if col == 0:  # Only connectivity to the upper right
                graph.add_edge((row, col), (row + 1, col + 1))
            elif col == (width - 1):  # Only connectivity to the upper left
                graph.add_edge((row, col), (row + 1, col - 1))
            else:
                graph.add_edge((row, col), (row + 1, col - 1))
                graph.add_edge((row, col), (row + 1, col + 1))

    # Now we remove the nodes that are not walkable (walls)
    cell_list = list(product(np.arange(0, width, 1), np.arange(0, height, 1)))
    for agent in model.grid.iter_cell_list_contents(cell_list):
        if isinstance(agent, WallAgent):
            graph.remove_node(tuple(agent.pos))

    for node in graph.nodes:
        graph.nodes[node]["walkable"] = True

    return graph


def astar_path(G, source, target, heuristic=None, weight='weight'):
    """Returns a list of nodes in a shortest path between source and target
    using the A* ("A-star") algorithm.

    There may be more than one shortest path.  This returns only one.

    Small tweaks from the original func: https://networkx.github.io/documentation/latest/reference/algorithms/generated/networkx.algorithms.shortest_paths.astar.astar_path.html

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    heuristic : function
       A function to evaluate the estimate of the distance
       from the a node to the target.  The function takes
       two nodes arguments and must return a number.

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    """
    if source not in G or target not in G:
        msg = 'Either source {} or target {} is not in G'
        raise nx.NodeNotFound(msg.format(source, target))

    if heuristic is None:
        # The default heuristic is h=0 - same as Dijkstra's algorithm
        def heuristic(u, v):
            return 0

    push = heappush
    pop = heappop

    # The queue stores priority, node, cost to reach, and parent.
    # Uses Python heapq to keep in priority order.
    # Add a counter to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guaranteed unique for all nodes in the graph.
    c = count()
    queue = [(0, next(c), source, 0, None)]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued = {}
    # Maps explored nodes to parent closest to the source.
    explored = {}

    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent = pop(queue)

        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            return path

        if curnode in explored:
            continue

        explored[curnode] = parent

        for neighbor, w in G[curnode].items():
            if not G.nodes[neighbor]["walkable"]:
                continue
            else:
                if neighbor in explored:
                    continue
                ncost = dist + w.get(weight, 1)
                if neighbor in enqueued:
                    qcost, h = enqueued[neighbor]
                    # if qcost less than ncost, a less costly path from the
                    # neighbor to the source was already determined.
                    # Therefore, we won't attempt to push this neighbor
                    # to the queue
                    if qcost <= ncost:
                        continue
                else:
                    h = heuristic(neighbor, target)
                enqueued[neighbor] = ncost, h
                push(queue, (ncost + h, next(c), neighbor, ncost, curnode))

    raise nx.NetworkXNoPath("Node %s not reachable from %s" % (source, target))


def find_path(graph, start, target, non_walkable=[]):
    """
    Finds the optimal path between start and target, avoiding nodes in non_walkable.

    Args:
        graph (nx.Graph): Graph that represents the grid spaces.
        start (tuple): Starting position
        target (tuple): Target position
        non_walkable (List): List of positions where agent shouldn't walk through

    Returns:
        (List): Optimal path. None when no path is found.

    """
    # We restrict paths that would go through non_walkable spaces
    for node in non_walkable:
        graph.nodes[node]["walkable"] = False

    try:
        # A* algorithm
        best_path = astar_path(graph, start, target, heuristic=euc_dist)
    except nx.NetworkXNoPath:
        best_path = None

    # Undo the operation (other agents will move making the previous non-walkable spaces available again)
    for node in non_walkable:
        graph.nodes[node]["walkable"] = True

    return best_path
