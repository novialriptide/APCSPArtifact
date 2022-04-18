import numpy


def move_towards(origin: numpy.array, target: numpy.array, distance: float):
    delta = target - origin
    dist = numpy.linalg.norm(delta)

    if dist <= distance or dist == 0:
        return target

    return origin + delta / dist * distance
