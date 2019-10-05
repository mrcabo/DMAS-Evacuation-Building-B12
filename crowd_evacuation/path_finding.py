import numpy as np
import itertools
import networkx as nx

from crowd_evacuation.agents import WallAgent, FireAgent


def euc_dist(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def create_graph(model):
    height = model.grid.height
    width = model.grid.width
    # Creating a 2D grid-like graph, each node represents a position
    # xv, yv = np.meshgrid(np.arange(0, width), np.arange(0, height))
    cell_list = list(itertools.product(np.arange(0, width, 1), np.arange(0, height, 1)))
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

    # Now we remove the nodes that are not walkable (walls, fire etc...)
    for agent in model.grid.iter_cell_list_contents(cell_list):
        if isinstance(agent, WallAgent):
            graph.remove_node(tuple(agent.pos))

    # graph = nx.grid_graph(dim=[5, 5])  # 5x5 grid
    # nx.draw(graph)
    # plt.show()

    return graph


def update_graph(model):
    graph = model.graph
    return graph


def find_path(graph, start, target):
    # A* algorithm
    best_path = None
    try:
        best_path = nx.astar_path(graph, start, target, heuristic=euc_dist, weight='cost')
    except nx.NetworkXNoPath:
        pass
        # print("Node {} not reachable from {}".format(target, start))
    # except:
    #     print()
    return best_path
