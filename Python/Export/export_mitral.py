import os
import sys
import neuroml
import exportHelper

#Nav to neuron folder where compiled MOD files are present
os.chdir("../../NEURON")
from neuron import h
os.chdir("../NeuroML2")

h.chdir('../NEURON')
h.load_file('mitral.hoc')
sys.path.append('../NEURON')

from mkmitral import mkmitral
from pyneuroml.neuron import export_to_neuroml2
from pyneuroml import pynml
from neuroml import SegmentGroup

def export(num_cells_to_export = 5):
    cells = []

    for mgid in range(num_cells_to_export):
      print mgid
      cells.append(mkmitral(mgid))

    nml_net_file = "../NeuroML2/MitralCells/Exported/PartialBulb_%iMTCells.net.nml" % num_cells_to_export
    export_to_neuroml2(None, 
                       nml_net_file,
                       includeBiophysicalProperties=False,
                       separateCellFiles=True)

    for i in range(num_cells_to_export):
        print("Processing cell %i out of %i"%(i, num_cells_to_export))
        nml_cell_file = "../NeuroML2/MitralCells/Exported/Mitral_0_%i.cell.nml" % i
        nml_doc = pynml.read_neuroml2_file(nml_cell_file)
        cell = nml_doc.cells[0]

        soma_seg = next(seg for seg in cell.morphology.segments if seg.name == "Seg0_soma")
        initial_seg = next(seg for seg in cell.morphology.segments if seg.name == "Seg0_initialseg")
        hillock_seg = next(seg for seg in cell.morphology.segments if seg.name == "Seg0_hillock")

        # Ensure hillock parent is soma
        hillock_seg.parent.segments = soma_seg.id

        # Fix initial and hillock segs by moving them to the soma
        hillock_seg.proximal = pointMovedByOffset(hillock_seg.proximal, soma_seg.distal)
        hillock_seg.distal = pointMovedByOffset(hillock_seg.distal, soma_seg.distal)
        initial_seg.proximal = pointMovedByOffset(initial_seg.proximal, soma_seg.distal)
        initial_seg.distal = pointMovedByOffset(initial_seg.distal, soma_seg.distal)

        # Set root to id=0 and increment others
        exportHelper.resetRoot(cell)

        # TODO: cell.position(x,y,z) used for cell positioning in networks does not work as expected
        # See: https://github.com/NeuroML/jNeuroML/issues/55
        # Skipping the translation for now
        # # Move everything back to the origin
        # originOffset = type("", (), dict(x = -soma_seg.proximal.x, y = -soma_seg.proximal.y, z = -soma_seg.proximal.z ))()
        #
        # for seg in cell.morphology.segments:
        #     seg.proximal = pointMovedByOffset(seg.proximal, originOffset)
        #     seg.distal =   pointMovedByOffset(seg.distal, originOffset)

        # Replace ModelViewParmSubset_N groups with all, axon, soma, dendrite groups
        buildStandardSegmentGroups(cell)

        # Add channel placeholders
        nml_doc.includes.append(neuroml.IncludeType(href="channelIncludesPLACEHOLDER"))
        cell.biophysical_properties = neuroml.BiophysicalProperties(id="biophysPLACEHOLDER")

        # Save the new NML
        pynml.write_neuroml2_file(nml_doc, nml_cell_file)

        # Replace placeholders with contents from MitralCell...xml files
        replaceChannelPlaceholders(nml_cell_file)

        print("COMPLETED: " + nml_cell_file)

    print("DONE")


def pointMovedByOffset(point, offset):

    if point is None:
        return None

    point.x = point.x + offset.x
    point.y = point.y + offset.y
    point.z = point.z + offset.z

    return point


def replaceChannelPlaceholders(nml_cell_file):

    with open ("../NeuroML2/MitralCells/MitralCellBiophysicalProperties.xml", "r") as bioPhysFile:
        bioPhysProps=bioPhysFile.read()

    with open ("../NeuroML2/MitralCells/MitralCellChannelIncludes.xml", "r") as channelIncludesFile:
        channelIncludes=channelIncludesFile.read()

    with open (nml_cell_file, "r") as cellFile:
        cellNMLreplaced=cellFile.read()\
            .replace('<include href="channelIncludesPLACEHOLDER"></include>', channelIncludes)\
            .replace('<biophysicalProperties id="biophysPLACEHOLDER"/>', bioPhysProps)\

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
    export()