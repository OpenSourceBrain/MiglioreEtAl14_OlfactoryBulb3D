import os
import sys
from neuron import h
from pyneuroml import pynml

h.chdir('../NEURON')
sys.path.append('../NEURON')


def __main__():
    import customsim
    import modeldata

    MCs = 5
    GCsPerMC = 50

    networkTemplate = FileTemplate("../NeuroML2/Networks/NetworkTemplate.xml")
    includeTemplate = FileTemplate("../NeuroML2/Networks/IncludeTemplate.xml")
    populationTemplate = FileTemplate("../NeuroML2/Networks/PopulationTemplate.xml")
    projectionTemplate = FileTemplate("../NeuroML2/Networks/ProjectionTemplate.xml")

    customsim.setup(MCs, GCsPerMC)
    model = modeldata.getmodel()

    netFile = "../NeuroML2/Networks/Bulb_%iMC_%iGC.net.nml" % (len(model.mitral_gids), len(model.granule_gids))

    includes = ""
    populations = ""
    projections = ""

    mcNMLs = {}
    gcNMLs = {}


    import pydevd
    #pydevd.settrace('10.211.55.3', port=4200, stdoutToServer=True, stderrToServer=True)

    # Make MC includes and populations
    for mcgid in model.mitral_gids:

        includes += includeTemplate.text\
            .replace("[CellType]", "Mitral")\
            .replace("[GID]", `mcgid`)

        populations += populationTemplate.text\
            .replace("[CellType]", "Mitral")\
            .replace("[GID]", `mcgid`)\
            .replace("[X]", `model.mitrals[mcgid].x`)\
            .replace("[Y]", `model.mitrals[mcgid].y`)\
            .replace("[Z]", `model.mitrals[mcgid].z`)

        # Retain mitral cell NML
        mcNML = pynml\
                .read_neuroml2_file("../NeuroML2/MitralCells/Exported/Mitral_0_%i.cell.nml" % mcgid)\
                .cells[0]
        
        mcNMLs.update({mcgid:mcNML})

    # Make GC includes and populations
    import granules

    for gcgid in model.granule_gids:

        includes += includeTemplate.text\
            .replace("[CellType]", "Granule")\
            .replace("[GID]", `gcgid`)

        populations += populationTemplate.text\
            .replace("[CellType]", "Granule")\
            .replace("[GID]", `gcgid`)\
            .replace("[X]", `granules.gid2pos[gcgid][0]`)\
            .replace("[Y]", `granules.gid2pos[gcgid][1]`)\
            .replace("[Z]", `granules.gid2pos[gcgid][2]`)

    # Add a projection for each synapse
    for sgid in model.mgrss.keys():

        synapse = model.mgrss[sgid]

        nsecden = model.mitrals[synapse.mgid].secden[synapse.isec].nseg
        secdenIndex = min(nsecden-1, int(synapse.xm * nsecden))
        postSegmentId = [seg.id\
                         for seg in mcNMLs[synapse.mgid].morphology.segments\
                         if seg.name == "Seg%i_secden_%i"%(secdenIndex,synapse.isec)\
                        ][0]

        # TODO: determine if numOfDivisions should be equal to number of group members if so, keep the below code
        #npriden = model.granules[synapse.ggid].priden2[synapse.ipri].nseg
        #pridenIndex = min(npriden-1, int(synapse.xg * npriden))
        #preSegmentId = [seg.id \
        #                 for seg in gcNMLs[synapse.ggid].morphology.segments \
        #                 if seg.name == "Seg%i_priden2_%i"%(pridenIndex,synapse.ipri) \
        #                ][0]

        projections += projectionTemplate.text\
            .replace("[ProjectionID]", `sgid`)\
            .replace("[PreCellType]", "Granule")\
            .replace("[PreGID]", `synapse.ggid`)\
            .replace("[PreSegment]", `synapse.ipri`)\
            .replace("[PreAlong]", `synapse.xg`)\
            .replace("[PostCellType]", "Mitral")\
            .replace("[PostGID]", `synapse.mgid`)\
            .replace("[PostSegment]", `postSegmentId`)\
            .replace("[PostAlong]", "0.5")


    network = networkTemplate.text\
        .replace("[IncludesPlaceholder]", includes)\
        .replace("[PopulationsPlaceholder]", populations)\
        .replace("[ProjectionsPlaceholder]", projections)

    with open(netFile, "w") as file:
        file.write(network)

class FileTemplate():
    def __init__(self, path):
        self.path = path

        with open(self.path, "r") as file:
            self.text = file.read()


if __name__ == "__main__":
    __main__()