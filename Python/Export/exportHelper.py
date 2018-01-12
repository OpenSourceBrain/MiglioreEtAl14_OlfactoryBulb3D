import copy
import neuroml

def resetRoot(cell, startSegId = -1):

    # Correct all to be contiguous
    if startSegId == -1:
        nextSegId = max([seg.id for seg in cell.morphology.segments])+1
    else:
        nextSegId = startSegId

    for seg in cell.morphology.segments:
        changeSegmentId(cell, seg.id, nextSegId)
        nextSegId += 1

    # Then reset to start at 0
    if startSegId != 0:
        resetRoot(cell, 0)

def changeSegmentId(cell, sourceId, targetId):

    for seg in cell.morphology.segments:
        if seg.id == sourceId:
            seg.id = targetId

            for sg in cell.morphology.segment_groups:
                for memb in sg.members:
                    if memb.segments == sourceId:
                        memb.segments = targetId

        if seg.parent is not None and seg.parent.segments == sourceId:
            seg.parent.segments = targetId


def splitSegmentAlongFraction(cell,parentName,parentGroup,fractionAlong,childName):

    child = [seg for seg in cell.morphology.segments if seg.name == childName][0]
    parent = [seg for seg in cell.morphology.segments if seg.name == parentName][0]

    newSegID = max([int(seg.id) for seg in cell.morphology.segments]) + 1

    parentA = copy.deepcopy(parent)

    parentB = copy.deepcopy(parent)
    parentB.id = newSegID
    parentB.parent.segments = parentA.id
    parentB.name = parentName + "_B"

    breakPoint = copy.deepcopy(parent.distal)

    breakPoint.x = parent.proximal.x + (parent.distal.x-parent.proximal.x) * fractionAlong
    breakPoint.y = parent.proximal.y + (parent.distal.y-parent.proximal.y) * fractionAlong
    breakPoint.z = parent.proximal.z + (parent.distal.z-parent.proximal.z) * fractionAlong

    parentA.distal = copy.deepcopy(breakPoint)
    parentB.proximal = copy.deepcopy(breakPoint)
    parentB.proximal.original_tagname_ = "proximal"

    i = 0
    for seg in cell.morphology.segments:
        if seg == parent:
            cell.morphology.segments[i] = parentA
            break
        i = i + 1

    cell.morphology.segments.append(parentB)

    [g for g in cell.morphology.segment_groups if g.id == parentGroup][0]\
        .members\
        .append(neuroml.Member(segments=newSegID))

    child.parent.segments = parent.id

def printSections(rootSections):
    rootSections.sort(key = lambda sec: sec.name())

    for sec in rootSections:
        printSegmentTree(sec)

def printSegmentTree(rootSection, indentLevel = 0):
    from neuron import h
    coordCount = int(h.n3d(sec = rootSection))
    coords = []
    for c in range(coordCount):
        coords.append({
            "x": h.x3d(c, sec = rootSection),
            "y": h.y3d(c, sec = rootSection),
            "z": h.z3d(c, sec = rootSection),
            "d": h.diam3d(c, sec = rootSection)
        })
    sectionInfo = {
        "name": rootSection.name(),
        "L": '{:.3f}'.format(rootSection.L),
        "Diam": '{:.3f}'.format(rootSection.diam),
        "Ra": '{:.3f}'.format(rootSection.Ra),
        "Branch": '{:.3f}'.format(rootSection.rallbranch),
        "Orientation":'{:.3f}'.format(rootSection.orientation()),
        "segs": rootSection.nseg,
        "locOnParent":'{:.3f}'.format(rootSection.parentseg().x) if rootSection.parentseg() is not None else None
    }
    print("   " * indentLevel + str(sectionInfo))
    print("")

    # for coord in coords:
    #     print("   " * indentLevel + str(coord))

    children = rootSection.children()
    children.sort(key=lambda sec: sec.name())
    for child in children:
        printSegmentTree(child, indentLevel + 1)

def sendVectorsToBlender(t, vectors):
    import xmlrpclib
    import numpy as np

    blender = xmlrpclib.ServerProxy('http://192.168.0.34:8000')

    for name in vectors:
        v = np.array(vectors[name])
        values = np.divide(np.add(v,100),150.0).tolist() # Scale to between 0-1

        blender.animateBrightness(name, t, values)

def sendToBlender(rootSectionList):
    import xmlrpclib
    blender = xmlrpclib.ServerProxy('http://192.168.0.34:8000')

    # try:
    for sec in rootSectionList:
        sendToBlenderRecursive(sec, blender)

    # finally:
    #     blender.stop()

def sendToBlenderRecursive(rootSection, blender):
    from neuron import h
    coordCount = int(h.n3d(sec=rootSection))

    if coordCount == 0:
        h.define_shape(sec=rootSection)
        coordCount = int(h.n3d(sec=rootSection))

    coords = []

    # If it has coords, collect them
    for c in range(coordCount):
        coords.append({
            "x": h.x3d(c, sec=rootSection),
            "y": h.y3d(c, sec=rootSection),
            "z": h.z3d(c, sec=rootSection),
            "d": h.diam3d(c, sec=rootSection)
        })

    if len(coords) < 2:
        newCoord = coords[0].copy()
        newCoord["y"] += 0.1
        coords.append(newCoord)

    for i in range(1, len(coords)):
        start = coords[i-1]
        end = coords[i]

        blender.cyl(start, end, rootSection.diam, rootSection.name() + str(i))

    children = rootSection.children()
    for child in children:
        sendToBlenderRecursive(child, blender)

def recordSegments(rootSectionList):
    vectors = {}

    for section in rootSectionList:
        recordSegmentsRecursive(section, vectors)

    return vectors

def recordSegmentsRecursive(rootSection, vectors):
    from neuron import h

    coordCount = int(h.n3d(sec=rootSection))

    for i in range(1, coordCount):
        startL = h.arc3d(i-1, sec=rootSection)
        endL = h.arc3d(i, sec=rootSection)
        vectorPos = (endL + startL) / 2.0 / rootSection.L
        vector = h.Vector()
        vector.record(rootSection(vectorPos)._ref_v)
        vectors.update({rootSection.name()+str(i):vector})

    for child in rootSection.children():
        recordSegmentsRecursive(child, vectors)
