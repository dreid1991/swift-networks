class PoissonModule:
    def __init__(self, state, leftGroup, rightGroup):
        self.leftGroup = leftGroup
        self.rightGroup = rightGroup
        self.state = state
        self.beforeMeasured = False
    def readPositions(self):
        xsLeft = []
        xsRight = []
        rightAtoms = self.state.selectGroup(self.rightGroup)
        leftAtoms = self.state.selectGroup(self.leftGroup)
        for i in range(len(leftAtoms)):
            xsLeft.append(leftAtoms[i].pos[0])
        for i in range(len(rightAtoms)):
            xsRight.append(rightAtoms[i].pos[0])
        return xsLeft, xsRight
    def measureBefore(self):
        xsLeft, xsRight = self.readPositions()
        self.xsLeftOrig = xsLeft
        self.xsRightOrig = xsRight
    def poissonsRatio(self):
        leftAvgOrig, rightAvgOrig = sum(self.xsLeftOrig)/len(self.xsLeftOrig), sum(self.xsRightOrig)/len(self.xsRightOrig)
        dxo = rightAvgOrig - leftAvgOrig

        xsLeft, xsRight = self.readPositions()
        leftAvgNew, rightAvgNew = sum(xsLeft)/len(xsLeft), sum(xsRight)/len(xsRight)
        dxf = rightAvgNew - leftAvgNew
        return dxf/dxo


