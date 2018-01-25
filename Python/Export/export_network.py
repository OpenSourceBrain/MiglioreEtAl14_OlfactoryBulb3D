import pydevd
pydevd.settrace('192.168.177.1', port=4200, suspend=False)

def export(MCs = 2, GCsPerMC = 10):
    # Export cells first - in their own NEURON instances
    import subprocess
    subprocess.Popen("python -c 'import export_mitral; export_mitral.export("+`MCs`+");'", shell=True).wait()
    subprocess.Popen("python -c 'import export_granule; export_granule.export(" + `MCs` + ","+`GCsPerMC`+");'", shell=True).wait()

    import os, neuroml, sys
    os.chdir('../../NEURON')
    sys.path.append(os.path.abspath(os.getcwd()))
    from neuron import h, gui

    from pyneuroml import pynml
    from pyneuroml.neuron import export_to_neuroml2

    import customsim
    import modeldata



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

    # Make MC includes and populations
    for mcgid in model.mitral_gids:

        includes += includeTemplate.text\
            .replace("[CellType]", "Mitral")\
            .replace("[GID]", `mcgid`)

        populations += populationTemplate.text\
            .replace("[CellType]", "Mitral")\
            .replace("[GID]", `mcgid`) \
            .replace("[X]", `0`) \
            .replace("[Y]", `0`) \
            .replace("[Z]", `0`)

            # TODO: restore these when this is resolved: https://github.com/NeuroML/jNeuroML/issues/55
            # .replace("[X]", `model.mitrals[mcgid].x`)\
            # .replace("[Y]", `model.mitrals[mcgid].y`)\
            # .replace("[Z]", `model.mitrals[mcgid].z`)

        # Retain mitral cell NML for later
        mcNML = pynml\
                .read_neuroml2_file("../NeuroML2/MitralCells/Exported/Mitral_0_%i.cell.nml" % mcgid)\
                .cells[0]
        
        mcNMLs.update({mcgid:mcNML})

    # Make GC includes and populations
    import granules
    from neuroml.nml.nml import NeuroMLDocument

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

        # Retain granule cell NML
        gcNML = pynml\
                .read_neuroml2_file("../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml" % gcgid)\
                .cells[0]

        gcNMLs.update({gcgid:gcNML})

    # Add a projection for each synapse
    synCount = len(model.mgrss.keys())
    curSyn = 0

    for sgid in model.mgrss.keys():

        print('Building synapse %i of %i' % (curSyn+1,synCount))

        synapse = model.mgrss[sgid]

        # Compute the segment on the MC to which the synapse will be connected
        nsecden = model.mitrals[synapse.mgid].secden[synapse.isec].nseg
        if synapse.xm < 1:
            fractionAlongSection = synapse.xm * nsecden
            mcSegmentIndex = int(fractionAlongSection)
            alongMcSegment = fractionAlongSection - mcSegmentIndex
        else:
            mcSegmentIndex = nsecden - 1
            alongMcSegment = 1.0

        # Get the NML ID of the MC segment
        mcSegmentID = next(seg.id for seg in mcNMLs[synapse.mgid].morphology.segments if seg.name == "Seg%i_secden_%i"%(mcSegmentIndex,synapse.isec))

        # Get the NML ID of the MC spine head, which all syns are attached (at 0.5 position)
        gcSpineHeadSegmentID = next(seg.id for seg in gcNMLs[synapse.ggid].morphology.segments if seg.name == "head_seg")

        # Add Dendro-dendritic synapses
        # GC -> MC part
        projections += projectionTemplate.text\
            .replace("[ProjectionID]", `sgid`+'_G2M')\
            .replace("[PreCellType]", "Granule")\
            .replace("[PreGID]", `synapse.ggid`)\
            .replace("[PreSegment]", `gcSpineHeadSegmentID`)\
            .replace("[PreAlong]", `0.5`)\
            .replace("[PostCellType]", "Mitral")\
            .replace("[PostGID]", `synapse.mgid`)\
            .replace("[PostSegment]", `mcSegmentID`)\
            .replace("[PostAlong]", `alongMcSegment`)\
            .replace("[Synapse]", "FIsyn")\

        # MC -> GC part
        projections += projectionTemplate.text\
            .replace("[ProjectionID]", `sgid`+'_M2G')\
            .replace("[PreCellType]", "Mitral")\
            .replace("[PreGID]", `synapse.mgid`)\
            .replace("[PreSegment]", `mcSegmentID`)\
            .replace("[PreAlong]", `alongMcSegment`)\
            .replace("[PostCellType]", "Granule")\
            .replace("[PostGID]", `synapse.ggid`)\
            .replace("[PostSegment]", `gcSpineHeadSegmentID`)\
            .replace("[PostAlong]", "0.5")\
            .replace("[Synapse]", "AmpaNmdaSynapse")\

        curSyn += 1


    network = networkTemplate.text\
        .replace("[IncludesPlaceholder]", includes)\
        .replace("[PopulationsPlaceholder]", populations)\
        .replace("[ProjectionsPlaceholder]", projections)

    with open(netFile, "w") as file:
        file.write(network)

    print('Net file saved to: ' + netFile)


class FileTemplate():
    def __init__(self, path):
        self.path = path

        with open(self.path, "r") as file:
            self.text = file.read()


if __name__ == "__main__":
    export()