import json
from matplotlib import pyplot as plt
import numpy as np
from tests.ModelTest import ModelTest
import sys, os; sys.path.append(os.path.abspath(os.getcwd()+"/../Python/Export"));

class NEURONTest(ModelTest):

    def subSampleVector(self, nrnVector, everyNth):
        result = np.array(nrnVector.to_python())
        result = result[0:len(result) - 1:int(everyNth)].tolist()
        return result

    def subSampleTVI(self, stepsPerMs):
        t = self.subSampleVector(self.tVector, stepsPerMs)
        v = self.subSampleVector(self.vVector, stepsPerMs)
        i = self.subSampleVector(self.iVector, stepsPerMs)

        return t, v, i

    def setupRecorders(self, t, v, i):
        self.tVector = self.h.Vector()
        self.tVector.record(t)

        self.vVector = self.h.Vector()
        self.vVector.record(v)

        self.iVector = self.h.Vector()
        self.iVector.record(i)

    def saveResults(self, result):
        self.resultsFilePath = self.startPath + "/" + self.resultsFile
        with open(self.resultsFilePath, "w") as file:
            json.dump(result, file, indent=4)

    def compareTraces(self, target, resultKey, variable):
        traces1 = self.loadResults()[resultKey]
        traces2 = target.loadResults()[resultKey]

        assert len(traces1) == len(traces2)

        traceErrors = []
        plt.figure(figsize=(20, 10))

        for t in range(len(traces1)):
            i1 = np.array(traces1[t][variable])
            i2 = np.array(traces2[t][variable])
            rangeExpected = np.max(i1) - np.min(i1)
            error = np.abs((i2 - i1))/rangeExpected*100.0  # Point-by-point absolute error as percentage of expected value range
            error[np.isnan(error)] = 100.0 # Treat NaNs as 100% error
            errorMean = np.mean(error)

            plt.subplot(len(traces1), 2, 2 * t + 1)
            plt.plot(traces1[t]['time'], i1, label="NEURON " + traces1[t]["label"])
            plt.plot(traces2[t]['time'], i2, label="NeuroML " + traces2[t]["label"])

            if (t != len(traces1) - 1):
                plt.gca().axes.get_xaxis().set_visible(False)

            plt.legend()

            plt.subplot(len(traces1), 2, 2 * t + 2)
            plt.plot(traces1[t]['time'], error, label="|Error| (mean: " + str(errorMean) + "%)")

            if (t != len(traces1) - 1):
                plt.gca().axes.get_xaxis().set_visible(False)

            plt.legend()

            traceErrors.append(errorMean)

        self.comparisonMean = np.mean(traceErrors)

        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, hspace=0.05)
        plt.suptitle(self.label + " Conversion Error: " + str(self.comparisonMean) + "%")

        # plt.show()
        plt.savefig(self.comparisonPath())

        return self.comparisonMean

    def loadNEURONandModFiles(self):
        from neuron import h, gui
        self.h = h
