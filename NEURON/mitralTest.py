# This script creates graphs of mitral cell voltages at various points vs various current stimulation values
# Also includes a closeup of one of the action potentials
# Run it with the following commmand: "nrniv -python mitralTest.py"

import os
from neuron import *
from mkmitral import *
import time


amps = [0.1, 1.0, 2, 5] # Current stimulation values in pA
delay = 40 # ms
duration = 100 # ms
tstop = 2*delay+duration
h.dt = 0.05 # ms
vinit = -65 # mV

cells = []
stims = []
graphs = []
closeup = h.Graph(0)

def main():
    
    # For each current value, create a cell
    for c in xrange(0,len(amps)):
        
        cells.append(mkmitral(0))

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

    # For one of the current values, create a closeup of the AP
    focusampindex = 1
    closedupStartTime = 90 # ms
    closedupEndTime = 95   # ms
    closeup.size(closedupStartTime,closedupEndTime,-80,50)
    closeup.view(closedupStartTime,-80,closedupEndTime-closedupStartTime,130, 850,0,400,200)
    addVars(closeup, focusampindex)

    initialize()
    integrate() # Plot the graphs

def addVars(graph, ampIndex):
    graph.addvar('soma ('       + str(amps[ampIndex]) + 'nA)', 'v(0.5)',1,0, sec = cells[ampIndex].soma)
    graph.addvar('initialseg (' + str(amps[ampIndex]) + 'nA)', 'v(0.5)',2,0, sec = cells[ampIndex].initialseg)
    graph.addvar('priden ('     + str(amps[ampIndex]) + 'nA)', 'v(0.5)',3,0, sec = cells[ampIndex].priden)

def initialize():
    h.finitialize(vinit)
    h.fcurrent()

def integrate():
    
    for c in xrange(0,len(amps)):
        graphs[c].begin()
    
    while h.t< tstop:
        h.fadvance()
        
        for c in xrange(0,len(amps)):
            graphs[c].plot(h.t)
            graphs[c].fastflush()

        closeup.plot(h.t)
        closeup.fastflush()

    for c in xrange(0,len(amps)):
        graphs[c].flush()

main()

if raw_input("Press ENTER to quit(), or SPACE + ENTER to continue") != " ":
    quit()
