"""
[SOVEREIGN FORGE] Algorithmic Python Synthesis
"""
import collections
from typing import List, Dict, Set

class DAGEngine:
    def __init__(self):
        self.graph: Dict[str, List[str]] = collections.defaultdict(list)
        self.in_degree: Dict[str, int] = collections.defaultdict(int)

    def add_dependency(self, u: str, v: str):
        self.graph[u].append(v)
        self.in_degree[v] += 1
        if u not in self.in_degree:
            self.in_degree[u] = 0

    def topological_sort(self):
        queue = [node for node in self.in_degree if self.in_degree[node] == 0]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in self.graph[node]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if len(order) != len(self.in_degree):
            raise ValueError('Cycle detected in DAG!')
        return order



