import os
import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
import neuroml

sys.path.append("/usr/local/lib/python2.7/site-packages")
import neuroml

#Nav to neuron folder where compiled MOD files are present
os.chdir("../../NEURON")
from neuron import h
os.chdir("../NeuroML2")

h.chdir('../NEURON')
sys.path.append('../NEURON')

#from neuronHelper import *
from pyneuroml import pynml
from pyneuroml.neuron import export_to_neuroml2

def __main__():
    import customsim
    import modeldata

    MCs = 1
    GCsPerMC = 1

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

#import pydevd
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

        gcNMLs.update({gcgid:gcNML})

    # Add a projection for each synapse
    synCount = len(model.mgrss.keys())
    curSyn = 0

    for sgid in model.mgrss.keys():

        print('Building synapse %i of %i' % (curSyn+1,synCount))

        synapse = model.mgrss[sgid]

        nsecden = model.mitrals[synapse.mgid].secden[synapse.isec].nseg
        secdenIndex = min(nsecden-1, int(synapse.xm * nsecden))
        postSegmentId = [seg.id\
                         for seg in mcNMLs[synapse.mgid].morphology.segments\
                         if seg.name == "Seg%i_secden_%i"%(secdenIndex,synapse.isec)\
                        ][0]

        gcNML = gcNMLs[synapse.ggid].cells[0]

        # Position the spine along the GC priden
        import exportHelper
        exportHelper.splitSegmentAlongFraction(gcNML,"Seg0_priden2_0","priden2_0",synapse.xg,'Seg0_neck')
        pynml.write_neuroml2_file(gcNMLs[synapse.ggid], "../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml" % synapse.ggid)

        # Add Dendro-dendritic synapses
        # GC -> MC part
        projections += projectionTemplate.text\
            .replace("[ProjectionID]", `sgid`+'_G2M')\
            .replace("[PreCellType]", "Granule")\
            .replace("[PreGID]", `synapse.ggid`)\
            .replace("[PreSegment]", `4`)\
            .replace("[PreAlong]", `0.5`)\
            .replace("[PostCellType]", "Mitral")\
            .replace("[PostGID]", `synapse.mgid`)\
            .replace("[PostSegment]", `postSegmentId`)\
            .replace("[PostAlong]", "0.5")\
            .replace("[Synapse]", "FIsyn")\

        # MC -> GC part
        projections += projectionTemplate.text\
            .replace("[ProjectionID]", `sgid`+'_M2G')\
            .replace("[PreCellType]", "Mitral")\
            .replace("[PreGID]", `synapse.mgid`)\
            .replace("[PreSegment]", `postSegmentId`)\
            .replace("[PreAlong]", `0.5`)\
            .replace("[PostCellType]", "Granule")\
            .replace("[PostGID]", `synapse.ggid`)\
            .replace("[PostSegment]", `4`)\
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
    __main__()

#makeTestPlots()

#def makeTestPlots():
#
h.tstop = 300
h.dt = 0.025

#clampM = h.IClamp(h.Mitral[0].soma(0.5))
#clampM.delay = 50
#clampM.dur = 200
#clampM.amp = 0.8
#
#clampG = h.IClamp(h.Granule[0].soma(0.5))
#clampG.delay = 50
#clampG.dur = 200
#clampG.amp = 0.05
#
#g=h.Graph()
#h.graphList[0].append(g)
#g.size(0,h.tstop,-80,50)
#g.addvar('mitral soma',   'v(0.5)',  1,0, sec = h.Mitral[0].soma)
#g.addvar('mitral secden', 'v(0.829)',2,0, sec = h.Mitral[0].secden[8])
#
#g2=h.Graph()
#h.graphList[0].append(g2)
#g2.size(0,h.tstop,-80,50)
#g2.addvar('gran soma',       'v(0.5)',2,0, sec = h.Granule[0].soma)
#g2.addvar('gran priden',     'v(0.5)',4,0, sec = h.Granule[0].priden2[0])
#g2.addvar('gran spine head', 'v(0.5)',5,0, sec = h.GranuleSpine[0].head)

h.nrnmainmenu()
