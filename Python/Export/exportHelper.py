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