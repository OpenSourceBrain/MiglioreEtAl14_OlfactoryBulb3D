# Launch this with "python customsim.py 2 10"
# to get a network with 2 Mitral cells and 10 Granule cells/Mitral (20 total)

def setup(mitralArg, granArg, run = False, enableOdorInput = False):
    import sys
    import custom_params
    custom_params.filename = 'fig7'

    custom_params.customMitralCount = mitralArg
    custom_params.customGranulesPerMitralCount = granArg
    custom_params.enableOdorInput = enableOdorInput

    import params
    import runsim
    runsim.build_complete_model('c10.dic')

    if run:
        runsim.run()

if __name__ == '__main__':
    
    import sys

    offset = 0
    if len(sys.argv) >= 2 and sys.argv[1] == "-python":
        offset = 2

    if len(sys.argv) > 1:
        mitralArg = int(sys.argv[1+offset])
        granArg = int(sys.argv[2+offset])

    setup(mitralArg, granArg)
    
