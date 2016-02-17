# This script creates graphs of granule cell voltages at various points vs various current stimulation values
# Also includes a closeup of one of the action potentials
# Run it with the following commmand: "nrniv -python granuleTest.py"

import os
import sys
from neuron import *
import time
import csv

# NEURON setup code
h.load_file('granule.hoc')
import custom_params
custom_params.filename = 'fig7'
from net_mitral_centric import mkgranule
import granules
gcid = 86086 # 86086 is the GID of first Gran cell of the first Mitral Cell of the full model

amps = [0.025, 0.05, 0.075, 0.1] # Current stimulation values in nA
delay = 40 # ms
duration = 100 # ms
tstop = 2*delay+duration
h.dt = 0.01 # ms
vinit = -65 # mV

cells = []
stims = []
graphs = []
closeup = h.Graph(0)
data = []

def main():
    
    # For each current value, create a cell
    for c in xrange(0,len(amps)):
        
        cells.append(mkgranule(gcid))

        g=h.Graph(0)
        g.size(0,tstop,-80,50)
        g.view(0,-80,tstop,130, (c % 2)*425,(c / 2)*260,400,200) # Position the graphs on screen
        addVars(g, c)
        graphs.append(g)
        
        stim = h.IClamp(0.5, sec = cells[c].soma)
        stim.delay = delay
        stim.amp = amps[c]
        stim.dur = duration
        stims.append(stim)
    
        data.append([])

    # For one of the current values, create a closeup of the AP
    focusampindex = 1
    closedupStartTime = 120 # ms
    closedupEndTime = 150   # ms
    closeup.size(closedupStartTime,closedupEndTime,-80,50)
    closeup.view(closedupStartTime,-80,closedupEndTime-closedupStartTime,130, 850,0,400,200)
    addVars(closeup, focusampindex)

    initialize()
    integrate() # Plot the graphs

def addVars(graph, ampIndex):
    graph.addvar('soma ('       + str(amps[ampIndex]) + 'nA)', 'v(0.5)',1,0, sec = cells[ampIndex].soma)
    graph.addvar('priden2 ('    + str(amps[ampIndex]) + 'nA)', 'v(0.5)',2,0, sec = cells[ampIndex].priden2[0])
    graph.addvar('priden ('     + str(amps[ampIndex]) + 'nA)', 'v(0.5)',3,0, sec = cells[ampIndex].priden)

def initialize():
    h.finitialize(vinit)
    h.fcurrent()

def integrate():
    
    for c in xrange(0,len(amps)):
        graphs[c].begin()
    
    while h.t< tstop:
        
        for c in xrange(0,len(amps)):
            graphs[c].plot(h.t)
            graphs[c].fastflush()
        
            data[c].append([h.t, cells[c].soma.v, cells[c].priden2[0].v, cells[c].priden.v])
        
        closeup.plot(h.t)
        closeup.fastflush()

        h.fadvance()

    for c in xrange(0,len(amps)):
        graphs[c].flush()


        with open('granuleTest_%snA.dat'%amps[c], 'w') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            for row in data[c]:
                writer.writerow(row)

main()

if raw_input("Press ENTER to quit(), or SPACE + ENTER to continue") != " ":
    quit()
