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


    exportToNML(model.granules)

def exportToNML(cells):
    '''
    GCs only vary these parameters:
        priden: length (through y position of distal pt), number of subdivitions (nseg)
	    spine neck: location on parent priden2
    '''

    for gid in cells.keys():
        pridenLength = cells[gid].priden.L
        pridenNseg = cells[gid].priden.nseg
        neckLoc = cells[gid].priden2[0].children()[0].parentseg().x

        # Translate these by the length of priden
        priden2DistalY = pridenLength + 250.0
        spineNeckDistalY = priden2DistalY + 2.0
        spineHeadDistalY = spineNeckDistalY + 1.0

        # TODO: Align the GC along the bulb versor
        import granules
        versor = granules.granule_position_orientation(gcid)[1]

        for seg in cell.morphology.segments:
            segLength = seg.length

            if seg.parent is not None:
                parentDistal = [parent for parent in cell.morphology.segments if parent.id == seg.parent.segments][
                    0].distal
                seg.proximal.x = parentDistal.x
                seg.proximal.y = parentDistal.y
                seg.proximal.z = parentDistal.z

            seg.distal = setAlongVersor(seg.distal, versor, seg.proximal, segLength)

        with open("../NeuroML2/GranuleCells/GranuleCellTemplate.xml") as f:
            template = f.read()

        template = template\
            .replace("[GID]", str(gid))\
            .replace("[PridenLength]", str(pridenLength))\
            .replace("[PridenSubdivisions]", str(pridenNseg))\
            .replace("[Priden2DistalY]", str(priden2DistalY))\
            .replace("[SpineFractionAlongPriden2]", str(neckLoc))\
            .replace("[SpineNeckDistalY]", str(spineNeckDistalY))\
            .replace("[SpineHeadDistalY]", str(spineHeadDistalY))

        with open("../NeuroML2/GranuleCells/Exported/Granule_" + str(gid) + ".cell.nml", "w") as f:
            f.write(template)

def exportToNML2(cells):
    import neuroml
    from pyneuroml.neuron import export_to_neuroml2
    from pyneuroml import pynml
    from neuroml import SegmentGroup

    nml_net_file = "../NeuroML2/GranuleCells/Exported/GCnet%iG.net.nml" % len(cells)
    export_to_neuroml2(None,
                       nml_net_file,
                       includeBiophysicalProperties=False,
                       separateCellFiles=True)

    # Rename files so their cell GIDs are preserved
    for gcid in cells.keys():
        fileId = cells[gcid]['index']
        oldFile = '../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml' % fileId
        newFile = '../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml_TEMP' % gcid

        # Using TEMP files to avoid naming conflicts
        os.rename(oldFile, newFile)

    # Remove temp files after all have been renamed
    for gcid in cells.keys():
        oldFile = '../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml_TEMP' % gcid
        newFile = '../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml' % gcid
        os.rename(oldFile, newFile)


    for gcid in cells.keys():

        cell, nml_doc, nml_cell_file = readGCnml(gcid)
        
        print("Loaded GC cell %i with %i segments"%(gcid, len(cell.morphology.segments)))

        # Change cell ID to preserve GCID
        cell.id = "Granule_0_%i" % gcid

        # Change segment ids to start at 0 and increment
        exportHelper.resetRoot(cell)

        # Replace ModelViewParmSubset_N groups with all, axon, soma, dendrite groups
        buildStandardSegmentGroups(cell)

        # Add channel placeholders
        nml_doc.includes.append(neuroml.IncludeType(href="channelIncludesPLACEHOLDER"))
        cell.biophysical_properties = neuroml.BiophysicalProperties(id="biophysPLACEHOLDER")
        cell.morphology.segments.append(neuroml.Segment(id="spinePLACEHOLDER"))

        # Save the new NML
        pynml.write_neuroml2_file(nml_doc, nml_cell_file)


        # Replace placeholders with contents from GranuleCell...xml files
        replaceChannelPlaceholders(nml_cell_file)

        cell, nml_doc, nml_cell_file = readGCnml(gcid)

        # Fix the fractionAlong parent segment bug ( https://github.com/NeuroML/org.neuroml.export/issues/46 )
        #exportHelper.splitSegmentAlongFraction(cell, "Seg0_priden", "priden", 0.8, "Seg0_priden2_0")

        # Orient cell along the versor
        versor = granules.granule_position_orientation(gcid)[1]

        for seg in cell.morphology.segments:
            segLength = seg.length

            if seg.parent is not None:
                parentDistal = [parent for parent in cell.morphology.segments if parent.id == seg.parent.segments][0].distal
                seg.proximal.x = parentDistal.x
                seg.proximal.y = parentDistal.y
                seg.proximal.z = parentDistal.z

            seg.distal = setAlongVersor(seg.distal, versor, seg.proximal, segLength)

        # Make sure spine is in the all group
        [group for group in cell.morphology.segment_groups if group.id == 'all'][0]\
            .includes\
            .append(neuroml.Include(segment_groups='spine_group'))\

        # and Dendrite group
        [group for group in cell.morphology.segment_groups if group.id == 'dendrite_group'][0]\
            .includes\
            .append(neuroml.Include(segment_groups='spine_group'))

        # Save orientation
        pynml.write_neuroml2_file(nml_doc, nml_cell_file)

        print(nml_cell_file)

