import sys; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.cells.NEURONCellTest  import NEURONCellTest
from tests.cells.NeuroMLCellTest import NeuroMLCellTest

class NEURON(NEURONCellTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/granule.hoc"
        self.label = "granule"
        self.resultsFile = "results/cells/granule/NEURON.json"
        self.currentRange = (-0.1, 0.2)

    def prepare(self, h):
        # NEURON setup code
        h.load_file('granule.hoc')
        import custom_params
        custom_params.filename = 'fig7'
        from net_mitral_centric import mkgranule
        import granules
        gcid = 86086  # 86086 is the GID of first Gran cell of the first Mitral Cell of the full model

        cell = mkgranule(gcid)

        h.celsius = 24

        return cell

class NeuroML(NeuroMLCellTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/GranuleCells/Exported/Granule_0_86086.cell.nml"
        self.label = "granule"
        self.resultsFile = "results/cells/granule/NeuroML.json"
        self.id = "Granule_0_86086"
        self.currentRange = (-0.1, 0.2)

        # ToDO: make granules work
        #import changes from my repo under downloads
        #build network tests

    def prepare(self, h):
        # Load the cell hoc
        h.load_file(self.id+".hoc")

        cell = getattr(h,self.id)()

        h.celsius = 24

        return cell



