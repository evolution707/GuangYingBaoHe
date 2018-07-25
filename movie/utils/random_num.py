# -*- coding=utf-8 -*-
import random
def randomNum():
    li = []
    n = 0
    while n <= 8:
        r = random.randint(0, 9)
        li.append(r)
        if li[0] == 0:
            li[0] = random.randint(1, 9)
        n += 1
    num = int(''.join(map(str, li)))
    return num