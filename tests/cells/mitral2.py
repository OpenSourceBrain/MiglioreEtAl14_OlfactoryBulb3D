import sys; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.cells.NEURONCellTest  import NEURONCellTest
from tests.cells.NeuroMLCellTest import NeuroMLCellTest

class NEURON(NEURONCellTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/mkmitral.py"
        self.label = "mitral2"
        self.resultsFile = "results/cells/mitral2/NEURON.json"
        self.currentRange = (-1, 3) # was -1

    def prepare(self, h):
        import mkmitral

        cell = mkmitral.mkmitral(1)

        h.celsius = 24


        # h.pt3dclear(sec=cell.soma)
        # cell.soma.L = 10000
        # cell.soma.nseg = 500
        # h.define_shape(sec=cell.soma)

        # from exportHelper import printSections
        # printSections([cell.soma])

        #from exportHelper import sendToBlender as sendToBlender
        #sendToBlender([cell.soma, cell.secden[0], cell.secden[1], cell.secden[2], cell.secden[3]])

        # from exportHelper import recordSegments as recordSegments
        # self.vectors = recordSegments([cell.soma, cell.secden[0], cell.secden[1], cell.secden[2], cell.secden[3]])

        return cell

class NeuroML(NeuroMLCellTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/MitralCells/Exported/Mitral_0_1.cell.nml"
        self.label = "mitral2"
        self.resultsFile = "results/cells/mitral2/NeuroML.json"
        self.id = "Mitral_0_1"
        self.currentRange = (-1, 3)

    def prepare(self, h):
        # Load the cell hoc
        h.load_file(self.id+".hoc")

        cell = getattr(h,self.id)()

        h.celsius = 24

        return cell



