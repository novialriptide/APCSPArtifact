import math
import numpy


class Node:
    def __init__(self, pos: numpy.array) -> None:
        self.pos = pos

        """
        G is the distance between the current node and the start node.
        H is the heuristic — estimated distance from the current node to the end node.
        """
        self.g = 0
        self.h = 0
        self.f = 0

        self.barrier = False

    def get_node_dist(self, node) -> None:
        return math.sqrt(
            (self.pos[0] - node.pos[0]) ** 2 + (self.pos[1] - node.pos[1]) ** 2
        )

    def __str__(self) -> str:
        return f"Node({self.pos[0]}, {self.pos[1]}, isbarrier: {self.barrier})"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __o) -> bool:
        if __o is None:
            return False

        return self.pos[0] == __o.pos[0] and self.pos[1] == __o.pos[1]
