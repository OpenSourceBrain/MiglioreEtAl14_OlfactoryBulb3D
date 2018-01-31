#import pydevd
#pydevd.settrace('192.168.177.1', port=4200, stdoutToServer=True, stderrToServer=True, suspend=False)

def export(MCs = 2):
    print("Exporting odor input for " + MCs + " MCs...")

    # Build the network
    import os, sys
    sys.path.append(os.path.abspath("../../NEURON"))
    os.chdir("../../NEURON")
    from neuron import h, gui
    import customsim
    import modeldata
    customsim.setup(MCs, 0)
    model = modeldata.getmodel()

    # Initialize default odor input sequence
    from odorstim import OdorSequence
    import custom_params
    import params
    odseq = OdorSequence(params.odor_sequence)
    odstim = odseq[0]
    next_time = odstim.init_ev(params.odor_sequence[0][1])

    # Simulate h.run() to obtain NetCon events
    sectionTimes = {}
    loop = True
    while(loop):
        h.t = next_time
        event = odstim.ev(next_time)

        for sec in event["weights"]:
            secName = sec["label"]

            if secName not in sectionTimes:
                sectionTimes[secName] = { 'times': [], 'weights': [] }

            sectionTimes[secName]['times'].append(event['time'])
            sectionTimes[secName]['weights'].append(sec['weight'])

        loop = 'next_time' in event

        if loop:
            next_time = event['next_time']

    import json, sys, os

    fileName = "odor-events.json"
    with open(fileName, "w") as file:
        json.dump(sectionTimes, file, indent=4)

    print("Odor stim times written to " + os.path.abspath(fileName))

if __name__ == '__main__':
    export()

