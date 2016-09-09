import random

def importSim():
    import sys
    sys.path.append('/home/danielreid/swift-auxetic/core/build/python/build/lib.linux-x86_64-2.7/')
    import Networks
    globals()['Networks'] = Networks
    sys.path.append('/home/danielreid/swift-auxetic/core/util_py/')
    sys.path.append('/home/danielreid/swift-auxetic/runs/')
    import poisson_module
    import pruningMethods
    globals()['poisson_module'] = poisson_module
    globals()['pruningMethods'] = pruningMethods
def countBonds(srcFile):
    state = Networks.State()
    reader = Networks.ReadConfig(state, srcFile)
    reader.next()
    return repr(len(state.bonds))


def setupInitState(srcFile):
    if not 'Networks' in globals():
        importSim()
    if 'state' in globals():
        return 'already setup'
    bondThickness = .12
    state = Networks.State()
    reader = Networks.ReadConfig(state, srcFile)
    reader.next()
    grid = Networks.AtomGrid(state, 4.5, 4.5, 1)
    state.grid = grid
    dataFile = open('cfg.dat', 'w')
    integVerlet = Networks.Integrater(state)
    state.integrater = integVerlet
    state.rCut=1
    #reader = ReadConfig(state, '../../027_create_finite/starting_config_z_4_15_600_particles.xml')
    dataFile.write('nodes as id, x, y\n')
    for atom in state.atoms:
        dataFile.write('%d %f %f\n' % (atom.id, atom.pos[0], atom.pos[1]))
    dataFile.write('bonds as bondId atomIdA, atomIdB\n')
    bondIdMap = {}
    for i, bond in enumerate(state.bonds):
        idA, idB = bond.first().id, bond.second().id
        bondId = i+1
        dataFile.write('%d %d %d\n' % (bondId, idA, idB))
        bondIdMap[(idA, idB)] = bondId
        bondIdMap[(idB, idA)] = bondId

    bondHarm = Networks.FixBondHarmonic(state, "bondy", 1)
    state.fixes.append(bondHarm)

    angleHarm = Networks.FixAngleHarmonic(state, "angley", 1)
    BENDING = True
    if BENDING:
        state.fixes.append(angleHarm)
    else:
        print 'ANGLES OFF'

    border = Networks.Mod.selectBorder(state)

    xs = []
    ys = []
    for i in range(len(border)):
        xs.append(border[i].pos[0])
        ys.append(border[i].pos[1])
        #print border[i].pos


    def findCorners(border):
        corners = []
        polarities = [-1, 1]
        for a in polarities:
            for b in polarities:
                positions = []
                for i in range(len(border)): #sigh, can't iterate over atom pointers
                    positions.append(border[i].pos[0] * a + border[i].pos[1] * b)
                idx = positions.index(max(positions))
                corners.append(idx)
        return corners



    def spliceAtoms(atoms, idxA, idxB):#is INCLUSIVE
        a = min(idxA, idxB)
        b = max(idxA, idxB)
        if b-a > len(atoms)/2:
            listA = atoms[:a+1]
            listB = atoms[b:-1]
            for i in range(len(listB)):
                listA.append(listB[i])
            return listA
        else:
            return atoms[a:b+1]

    corners = findCorners(border)

#so it goes idx for lower left, upper left, lower right, upper right
#idxs go counterclockwise
    LoL = corners[0]
    UpL = corners[1]
    LoR = corners[2]
    UpR = corners[3]

    topBorder = spliceAtoms(border, UpR, UpL)
    state.createGroup("top", topBorder)

