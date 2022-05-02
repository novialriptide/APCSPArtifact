from typing import List
import pygame
import sys
import numpy
import math

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

class Graph:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._nodes = []

        for h in range(height):
            for w in range(width):
                self._nodes.append(Node(numpy.array([w, h])))

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    def set_barrier(self, pos: numpy.array) -> None:
        self._nodes[self.get_node_index(pos)].barrier = True

    def get_node_index(self, pos: numpy.array) -> Node:
        i = 0
        for n in self.nodes:
            if n.pos[0] == pos[0] and n.pos[1] == pos[1]:
                return i
            i += 1

        return None

    def get_node(self, pos: numpy.array) -> Node:
        for n in self.nodes:
            if n.pos[0] == pos[0] and n.pos[1] == pos[1]:
                return n

        return None

    def get_neighbor_nodes(self, node: Node) -> List[Node]:
        possible_neighbors = [
            {"offset": numpy.array([-1, 0]), "corner": False},
            {"offset": numpy.array([1, 0]), "corner": False},
            {"offset": numpy.array([0, -1]), "corner": False},
            {"offset": numpy.array([0, 1]), "corner": False},
        ]

        neighbors = []

        for p in possible_neighbors:
            neighbor_node = self.get_node(p["offset"] + node.pos)
            if neighbor_node is not None and not neighbor_node.barrier:
                neighbors.append(
                    {
                        "node": neighbor_node,
                        "corner": p["corner"],
                        "offset": p["offset"],
                    }
                )

        return neighbors

    def _reconstruct_path(self, came_from, current) -> None:
        total_path = [current]

        while current in came_from:
            current = came_from[current]
            total_path.append(current)

        total_path.reverse()
        return total_path

    def get_path(self, start: numpy.array, end: numpy.array, barriers=[]):
        for b in barriers:
            self.set_barrier(b)
        
        start = self.get_node(start)
        end = self.get_node(end)

        open_nodes = [start]
        closed_nodes = []
        came_from = {}

        start.f = 0
        start.g = 0

        while len(open_nodes) != 0:
            def compare(e: Node) -> float:
                return e.f

            open_nodes.sort(key=compare)
            current = open_nodes[0]
            if current == end:
                return self._reconstruct_path(came_from, current)

            open_nodes.remove(current)
            closed_nodes.append(current)

            for neighbor in self.get_neighbor_nodes(current):
                neighbor = neighbor["node"]
                if neighbor in closed_nodes:
                    continue

                tentative_g_score = current.g + current.get_node_dist(neighbor)
                if neighbor not in open_nodes or tentative_g_score < neighbor.g:
                    came_from[neighbor] = current
                    neighbor.g = tentative_g_score
                    neighbor.f = neighbor.g + neighbor.h
                    if neighbor not in open_nodes:
                        open_nodes.append(neighbor)

        raise Exception("Cannot find path")

    def print_visual(self) -> None:
        lines = []

        for h in range(self.height):
            line = ""
            for w in range(self.width):
                node = self.get_node(numpy.array([w, h]))
                if node.barrier:
                    line += "# "
                if not node.barrier:
                    line += f"{math.ceil(node.g)} "

            lines.append(line)

        for l in lines:
            print(l)


def move_towards(origin: numpy.array, target: numpy.array, distance: float):
    delta = target - origin
    dist = numpy.linalg.norm(delta)

    if dist <= distance or dist == 0:
        return target

    return origin + delta / dist * distance

g = Graph(20, 20)

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((640, 640))
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

howto_text = font.render("Hover over the screen to create barriers", False, (0, 0, 0))

block_pos = (2, 1)
block_length = 25

rects = []

for n in g.nodes:
    rects.append(
        {
            "rect": pygame.Rect(
                n.pos[0] * block_length,
                n.pos[1] * block_length,
                block_length,
                block_length,
            ),
            "color": (255, 255, 255),
            "node": n,
        }
    )

start_pos = numpy.array([2, 1])
end_pos = numpy.array([15, 17])
path = g.get_path(start_pos, end_pos)
next_path = 0
ms_to_next_path = 1000
next_tile = 0

entity = pygame.Rect(start_pos * block_length, (block_length, block_length))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    new_pos = numpy.asarray(path[next_tile].pos) * block_length
    entity.topleft = move_towards(numpy.asarray(entity.topleft), new_pos, 3)
    if entity.topleft[0] == new_pos[0] and entity.topleft[1] == new_pos[1]:
        next_tile += 1
    elif next_tile == len(path) - 1:
        next_tile = 0
        entity.topleft = start_pos.tolist()
        path = g.get_path(start_pos, end_pos)

    for r in rects:
        if r["node"].barrier:
            color = (100, 0, 0)
        else:
            color = (255, 255, 255)

        if r["node"] in path:
            color = (0, 255, 0)

        pygame.draw.rect(
            screen,
            color,
            r["rect"],
        )

        if r["rect"].collidepoint(pygame.mouse.get_pos()):
            g.set_barrier(r["node"].pos)

    pygame.draw.rect(screen, (100, 100, 100), entity)
    
    screen.blit(howto_text, (0, 0))

    pygame.display.update()
    pygame.display.set_caption(f"astarpy (fps: {clock.get_fps()})")
    clock.tick(0)
