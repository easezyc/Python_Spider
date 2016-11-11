# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 18:53:45 2016

@author: zhuyongchun
"""
import random
def conflict(state,nextX):
    nextY=len(state)
    for i in range(nextY):
        if abs(state[i]-nextX) in (0,nextY-i):
            return True
    return False
    
def queens(num=8,state=()):
    for pos in range(num):
        if not conflict(state,pos):
            if len(state)==num-1:
                yield (pos,)
            else:
                for result in queens(num,state+(pos,)):
                    yield (pos,)+result
     
def line(pos,solution):
    length=len(solution)
    print('. '*(pos)+'X'+'. '*(length-pos-1))
               
def prettyprint(solution):
    for pos in solution:
        line(pos,solution)
      


r=random.choice(list(queens(8)))
print(r)
prettyprint(r)