#CORNER ATOMS ARE IN BORDERS FOR BOTH DIRECTIONS (top and left, for upper keft corner, for example)
    leftBorder = spliceAtoms(border, UpL, LoL)
    state.createGroup("left", leftBorder)
    bottomBorder = spliceAtoms(border, LoL, LoR)
    state.createGroup("bottom", bottomBorder)
    rightBorder = spliceAtoms(border, LoR, UpR)
    state.createGroup("right", rightBorder)

    leftBorderMeasure = spliceAtoms(border, UpL, LoL)
    #leftBorderMeasure = spliceAtoms(border, UpL+1, LoL-1)
    state.createGroup("leftMeasure", leftBorderMeasure)
    rightBorderMeasure = spliceAtoms(border, LoR, UpR)
    #rightBorderMeasure = spliceAtoms(border, LoR+1, UpR-1)
    state.createGroup("rightMeasure", rightBorderMeasure)


    state.createGroup('orig')
    origAtoms = [a for a in state.atoms]
    state.addToGroupPythonList('orig', origAtoms)

    all_xs = [a.pos[0] for a in state.atoms]
    middleX = sum(all_xs)/float(len(all_xs))
    leftX = min(all_xs)
    rightX = max(all_xs)
    rightBoundary = (middleX + rightX) * 0.5
    leftBoundary = (middleX + leftX) * 0.5
    leftCOMAtoms = [a for a in state.atoms if a.pos[0] < leftBoundary]
    rightCOMAtoms = [a for a in state.atoms if a.pos[0] > rightBoundary]

    state.createGroup('leftCOM')
    state.createGroup('rightCOM')
    state.addToGroupPythonList('leftCOM', leftCOMAtoms)
    state.addToGroupPythonList('rightCOM', rightCOMAtoms)
    lala = state.selectGroup('rightCOM')

    poisson = poisson_module.PoissonModule(state, 'leftMeasure', 'rightMeasure')

    dataFile.write('top group node ids\n')
    dataFile.write(' '.join([str(topBorder[i].id) for i in range(len(topBorder))]) + '\n')
    dataFile.write('bottom group node ids\n')
    dataFile.write(' '.join([str(bottomBorder[i].id) for i in range(len(bottomBorder))]) + '\n')


#border test

#def GO(k)k = 1000
    stickTop = Networks.FixStickParticles(state, 'stickTop', 'top', Networks.Vector(0, 1, 1), 1)
    stickBottom = Networks.FixStickParticles(state, 'stickBottom', 'bottom', Networks.Vector(0, 1, 1), 1)

    state.activateFix(stickTop)
    state.activateFix(stickBottom)

    def springFunc(id, pos):
        return pos


    moduliFile = open('moduli.dat', 'w')
    moduliFile.write('z, compMod, shearMod, lateralDef\n')

#springLeft = FixSpringStatic(state, 'stickLeft', 'left', k, springFunc, Networks.Vector(1, 0, 0))
#springRight = FixSpringStatic(state, 'stickRight', 'left', k, springFunc, Networks.Vector(1, 0, 0))
    stickLeft = Networks.FixStickParticles(state, 'stickLeft', 'left', Networks.Vector(1, 0, 0), 1)
    stickRight = Networks.FixStickParticles(state, 'stickRight', 'right', Networks.Vector(1, 0, 0), 1)

    state.activateFix(stickLeft)
    state.activateFix(stickRight)
    sticks = [stickTop, stickBottom, stickLeft, stickRight]
    state.sticks = sticks
    border = Networks.Mod.selectBorder(state)
    borderIds = []
    for i in range(len(border)):
        borderIds.append(border[i].id)
#for i in range(len(topBorder)):
#    borderIds.append(topBorder[i].id)
    cfgIdx=0

    topbottomIds = []
    topAtoms = state.selectGroup('top')
    bottomAtoms = state.selectGroup('bottom')
    for i in range(len(topAtoms)):
        topbottomIds.append(topAtoms[i].id)
    for i in range(len(bottomAtoms)):
        topbottomIds.append(bottomAtoms[i].id)

    sizeRatio = state.bounds.trace[1] / state.bounds.trace[0]
    #plt.figure(figsize=(6, 6*sizeRatio))

    dataFile.write('Begin cutting\n')
