from tests.ModelTest import ModelTest
import numpy as np

class NEURONTest(ModelTest):
    def subSampleVector(self, nrnVector, everyNth):
        result = np.array(nrnVector.to_python())
        result = result[0:len(result) - 1:int(everyNth)].tolist()
        return result