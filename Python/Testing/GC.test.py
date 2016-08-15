# This script shows the output of an GC in a network with disconnected MCs and GCs
# Useful to evaluate isolated GC properties
# From this folder, run it with the following command:
# cd ../../neuron && nrniv -python ../Python/Testing/GC.test.py; cd ../Python/Testing

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
custom_params.makeSynConns = False

import params
import runsim

from common import *
import params
import util
import parrun
import weightsave
import net_mitral_centric as nmc
makeSynConns = False # disconnect MCs and GCs

nmc.build_net_round_robin(getmodel(), 'c10.dic')

model = getmodel()

h.tstop = 300
h.dt = 1/64.0

#GIDs
mc = 0
gc = 110821
syn = 703836162

clampG = h.IClamp(model.granules[gc].soma(0.5))
clampG.delay = 50
clampG.dur = 200
clampG.amp = 0.05

g2=h.Graph()
h.graphList[0].append(g2)
g2.size(0,h.tstop,-80,50)
g2.addvar('gran soma',       'v(0.5)',2,0, sec = model.granules[gc].soma)
g2.addvar('gran spine head', 'v(0.5)',5,0, sec = model.mgrss[syn].spine.head)


h.nrnmainmenu()
h.run()
