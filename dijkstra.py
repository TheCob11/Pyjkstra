from dataclasses import dataclass, field
from math import inf
import networkx as nx
from matplotlib import pyplot as plt, animation, figure
from queue import PriorityQueue
from typing import Callable
from time import time
from random import randint


@dataclass(order=True)
class Route:
    node: int = field(compare=False)
    score: int = inf
    through: int = field(default=None, compare=False)

@dataclass
class AnimFunc(Callable):
    labels: list
    edge: tuple
    node: int
    G: nx.Graph
    def __call__(self) -> list:
        changes: list = []
        changes.append(nx.draw_networkx_nodes(
            G, G.pos, nodelist=[self.node], label=self.node, node_color="#00ff00"))
        changes.append(nx.draw_networkx_edges(
            G, G.pos, [self.edge], edge_color="#0000ff"))
        changes += list(nx.draw_networkx_edge_labels(
            G, G.pos, self.labels, .9, font_color="#00ff00").values())
        return changes

def dijkstra(G: nx.Graph, start: int, anim: list[Callable] | None = None) -> dict[int, Route]:
    q: PriorityQueue[Route] = PriorityQueue()
    done: set[int] = set()
    full_route: dict[int, Route] = {i: Route(i, inf, i) for i in G.nodes}
    q.put(Route(start, 0, start))
    while len(done) < len(G.nodes):
        curr: Route = q.get()
        if curr.node in done:
            continue
        for i in G.adj[curr.node]:
            if i not in done:
                q.put(
                    Route(i, curr.score+G.edges[curr.node, i]["weight"], curr.node))
                if anim is not None:
                    anim.append(AnimFunc(
                        {(i.node, i.through): i.score for i in full_route.values()},
                        (curr.node, i),
                        curr.node,
                        G))
        done.add(curr.node)
        if curr < full_route[curr.node]:
            full_route[curr.node] = curr
    if anim is not None:
        anim.append(AnimFunc(
            {(i.node, i.through): i.score for i in full_route.values()},
            (curr.node, i),
            curr.node,
            G))
    return full_route


def draw(data: Callable):
    fig.clf(True)
    init_draw()
    return data()


def init_draw() -> None:
    nx.draw_networkx(G, G.pos)
    nx.draw_networkx_edge_labels(G, G.pos, edge_labels=edge_weights)

if __name__ == "__main__":
    # G: nx.Graph = nx.Graph([
    #     ("A", "B", {"weight": 7}),
    #     ("A", "C", {"weight": 3}),
    #     ("A", "D", {"weight": 5}),
    #     ("B", "E", {"weight": 3}),
    #     ("C", "B", {"weight": 4}),
    #     ("C", "F", {"weight": 3}),
    #     ("D", "F", {"weight": 2}),
    #     ("F", "E", {"weight": 3})
    # ])
    G: nx.Graph = nx.fast_gnp_random_graph(10,.4)
    # G = nx.convert_node_labels_to_integers(G)
    G.pos: dict = nx.spring_layout(G)
    nx.set_edge_attributes(G, {i: randint(3,7) for i in G.edges}, "weight")
    edge_weights: dict = nx.get_edge_attributes(G, "weight")
    plt.gcf().set_size_inches((16,8))
    init_draw()
    plt.show()
    animation_data: list[Callable] = []
    route: dict[int, Route] = dijkstra(G, 0, animation_data)
    print(route)
    fig: figure.Figure = plt.figure(figsize=(16, 8))
    ani: animation.FuncAnimation = animation.FuncAnimation(
        plt.gcf(), draw, animation_data, interval=250, blit=True, repeat=False)
    if(input("y for save? ").lower() == "y"):
        ani.save(f"dijkstra-{time()}.mp4")
    plt.show(block=True)
    plt.close()
