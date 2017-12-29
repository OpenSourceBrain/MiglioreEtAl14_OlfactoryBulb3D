# This script shows the output of a network of 1 MC and 1 GC connected by the FI synapse only
# Useful to evaluate FI synapse properties
# From this folder, run it with the following command:
# cd ../../neuron && nrniv -python ../Python/Testing/FI.test.py; cd ../Python/Testing

import sys
import os

#os.chdir("../../NEURON")
from neuron import h
os.chdir("../NeuroML2")

h.chdir('../NEURON')
sys.path.append('../NEURON')

import custom_params
custom_params.filename = 'fig7'

custom_params.customMitralCount = 1
custom_params.customGranulesPerMitralCount = 1
custom_params.makeSynConns = True
custom_params.enableAmpaNmdasyn = False
custom_params.enableFIsyn = True

from math import *
import params
import runsim

from common import *
import params
import util
import parrun
import weightsave
import net_mitral_centric as nmc

nmc.build_net_round_robin(getmodel(), 'c10.dic')

model = getmodel()

#GIDs
mc = 0
gc = 110821
syn = 703836162

#clampM = h.IClamp(model.mitrals[mc].soma(0.5))
#clampM.delay = 50
#clampM.dur = 200
#clampM.amp = 0.0

spikes = 4
spikeInterval = 20 # <33.33 for LTP, 33.33 < LTD < 250
trainDur = spikeInterval * spikes

clamps = []
for i in range(0,spikes):
    clampG = h.IClamp(model.granules[gc].soma(0.5))
    clampG.delay = 50 + i * spikeInterval
    clampG.dur = 1
    clampG.amp = 10
    clamps.append(clampG)

h.t = 0
h.tstop = trainDur + 2*50
h.dt = 1/64.0

g=h.Graph()
h.graphList[0].append(g)
g.size(0,h.tstop,-80,50)
g.addvar('GC spine head v', 'v(0.5)',5,0, sec = model.mgrss[syn].spine.head)
g.addvar('GC soma v',       'v(0.5)',1,0, sec = model.granules[gc].soma)

g2=h.Graph()
h.graphList[0].append(g2)
g2.size(0,h.tstop,0,0.00074)
g2.addvar('mitral FI i',   model.mgrss[syn].fi._ref_i,2,0)

g3=h.Graph()
h.graphList[0].append(g3)
g3.size(0,h.tstop,-67.3,-67.1)
g3.addvar('mitral v',   'v('+str(model.mgrss[syn].xm)+')',2,0, sec = model.mgrss[syn].msecden)



h.nrnmainmenu()
h.run()