def readGCnml(gcid):

    nml_cell_file = "../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml" % gcid
    nml_doc = pynml.read_neuroml2_file(nml_cell_file)
    cell = nml_doc.cells[0]

    return cell, nml_doc, nml_cell_file



def setAlongVersor(segmentPoint, versor, startPoint, distance):

    segmentPoint.x = startPoint.x + versor[0]*distance
    segmentPoint.y = startPoint.y + versor[1]*distance
    segmentPoint.z = startPoint.z + versor[2]*distance

    return segmentPoint

def replaceChannelPlaceholders(nml_cell_file):

    with open ("../NeuroML2/GranuleCells/GranuleCellBiophysicalProperties.xml", "r") as bioPhysFile:
        bioPhysProps=bioPhysFile.read()

    with open ("../NeuroML2/GranuleCells/GranuleCellChannelIncludes.xml", "r") as channelIncludesFile:
        channelIncludes=channelIncludesFile.read()

    with open ("../NeuroML2/GranuleCells/GranuleCellSpineSegments.xml", "r") as spineFile:
        spine=spineFile.read()

    with open (nml_cell_file, "r") as cellFile:
        cellNMLreplaced=cellFile.read()\
            .replace('<include href="channelIncludesPLACEHOLDER"></include>', channelIncludes)\
            .replace('<biophysicalProperties id="biophysPLACEHOLDER"/>', bioPhysProps)\
            .replace('<segment id="spinePLACEHOLDER"/>', spine)

    with open(nml_cell_file, "w") as cellFile:
        cellFile.write(cellNMLreplaced)

def buildStandardSegmentGroups(cell):

    largestGroup = None
    # Delete all ModelViewParmSubset_N groups, saving the largest
    for g in xrange(len(cell.morphology.segment_groups) - 1, -1, -1):  # Start from the end
        group = cell.morphology.segment_groups[g]

        if group.id.startswith('ModelViewParmSubset'):
            cell.morphology.segment_groups.remove(group)

            if largestGroup is None or len(largestGroup.includes) < len(group.includes):
                largestGroup = group

    # Add the standard soma, dendrite, axon groups
    somaGroup = SegmentGroup('GO:0043025', 'soma_group')
    dendriteGroup = SegmentGroup('GO:0030425', 'dendrite_group')
    axonGroup = SegmentGroup('GO:0030424', 'axon_group')
    allGroup = None

    # Find the group with all segments
    for group in cell.morphology.segment_groups:
        if group.id == 'all':
            allGroup = group

    # If there is no "all" group, assume it's the largest of the ModelViewP... groups
    if allGroup is None and largestGroup is not None:
        allGroup = largestGroup

        # Create the 'all' group from the largest group
        largestGroup.id = 'all'
        cell.morphology.segment_groups.append(largestGroup)

    if allGroup is not None:

        # Classify each include of 'all' group into a standard group
        for include in allGroup.includes:

            if include.segment_groups.startswith(('secden', 'priden', 'tuftden')):
                dendriteGroup.includes.append(include)

            elif include.segment_groups == 'soma':
                somaGroup.includes.append(include)

            elif include.segment_groups.startswith(('hillock', 'initialseg')):
                axonGroup.includes.append(include)

        # Attach the standard groups to the cell
        cell.morphology.segment_groups.append(somaGroup)
        cell.morphology.segment_groups.append(dendriteGroup)
        cell.morphology.segment_groups.append(axonGroup)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        exportNetworkGCs(sys.argv[1])

    # Otherwise export the num defined in main()
    else:
        __main__()