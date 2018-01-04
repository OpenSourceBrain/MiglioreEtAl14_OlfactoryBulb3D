import pydevd
pydevd.settrace('192.168.177.1', port=4200, suspend=False)

import os
import sys
import re
import copy
import exportHelper


def __main__():

    MCs = 1
    GCsPerMC = 1
    numGranulesTotal = MCs * GCsPerMC

    # Nav to neuron folder where compiled MOD files are present
    os.chdir("../../NEURON")
    from neuron import h,gui

    # Build the network with desired number of GCs - including spines
    sys.path.append(os.getcwd())
    import customsim
    import modeldata
    customsim.setup(MCs, GCsPerMC)
    model = modeldata.getmodel()


    result = exportToNML(model.granules)

    print("Exported the following cell files:")
    for file in result:
        print("   " + file)

def exportToNML(cells):
    '''
    GCs only vary these parameters:
        id
        priden: length (through y position of distal pt), number of subdivitions (nseg)
	    spine neck: location on parent priden2
    '''

    exported = []

    for gid in cells.keys():
        # Obtain the varying values from the network model
        pridenLength = cells[gid].priden.L
        pridenNseg = cells[gid].priden.nseg
        neckLoc = cells[gid].priden2[0].children()[0].parentseg().x

        # Read the cell template
        from pyneuroml import pynml
        nmldoc = pynml.read_neuroml2_file("../NeuroML2/GranuleCells/GranuleCellTemplate.xml")
        cell = nmldoc.cells[0]

        # Replace placeholders
        cell.id = "Granule_" + str(gid)
        next(seg for seg in cell.morphology.segments if seg.name == 'priden_seg').distal.y = pridenLength
        next(prop for prop in next(section for section in cell.morphology.segment_groups if section.id == 'priden').properties if prop.tag == 'numberInternalDivisions').value = pridenNseg
        next(seg for seg in cell.morphology.segments if seg.name == 'neck_seg').parent.fraction_along = neckLoc

        # Align the GC along the bulb versor
        import granules
        versor = granules.granule_position_orientation(gid)[1]

        for seg in cell.morphology.segments:
            segLength = seg.length # retain the original length

            if seg.parent is not None:
                parent = next(parent for parent in cell.morphology.segments if parent.id == seg.parent.segments)
                seg.proximal.x = parent.distal.x
                seg.proximal.y = parent.distal.y
                seg.proximal.z = parent.distal.z

            seg.distal = setAlongVersor(seg.distal, versor, seg.proximal, segLength)

        # Save the file
        cellFile = "../NeuroML2/GranuleCells/Exported/Granule_" + str(gid) + ".cell.nml"
        pynml.write_neuroml2_file(nmldoc, cellFile)

        exported.append(cellFile)

    return exported

def setAlongVersor(segmentPoint, versor, startPoint, distance):

    segmentPoint.x = startPoint.x + versor[0]*distance
    segmentPoint.y = startPoint.y + versor[1]*distance
    segmentPoint.z = startPoint.z + versor[2]*distance

    return segmentPoint


if __name__ == "__main__":
    __main__()