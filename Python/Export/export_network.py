# import pydevd
# pydevd.settrace('192.168.177.1', port=4200, suspend=False)


def export(MCs = 2, GCsPerMC = 1, useOdorInput = True, odorInputMaxTime = 200):
    # Export cells first - in their own NEURON instances
    import subprocess
    subprocess.Popen("python -c 'import export_mitral; export_mitral.export("+`MCs`+");'", shell=True).wait()
    subprocess.Popen("python -c 'import export_granule; export_granule.export(" + `MCs` + ","+`GCsPerMC`+");'", shell=True).wait()

    # Export the odor input
    if useOdorInput:
        subprocess.Popen("python -c 'import export_input; export_input.export(" + `MCs` + ");'", shell=True).wait()

    import os, neuroml, sys
    from math import ceil
    os.chdir('../../NEURON')
    sys.path.append(os.path.abspath(os.getcwd()))
    from neuron import h, gui

    from pyneuroml import pynml
    from pyneuroml.neuron import export_to_neuroml2

    import customsim
    import modeldata



    networkTemplate = FileTemplate("../NeuroML2/Networks/NetworkTemplate.xml")
    includeTemplate = FileTemplate("../NeuroML2/Networks/IncludeTemplate.xml")
    glomsTemplate = FileTemplate("../NeuroML2/Networks/GlomeruliTemplate.xml")
    populationTemplate = FileTemplate("../NeuroML2/Networks/PopulationTemplate.xml")
    projectionTemplate = FileTemplate("../NeuroML2/Networks/ProjectionTemplate.xml")

    odorInputListTemplate = FileTemplate("../NeuroML2/Networks/OdorInputListTemplate.xml")
    odorSynapseTemplate = FileTemplate("../NeuroML2/Networks/OdorSynapseTemplate.xml")

    customsim.setup(MCs, GCsPerMC)
    model = modeldata.getmodel()

    # Exp2Syns are used for odor input
    if useOdorInput:
        section2synapse = {syn.get_segment().sec.name(): syn for syn in h.Exp2Syn}

    netFile = "../NeuroML2/Networks/Bulb_%iMC_%iGC%s.net.nml" % (len(model.mitral_gids), len(model.granule_gids),"_OdorIn" if useOdorInput else "")

    includes = ""
    populations = ""
    projections = ""
    gloms = ""
    odorInputLists = ""
    odorSyns = ""

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

    # Each glom consists of 5 mcs -- using the highest mc id, generate the required gloms
    num_gloms = int(ceil((max(model.mitral_gids)+1)/5.0))

    with open('realgloms.txt') as f:
        for g in range(num_gloms):
            g_x, g_y, g_z = map(float, f.readline().split(' '))

            gloms += glomsTemplate.text \
                .replace("[GlomID]", `g`) \
                .replace("[X]", `g_x`) \
                .replace("[Y]", `g_y`) \
                .replace("[Z]", `g_z`)

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
        alongSegment = getFractionAlongSegment(model.mitrals[synapse.mgid].secden[synapse.isec], synapse.xm)
        mcSegmentIndex = alongSegment["segment_index"]
        alongMcSegment = alongSegment["along_segment"]

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

    # Add odor inputs
    if useOdorInput:
        import re, json
        synId = 0

        with open('odor-events.json') as r:
            odorTimes = json.load(r)

        for mcid in model.mitral_gids:
            mc = model.mitrals[mcid]
            nmlmc = mcNMLs[mcid]

            for tuftden in mc.tuftden:
                # Translate NRN name into NML name
                tuftdenIndex = re.compile('tuftden\[(.*)\]').search(tuftden.name()).groups(1)[0]
                nmlTuftDenName = 'tuftden_'+tuftdenIndex
                nmlTuftDenSegs = [seg for seg in nmlmc.morphology.segments if seg.name.endswith(nmlTuftDenName)]
                alongSegment = getFractionAlongSegment(tuftden, 0.1) # Syns are placed at 0.1

                nmlTuftDenSeg = nmlTuftDenSegs[alongSegment['segment_index']]
                nmlAlongTuftDenSeg = alongSegment['along_segment']

                times = odorTimes[tuftden.name()]

                for i, time in enumerate(times['times']):
                    if time > odorInputMaxTime:
                        break

                    # Add inputList
                    odorInputLists += odorInputListTemplate.text\
                        .replace("[ID]", `synId`)\
                        .replace("[SynInputID]", "OdorSynTimes"+`synId`)\
                        .replace("[McID]", `mcid`)\
                        .replace("[SegmentID]", `nmlTuftDenSeg.id`)\
                        .replace("[FractionAlong]", `nmlAlongTuftDenSeg`)

                    # Add synapse and timed input
                    odorSyns += odorSynapseTemplate.text\
                        .replace("[ID]", `synId`)\
                        .replace("[Weight]", `times['weights'][i]`)\
                        .replace("[Time]", `time`)

                    synId += 1


    network = networkTemplate.text\
        .replace("[NumGloms]", `num_gloms`) \
        .replace("[GlomeruliPlaceholder]", gloms) \
        .replace("[IncludesPlaceholder]", includes)\
        .replace("[PopulationsPlaceholder]", populations)\
        .replace("[ProjectionsPlaceholder]", projections)\
        .replace("[OdorInputLists]", odorInputLists)\
        .replace("[OdorInputSynapses]", odorSyns)

    with open(netFile, "w") as file:
        file.write(network)

    print('Net file saved to: ' + netFile)

def getFractionAlongSegment(section, fractionAlong):
    nseg = section.nseg

    if fractionAlong < 1:
        alongSection = fractionAlong * nseg
        segmentIndex = int(alongSection)
        alongSegment = alongSection - segmentIndex
    else:
        segmentIndex = nseg - 1
        alongSegment = 1.0

    return {"segment_index":segmentIndex, "along_segment": alongSegment}

class FileTemplate():
    def __init__(self, path):
        self.path = path

        with open(self.path, "r") as file:
            self.text = file.read()


if __name__ == "__main__":
    export()