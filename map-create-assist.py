from random import choice
from map import *

def random_map(x, y, choose):
    toprint = ""
    for i in range(0, y):
        toprint += "["
        for j in range(0, x):
            toprint += choice(choose) + ", "
        toprint += choice(choose)
        toprint += "],\n"
    return toprint

def filler(filled, choose, map):
    for i in range(0, len(map)):
        for j in range(0, len(map[i])):
            if map[i][j] == filled:
                map[i][j] = choice(choose)
    return map

# a = filler(bb, ["b1", "b2", "b3"], s)
# b = filler(zz, ["p1", "p2", "p3"], a)
# c = filler(rr, ["r1", "r2", "r3", "r4"], b)

print(random_map(40, 40, ["v1", "v2", "v3", "v4", "g1", "g2", "g3", "g4", "w1", "w2", "w3", "w4", "l1", "l2", "l3", "b1", "b2", "b3", "sk", "r1", "r2", "r3", "r4", "p1", "p2", "p3"]))
