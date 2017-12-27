import sys; sys.path.insert(0,'..')
from tests.channels.NeuroMLChannelTest import NeuroMLChannelTest

class NeuroML(NeuroMLChannelTest):

    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Channels/nax.channel.nml"
        self.label = "nax"
        self.resultsFile = "results_NeuroML.json"

    def prepare(self, model):
        model.gmax = 0.010

