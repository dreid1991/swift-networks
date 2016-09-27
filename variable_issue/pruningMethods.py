import sys
sys.path.append('/home/danielreid/auxetic/core/util_py/')
sys.path.append('/home/danielreid/auxetic/core/python/')
from measureModuli import *
from updatesStd import *
from random import random
import math
import copy

def getChangeInEngShearSingle(state, benderIdx):
    init = measureShearStresses(state, -3, -13, -.00001, shearType=1, isBending=True, postTransform=updateCompress)
    initialEng = sum(init)
    bond = state.bendingBonds[benderIdx]
    state.setBendingBondActive(bond, False)
    final = measureShearStresses(state, -3, -13, -.00001, shearType=1, isBending=True, postTransform=updateCompress)
    changeInEng = initialEng - sum(final)
    state.setBendingBondActive(bond, True)

    return changeInEng


def getShearStresses(state):
    return list(measureShearStresses(state, -3, -13, -.00001, shearType=1, isBending=True, postTransform=updateCompress))






