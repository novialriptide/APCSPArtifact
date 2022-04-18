import pygame
import sys
import numpy
from graph import Graph
from move_towards import move_towards

g = Graph(20, 20)

pygame.init()
screen = pygame.display.set_mode((640, 640))
clock = pygame.time.Clock()

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
path = g.get_path(start_pos, numpy.array([15, 17]))
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
        path = g.get_path((2, 1), (15, 17))

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

    pygame.display.update()
    pygame.display.set_caption(f"astarpy (fps: {clock.get_fps()})")
    clock.tick(0)