#smoosh(-1, deformBy=0.02)
    #print 'z'
    #print Mod.computeZ(state, groupHandle='orig')
    #print len(state.atoms)
    state.atomParams.addSpecies(handle='spliced', sig=1, eps=1, mass=1)
    state.atomParams.addSpecies(handle='director', sig=1, eps=1, mass=1)
    #bondThickness = 0.06
    #measureBondThickness = 0.12
    topAtom = state.selectGroup('top')[0]
    topAtomIdx = -1
    for i, a in enumerate(state.atoms):
        if topAtom.id == a.id:
            topAtomIdx = i

    if BENDING:
        Networks.Mod.replaceBondsWithBending(state, 0, 1, bondThickness, 'spliced', 'director')
    else:
        print 'NO BENDING BONDS'
    print 'NUM ATOMS %d' % len(state.atoms)
    topAtoms = state.selectGroup('top')




    origAtoms = state.selectGroup('orig')
    origIds = []
    for i in range(len(origAtoms)):
        origIds.append(origAtoms[i].id)

    def stressGraph():
        stresses = Mod.computeBendingBondStresses(state)
        print 'sum stress %s\n' % str(sum(stresses))
        plt.hist(stresses, 100)
        plt.show()

    xs = [a.pos[0] for a in state.atoms]
    ys = [a.pos[1] for a in state.atoms]
    newBounds = Networks.Bounds(state, Networks.Vector(min(xs)-1, min(ys)-1, -3), Networks.Vector(max(xs)+1, max(ys)+1, 3))
    state.bounds = newBounds
    state.verbose = False
    globals()['state'] = state
    globals()['poisson'] = poisson
    return repr(None)

def measureStress(bondIdx, setupDone, prevCutDone):
    changeInEng = pruningMethods.getChangeInEngShearSingle(state, bondIdx)
    return repr(changeInEng)

def measureStressNoCut(setupDone, prevCutDone):
    return repr(pruningMethods.getShearStresses(state))

def measurePoissonsRatio(setupDone, prevCutDone):
    from updatesStd import smoosh
    deformBy = 1e-4
    lateralMotion = smoosh(state, poisson, deformBy=deformBy)
    poissons = (lateralMotion-1) / deformBy
    return repr(poissons)

def measureBulkMod(setupDone, prevCutDone):
    from measureModuli import measureBulkModulus
    from updatesStd import updateCompress
    compModulus = measureBulkModulus(state, postTransform=updateCompress, isBending=True, compressTo=0.99999)
    return repr(compModulus)

def measureShearMod(shearType, setupDone, prevCutDone):
    from measureModuli import measureShearModulus
    from updatesStd import updateShear
    from updatesStd import updateCompress
    from math import pi
    if shearType == "1":
        return repr(measureShearModulus(state, pi/2, postTransform=updateShear, isBending=True, deformBy=.000001))
    elif shearType == "2":
        return repr(measureShearModulus(state, shearType=1, postTransform=updateCompress, deformBy=-0.000001, isBending = True))
    return repr(None)

def measureZ(setupDone, prevCutDone):
    z = Networks.Mod.computeZ(state, groupHandle='orig')
    return repr(z)

def countBendingBonds(setupDone, prevCutDone):
    return repr(len(state.bendingBonds))

def pickIdxToCut(xs):
    xs = eval(xs)
    minIdx = 0
    minVal = min(xs)
    idx = xs.index(minVal)
    return repr(idx)

def cutBond(idxToRemove, writesFinished):
    state.removeBendingBond(state.bendingBonds[idxToRemove])
    while True:
        removed = Networks.Mod.deleteAtomsWithBondThreshold(state, groupHandle='orig', polarity=-1, thresh=1)
        if not len(removed):
            break
        dataFile.write('Remove atom ids %s' % (' '.join(str(x) for x in removed)))

    while Networks.Mod.deleteAtomsWithBondThreshold(state, groupHandle='all', polarity=-1, thresh=0): #this gets rid of extra director atoms
        pass
    return repr(None)


#file management funcs
def clearFiles(files):
    import os
    import shutil
    for f in files:
        if os.path.isfile(f):
            shutil.move(f, f + '_backup')
    return repr(None)

def writeArray(fileName, xs): #
    f = open(fileName, 'a')
    if isinstance(xs, list):
        xs = repr(xs)
    f.write(xs)
    f.write('\n')
    f.close()
    return repr(None)

def writeInfoHeader(fn, clearCompleted):
    f = open(fn, 'w')
    f.write('z compMod shearMod1 shearMod2, poisson\n')
    f.close()
    return repr(None)
def writeInfo(fn, vals):
    f = open(fn, 'a')
    v = ' '.join([str(x) for x in vals])
    f.write(v + '\n')
    f.close()
    return repr(None)
